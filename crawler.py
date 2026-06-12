#!/usr/bin/env python3
"""
RECONPRO Custom Web Crawler - Deep Async Crawler
Finds hidden endpoints, JS APIs, comments, sitemaps, parameters
Better than gospider/hakrawler for bug bounty recon
"""

import asyncio
import aiohttp
import re
import json
import sys
import os
import time
import hashlib
from urllib.parse import urljoin, urlparse, parse_qs, unquote
from pathlib import Path

if sys.platform == "win32":
    os.system("chcp 65001 >nul 2>&1")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except:
        pass

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
]

BLOCKED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".bmp", ".tiff",
    ".css", ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".mp3", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm",
    ".zip", ".tar", ".gz", ".rar", ".7z",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".exe", ".dll", ".so", ".dylib",
}

INTERESTING_KEYWORDS = [
    ".env", ".git", "admin", "login", "config", "backup", "debug",
    "phpinfo", "info.php", "test", "console", ".sql", ".bak",
    "upload", "trace", "actuator", "swagger", "graphql",
    ".htaccess", "web.config", "error", "log", "dump",
    "api", "token", "secret", "key", "password", "auth",
    "internal", "private", "hidden", "staging", "dev",
    "robots.txt", "sitemap.xml", "crossdomain.xml",
    "wp-admin", "wp-config", "xmlrpc", "wp-login",
    "phpmyadmin", "adminer", "pma", "db", "database",
    "shell", "cmd", "exec", "eval", "assert",
    "backup.sql", "dump.sql", "db.sql", "database.sql",
    ".DS_Store", "Thumbs.db", "web.config", "crossdomain.xml",
    ".well-known", "security.txt", "humans.txt",
]


class DeepCrawler:
    def __init__(self, max_depth=3, max_pages=200, concurrency=30, timeout=10):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.concurrency = concurrency
        self.timeout = timeout
        self.visited = set()
        self.found_urls = set()
        self.found_params = set()
        self.found_endpoints = set()
        self.js_files = set()
        self.forms = []
        self.comments = []
        self.interesting = []
        self.api_endpoints = set()
        self._lock = asyncio.Lock()
        self._semaphore = None
        self._session = None
        self._pages_crawled = 0
        self._start_time = 0

    def _ua(self):
        return USER_AGENTS[hash(str(time.time())) % len(USER_AGENTS)]

    def _headers(self):
        return {
            "User-Agent": self._ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def _normalize(self, url, base):
        url = url.strip()
        if not url or url.startswith(("#", "javascript:", "mailto:", "tel:", "data:")):
            return None
        url = urljoin(base, url)
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return None
        ext = Path(parsed.path).suffix.lower()
        if ext in BLOCKED_EXTENSIONS:
            return None
        url = parsed._replace(fragment="").geturl()
        return url.rstrip("/")

    def _is_same_domain(self, url, target_domain):
        host = urlparse(url).hostname or ""
        return host == target_domain or host.endswith("." + target_domain)

    def _is_interesting(self, url):
        low = url.lower()
        return any(kw in low for kw in INTERESTING_KEYWORDS)

    async def _fetch(self, url):
        try:
            async with self._semaphore:
                async with self._session.get(
                    url,
                    headers=self._headers(),
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    allow_redirects=True,
                    ssl=False,
                ) as resp:
                    if resp.status >= 400:
                        return None, None
                    ct = resp.headers.get("Content-Type", "")
                    if "text" not in ct and "javascript" not in ct and "json" not in ct and "xml" not in ct:
                        return None, None
                    try:
                        body = await resp.text(errors="replace")
                    except:
                        return None, None
                    return body, str(resp.url)
        except:
            return None, None

    def _extract_links(self, html, base_url):
        urls = set()

        for match in re.finditer(r'href=["\']([^"\']+)["\']', html):
            norm = self._normalize(match.group(1), base_url)
            if norm:
                urls.add(norm)

        for match in re.finditer(r'src=["\']([^"\']+)["\']', html):
            norm = self._normalize(match.group(1), base_url)
            if norm:
                urls.add(norm)

        for match in re.finditer(r'action=["\']([^"\']+)["\']', html):
            norm = self._normalize(match.group(1), base_url)
            if norm:
                urls.add(norm)

        for match in re.finditer(r'content=["\'][^"\']*url=([^"\']+)["\']', html):
            norm = self._normalize(match.group(1), base_url)
            if norm:
                urls.add(norm)

        for match in re.finditer(r'poster=["\']([^"\']+)["\']', html):
            norm = self._normalize(match.group(1), base_url)
            if norm:
                urls.add(norm)

        for match in re.finditer(r'(?:src|href|data-src|data-url)=["\']([^"\']*\.js(?:\?[^"\']*)?)["\']', html):
            norm = self._normalize(match.group(1), base_url)
            if norm:
                self.js_files.add(norm)

        return urls

    def _extract_from_js(self, js_content, base_url):
        urls = set()

        patterns = [
            r'["\']https?://[^"\']+["\']',
            r'["\']\/[a-zA-Z0-9_\/\-\.]+(?:\?[^"\']*)?["\']',
            r'["\'][a-zA-Z0-9_]+\/api\/[^"\']+["\']',
            r'fetch\s*\(\s*["\']([^"\']+)["\']',
            r'axios\.(?:get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
            r'\.open\s*\(\s*["\'](?:GET|POST|PUT|DELETE)["\']\s*,\s*["\']([^"\']+)["\']',
            r'url\s*:\s*["\']([^"\']+)["\']',
            r'endpoint\s*[=:]\s*["\']([^"\']+)["\']',
            r'baseURL\s*[=:]\s*["\']([^"\']+)["\']',
            r'["\']\/api\/v\d+\/[^"\']+["\']',
            r'["\']\/graphql["\']',
            r'["\']\/swagger[^"\']*["\']',
            r'["\']\/openapi[^"\']*["\']',
            r'window\.__[A-Z_]+\s*=\s*["\']([^"\']+)["\']',
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, js_content):
                raw = match.group(0).strip("'\"")
                if raw.startswith("http"):
                    norm = self._normalize(raw, base_url)
                    if norm:
                        urls.add(norm)
                elif raw.startswith("/"):
                    norm = self._normalize(raw, base_url)
                    if norm:
                        urls.add(norm)

        api_patterns = [
            r'["\']\/api(?:\/v\d+)?\/[a-zA-Z0-9_\/\-]+["\']',
            r'["\']\/graphql(?:\?[^"\']*)?["\']',
            r'["\']\/rest\/[^"\']+["\']',
            r'["\']\/_api\/[^"\']+["\']',
            r'["\']\/internal\/[^"\']+["\']',
            r'["\']\/admin\/api\/[^"\']+["\']',
        ]
        for pattern in api_patterns:
            for match in re.finditer(pattern, js_content):
                raw = match.group(0).strip("'\"")
                norm = self._normalize(raw, base_url)
                if norm:
                    self.api_endpoints.add(norm)
                    urls.add(norm)

        return urls

    def _extract_comments(self, html, url):
        html_comments = re.findall(r'<!--(.*?)-->', html, re.DOTALL)
        for c in html_comments:
            c = c.strip()
            if len(c) > 5:
                self.comments.append({"url": url, "comment": c[:500], "type": "html"})

        js_comments = re.findall(r'\/\*(.*?)\*\/', html, re.DOTALL)
        for c in js_comments:
            c = c.strip()
            if len(c) > 5:
                self.comments.append({"url": url, "comment": c[:500], "type": "js-block"})

        line_comments = re.findall(r'\/\/([^\n]{10,})', html)
        for c in line_comments:
            c = c.strip()
            if any(kw in c.lower() for kw in ["todo", "fixme", "hack", "bug", "password", "key", "token", "secret", "api", "url", "endpoint"]):
                self.comments.append({"url": url, "comment": c[:500], "type": "js-line"})

    def _extract_forms(self, html, url):
        form_pattern = re.compile(r'<form[^>]*>(.*?)</form>', re.DOTALL | re.IGNORECASE)
        for form_match in form_pattern.finditer(html):
            form_html = form_match.group(0)
            action_match = re.search(r'action=["\']([^"\']*)["\']', form_html, re.IGNORECASE)
            method_match = re.search(r'method=["\']([^"\']*)["\']', form_html, re.IGNORECASE)
            action = action_match.group(1) if action_match else ""
            method = (method_match.group(1) if method_match else "GET").upper()
            inputs = re.findall(r'<input[^>]*name=["\']([^"\']+)["\']', form_html, re.IGNORECASE)
            selects = re.findall(r'<select[^>]*name=["\']([^"\']+)["\']', form_html, re.IGNORECASE)
            textareas = re.findall(r'<textarea[^>]*name=["\']([^"\']+)["\']', form_html, re.IGNORECASE)
            params = inputs + selects + textareas
            if params:
                full_action = self._normalize(action, url) if action else url
                self.forms.append({
                    "url": url,
                    "action": full_action,
                    "method": method,
                    "params": params,
                })
                if method == "POST":
                    for p in params:
                        self.found_params.add(p)

    def _extract_params(self, url):
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        for key in qs:
            self.found_params.add(key)

    def _extract_meta(self, html, url):
        for match in re.finditer(r'<meta[^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE):
            content = match.group(1)
            if content.startswith("http"):
                norm = self._normalize(content, url)
                if norm:
                    self.found_urls.add(norm)

        for match in re.finditer(r'property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE):
            norm = self._normalize(match.group(1), url)
            if norm:
                self.found_urls.add(norm)

        for match in re.finditer(r'<link[^>]+href=["\']([^"\']+)["\']', html, re.IGNORECASE):
            norm = self._normalize(match.group(1), url)
            if norm:
                self.found_urls.add(norm)

    async def _parse_robots(self, base_url):
        robots_url = urljoin(base_url, "/robots.txt")
        body, _ = await self._fetch(robots_url)
        if not body:
            return
        for line in body.splitlines():
            line = line.strip()
            if line.lower().startswith(("disallow:", "allow:")):
                path = line.split(":", 1)[1].strip()
                if path and path != "/":
                    norm = self._normalize(path, base_url)
                    if norm:
                        self.found_urls.add(norm)
            elif line.lower().startswith("sitemap:"):
                sitemap = line.split(":", 1)[1].strip()
                norm = self._normalize(sitemap, base_url)
                if norm:
                    self.found_urls.add(norm)

    async def _parse_sitemap(self, url):
        body, final_url = await self._fetch(url)
        if not body:
            return
        locs = re.findall(r'<loc>(.*?)</loc>', body, re.DOTALL)
        for loc in locs:
            loc = loc.strip()
            norm = self._normalize(loc, final_url or url)
            if norm:
                self.found_urls.add(norm)
        sitemaps = re.findall(r'<sitemap>.*?<loc>(.*?)</loc>', body, re.DOTALL)
        for sm in sitemaps[:5]:
            norm = self._normalize(sm.strip(), final_url or url)
            if norm:
                await self._parse_sitemap(norm)

    async def _crawl_page(self, url, depth, target_domain):
        if depth > self.max_depth:
            return
        if url in self.visited:
            return
        if self._pages_crawled >= self.max_pages:
            return

        async with self._lock:
            if url in self.visited:
                return
            self.visited.add(url)
            self._pages_crawled += 1

        body, final_url = await self._fetch(url)
        if not body:
            return

        self._extract_params(url)

        if self._is_interesting(url):
            self.interesting.append(url)

        self._extract_comments(body, url)
        self._extract_forms(body, url)
        self._extract_meta(body, url)

        new_urls = self._extract_links(body, url)

        js_urls = set(self.js_files)
        self.js_files.clear()
        for js_url in js_urls:
            if js_url not in self.visited:
                self.visited.add(js_url)
                js_body, _ = await self._fetch(js_url)
                if js_body:
                    js_found = self._extract_from_js(js_body, js_url)
                    new_urls.update(js_found)
                    self._extract_comments(js_body, js_url)

        tasks = []
        for u in new_urls:
            if u not in self.visited and self._is_same_domain(u, target_domain):
                self.found_urls.add(u)
                if depth + 1 <= self.max_depth and self._pages_crawled < self.max_pages:
                    tasks.append(self._crawl_page(u, depth + 1, target_domain))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def crawl(self, target_url, target_domain):
        self._start_time = time.time()
        self._semaphore = asyncio.Semaphore(self.concurrency)

        connector = aiohttp.TCPConnector(
            limit=self.concurrency,
            ttl_dns_cache=300,
            ssl=False,
            enable_cleanup_closed=True,
        )
        self._session = aiohttp.ClientSession(connector=connector)

        try:
            await self._parse_robots(f"https://{target_domain}")
            await self._parse_robots(f"http://{target_domain}")

            sitemap_urls = [
                f"https://{target_domain}/sitemap.xml",
                f"http://{target_domain}/sitemap.xml",
                f"https://{target_domain}/sitemap_index.xml",
                f"https://{target_domain}/sitemap-index.xml",
            ]
            for sm in sitemap_urls:
                await self._parse_sitemap(sm)

            await self._crawl_page(target_url, 0, target_domain)
        finally:
            await self._session.close()

        elapsed = time.time() - self._start_time
        return self._build_result(target_domain, elapsed)

    def _build_result(self, domain, elapsed):
        all_urls = sorted(self.found_urls)
        interesting = sorted(set(self.interesting))
        interesting.extend([u for u in all_urls if self._is_interesting(u)])
        interesting = sorted(set(interesting))

        api_eps = sorted(self.api_endpoints)

        return {
            "domain": domain,
            "total_urls": len(all_urls),
            "pages_crawled": self._pages_crawled,
            "urls": all_urls,
            "interesting": interesting,
            "api_endpoints": api_eps,
            "js_files": sorted(self.js_files) if self.js_files else [],
            "forms": self.forms,
            "params": sorted(self.found_params),
            "comments": self.comments,
            "elapsed": elapsed,
        }


def print_result(result):
    r = result
    print(f"\n    {'─'*50}")
    print(f"    \033[1;96mCRAWL COMPLETE: {r['domain']}\033[0m")
    print(f"    {'─'*50}")
    print(f"    \033[90m│\033[0m  Pages crawled   \033[1;92m{r['pages_crawled']}\033[0m")
    print(f"    \033[90m│\033[0m  URLs found      \033[1;92m{r['total_urls']}\033[0m")
    print(f"    \033[90m│\033[0m  Interesting     \033[1;91m{len(r['interesting'])}\033[0m")
    print(f"    \033[90m│\033[0m  API endpoints   \033[1;93m{len(r['api_endpoints'])}\033[0m")
    print(f"    \033[90m│\033[0m  JS files        \033[1;95m{len(r['js_files'])}\033[0m")
    print(f"    \033[90m│\033[0m  Forms           \033[1;96m{len(r['forms'])}\033[0m")
    print(f"    \033[90m│\033[0m  Parameters      \033[1;93m{len(r['params'])}\033[0m")
    print(f"    \033[90m│\033[0m  Comments        \033[1;95m{len(r['comments'])}\033[0m")
    print(f"    \033[90m│\033[0m  Time            \033[1;93m{r['elapsed']:.1f}s\033[0m")
    print(f"    {'─'*50}")

    if r["interesting"]:
        print(f"\n    \033[1;91m Interesting URLs:\033[0m")
        for u in r["interesting"][:30]:
            print(f"    \033[90m├─▸\033[0m \033[91m{u}\033[0m")
        if len(r["interesting"]) > 30:
            print(f"    \033[90m├─▸\033[0m \033[90m... and {len(r['interesting'])-30} more\033[0m")

    if r["api_endpoints"]:
        print(f"\n    \033[1;93m API Endpoints:\033[0m")
        for u in r["api_endpoints"][:20]:
            print(f"    \033[90m├─▸\033[0m \033[93m{u}\033[0m")

    if r["params"]:
        print(f"\n    \033[1;96m Parameters Found:\033[0m")
        for p in r["params"][:30]:
            print(f"    \033[90m├─▸\033[0m \033[96m{p}\033[0m")

    if r["forms"]:
        print(f"\n    \033[1;95m Forms:\033[0m")
        for f in r["forms"][:10]:
            print(f"    \033[90m├─▸\033[0m \033[95m{f['method']} {f['action']} ({', '.join(f['params'][:5])})\033[0m")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python crawler.py <target_url>")
        sys.exit(1)

    target = sys.argv[1]
    if not target.startswith("http"):
        target = f"https://{target}"
    parsed = urlparse(target)
    domain = parsed.hostname

    crawler = DeepCrawler(max_depth=3, max_pages=200, concurrency=30, timeout=10)
    result = asyncio.run(crawler.crawl(target, domain))
    print_result(result)
