#!/usr/bin/env python3
"""
RECONPRO v3.1 - Red Team Recon Pipeline
Advanced Attack Surface Mapping & Reconnaissance
"""

import subprocess
import os
import sys
import json
import re
import time
import random
import shutil
import urllib.request
import urllib.parse
import socket
import asyncio
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    os.system("chcp 65001 >nul 2>&1")
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

GO_BIN = os.path.join(os.path.expanduser("~"), "go", "bin")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ["PATH"] = GO_BIN + os.pathsep + SCRIPT_DIR + os.pathsep + os.environ.get("PATH", "")


class C:
    if sys.platform == "win32":
        os.system("")
    R = "\033[91m"
    G = "\033[92m"
    Y = "\033[93m"
    B = "\033[94m"
    M = "\033[95m"
    C = "\033[96m"
    W = "\033[97m"
    D = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    BR = "\033[1;91m"
    BG = "\033[1;92m"
    BY = "\033[1;93m"
    BB = "\033[1;94m"
    BM = "\033[1;95m"
    BC = "\033[1;96m"


SPIN_CHARS = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
BLOCK = "█"
HALF = "▀"
LINE = "═"

_stop_spinner = False
_spinner_thread = None


def spinner(msg, color=C.C):
    global _stop_spinner
    _stop_spinner = False
    i = 0
    while not _stop_spinner:
        sys.stdout.write(f"\r    {color}{SPIN_CHARS[i % len(SPIN_CHARS)]} {msg}{C.D}   ")
        sys.stdout.flush()
        i += 1
        time.sleep(0.08)
    sys.stdout.write(f"\r    {C.D}{' ' * (len(msg) + 10)}\r")
    sys.stdout.flush()


def start_spinner(msg, color=C.C):
    import threading
    global _stop_spinner, _spinner_thread
    _stop_spinner = False
    _spinner_thread = threading.Thread(target=spinner, args=(msg, color), daemon=True)
    _spinner_thread.start()


def stop_spinner():
    global _stop_spinner
    _stop_spinner = True
    time.sleep(0.15)


def typing_print(text, color=C.C, delay=0.02):
    sys.stdout.write(color + C.BOLD)
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(C.D + "\n")
    sys.stdout.flush()


def progress_bar(current, total, prefix="", width=40):
    pct = current / total if total else 0
    filled = int(width * pct)
    bar = BLOCK * filled + "░" * (width - filled)
    sys.stdout.write(f"\r    {C.C}{prefix} {C.BG}{bar}{C.D} {C.Y}{pct*100:.0f}%{C.D}  ")
    sys.stdout.flush()


def banner():
    b = f"""{C.BOLD}{C.BC}
    {LINE*72}
    
    
      ▄█████ ██  ██ █████▄ ██████ █████▄  ▄█████ ▄█████ ▄████▄ ██  ██ ██████ 
      ██      ▀██▀  ██▄▄██ ██▄▄   ██▄▄██▄ ▀▀▀▄▄▄ ██     ██  ██ ██  ██   ██   
      ▀█████   ██   ██▄▄█▀ ██▄▄▄▄ ██   ██ █████▀ ▀█████ ▀████▀ ▀████▀   ██   

                                                                       
    
    {C.BG}  Red Team Recon Pipeline v3.1{C.D}
    {C.BY}  Advanced Attack Surface Mapping{C.D}
    {C.DIM}  25+ Free Subdomain Sources | Custom Deep Crawler | Cross-Platform{C.D}
    
    {LINE*72}{C.D}"""
    print(b)


def phase_header(phase, title):
    total = 8
    dots = " ".join([f"{C.BG}●{C.D}" if i < phase else f"{C.DIM}○{C.D}" for i in range(total)])
    print(f"\n{C.BOLD}{C.M}{LINE*72}")
    print(f"  {dots}  {C.BC}PHASE {phase}/{total}:{C.D} {C.BOLD}{title}")
    print(f"{LINE*72}{C.D}\n")


def info(msg):
    print(f"    {C.C}▸{C.D} {msg}")


def ok(msg):
    print(f"    {C.BG}✔{C.D} {C.G}{msg}{C.D}")


def warn(msg):
    print(f"    {C.Y}!{C.D} {C.Y}{msg}{C.D}")


def fail(msg):
    print(f"    {C.R}✘{C.D} {C.R}{msg}{C.D}")


def stat(label, value, color=C.BC):
    print(f"    {C.DIM}├─{C.D} {color}{label}:{C.D} {C.BOLD}{value}{C.D}")


def check_tool(name):
    go_path = os.path.join(GO_BIN, name + (".exe" if sys.platform == "win32" else ""))
    if os.path.exists(go_path):
        return go_path
    return shutil.which(name)


def run_cmd(cmd, timeout=120, silent=False):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                           timeout=timeout, encoding='utf-8', errors='replace')
        return r.stdout.strip()
    except:
        return ""


def save(results_dir, filename, content):
    path = results_dir / filename
    path.write_text(content, encoding="utf-8")
    return path


def timer_str(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m}m {s}s"
    elif m:
        return f"{m}m {s}s"
    return f"{s}s"


# ─────────────────────────────────────────────
# PHASE 1: Subdomain Enumeration (15+ Sources)
# ─────────────────────────────────────────────
def phase1_subdomains(domain, results_dir):
    phase_header(1, "SUBDOMAIN ENUMERATION")
    all_subs = set()
    sources_ok = 0
    sources_total = 25

    def add_sub(sub):
        sub = sub.strip().lower()
        if sub and "*" not in sub and (sub.endswith(f".{domain}") or sub == domain):
            all_subs.add(sub)

    # 1. subfinder
    info("subfinder (primary)")
    start_spinner("Running subfinder")
    outfile = results_dir / "subfinder.txt"
    run_cmd(f'subfinder -d {domain} -o "{outfile}" -silent -timeout 60 -all', timeout=300, silent=True)
    stop_spinner()
    if outfile.exists():
        for line in outfile.read_text().splitlines():
            add_sub(line)
        cnt = len([l for l in outfile.read_text().splitlines() if l.strip()])
        ok(f"subfinder: {cnt} subdomains")
        sources_ok += 1
    else:
        fail("subfinder: no results")

    # 2. crt.sh (API)
    info("crt.sh (certificate transparency)")
    for attempt in range(3):
        try:
            url = f"https://crt.sh/?q=%.{domain}&output=json"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
            count = 0
            for entry in data:
                for sub in entry.get("name_value", "").split("\n"):
                    if sub.strip().lower().endswith(domain):
                        add_sub(sub)
                        count += 1
            ok(f"crt.sh: {count} subdomains")
            sources_ok += 1
            break
        except:
            if attempt < 2:
                warn(f"crt.sh timeout, retrying ({attempt+2}/3)")
                time.sleep(5)
            else:
                fail("crt.sh: failed after 3 attempts")

    # 3. amass (passive)
    info("amass (passive mode)")
    start_spinner("Running amass")
    amass_out = results_dir / "amass.txt"
    run_cmd(f'amass enum -passive -d {domain} -o "{amass_out}"', timeout=300, silent=True)
    stop_spinner()
    if amass_out.exists():
        before = len(all_subs)
        for line in amass_out.read_text().splitlines():
            add_sub(line)
        ok(f"amass: {len(all_subs) - before} new subdomains")
        sources_ok += 1
    else:
        fail("amass: no results")

    # 4. crt.sh via curl (fallback)
    info("crt.sh (curl fallback)")
    try:
        curl_out = results_dir / "crtsh_curl.json"
        run_cmd(f'curl -s "https://crt.sh/?q=%.{domain}&output=json" -o "{curl_out}" --connect-timeout 30', timeout=45, silent=True)
        if curl_out.exists():
            before = len(all_subs)
            data = json.loads(curl_out.read_text())
            for entry in data:
                for sub in entry.get("name_value", "").split("\n"):
                    add_sub(sub)
            ok(f"crt.sh curl: {len(all_subs) - before} new")
            sources_ok += 1
    except:
        fail("crt.sh curl: failed")

    # 5. rapiddns
    info("rapiddns")
    try:
        url = f"https://rapiddns.io/subdomain/{domain}?full=1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        found = re.findall(r'<td>([a-zA-Z0-9._-]+\.' + re.escape(domain) + r')</td>', html)
        before = len(all_subs)
        for sub in found:
            add_sub(sub)
        ok(f"rapiddns: {len(all_subs) - before} new")
        sources_ok += 1
    except:
        fail("rapiddns: failed")

    # 6. hackertarget
    info("hackertarget")
    try:
        url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read().decode("utf-8", errors="replace")
        before = len(all_subs)
        for line in data.splitlines():
            if "," in line:
                add_sub(line.split(",")[0])
        ok(f"hackertarget: {len(all_subs) - before} new")
        sources_ok += 1
    except:
        fail("hackertarget: failed")

    # 7. AlienVault OTX
    info("AlienVault OTX")
    try:
        url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        before = len(all_subs)
        for record in data.get("passive_dns", []):
            add_sub(record.get("hostname", ""))
        ok(f"alienvault: {len(all_subs) - before} new")
        sources_ok += 1
    except:
        fail("alienvault: failed")

    # 8. bufferover.run
    info("bufferover.run")
    try:
        url = f"https://tls.bufferover.run/dns?q=.{domain}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        before = len(all_subs)
        for record in data.get("Results", []):
            parts = record.split(",")
            if len(parts) >= 2:
                add_sub(parts[1])
        ok(f"bufferover: {len(all_subs) - before} new")
        sources_ok += 1
    except:
        fail("bufferover: failed")

    # 9. ThreatCrowd
    info("ThreatCrowd")
    try:
        url = f"https://www.threatcrowd.org/searchApi/v2/domain/report/?domain={domain}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        before = len(all_subs)
        for sub in data.get("subdomains", []):
            add_sub(sub)
        ok(f"threatcrowd: {len(all_subs) - before} new")
        sources_ok += 1
    except:
        fail("threatcrowd: failed")

    # 10. Anubis (jldc.me)
    info("Anubis")
    try:
        url = f"https://jldc.me/anubis/subdomains/{domain}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        before = len(all_subs)
        for sub in data:
            add_sub(sub)
        ok(f"anubis: {len(all_subs) - before} new")
        sources_ok += 1
    except:
        fail("anubis: failed")

    # 11. SubdomainCenter
    info("SubdomainCenter")
    try:
        url = f"https://api.subdomaincenter.com/subdomain/{domain}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        before = len(all_subs)
        for sub in data:
            if isinstance(sub, str):
                add_sub(sub)
        ok(f"subdomaincenter: {len(all_subs) - before} new")
        sources_ok += 1
    except:
        fail("subdomaincenter: failed")

    # 12. CertSpotter
    info("CertSpotter")
    try:
        url = f"https://api.certspotter.com/v1/issuances?domain={domain}&include_subdomains=true&expand=dns_names"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        before = len(all_subs)
        for cert in data:
            for name in cert.get("dns_names", []):
                add_sub(name)
        ok(f"certspotter: {len(all_subs) - before} new")
        sources_ok += 1
    except:
        fail("certspotter: failed")

    # 13. Wayback Machine
    info("Wayback Machine")
    try:
        url = f"https://web.archive.org/cdx/search/cdx?url=*.{domain}&output=json&fl=original&collapse=urlkey&limit=5000"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        before = len(all_subs)
        for row in data[1:]:
            parsed = urllib.parse.urlparse(row[0])
            host = parsed.hostname or ""
            add_sub(host)
        ok(f"wayback: {len(all_subs) - before} new")
        sources_ok += 1
    except:
        fail("wayback: failed")

    # 14. ThreatMiner
    info("ThreatMiner")
    try:
        url = f"https://api.threatminer.org/v2/domain.php?q={domain}&rt=1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        before = len(all_subs)
        for sub in data.get("results", []):
            add_sub(sub)
        ok(f"threatminer: {len(all_subs) - before} new")
        sources_ok += 1
    except:
        fail("threatminer: failed")

    # 15. DNS brute force
    info("DNS brute force")
    common = ["www", "mail", "ftp", "smtp", "pop", "imap", "ns1", "ns2", "ns3",
              "dns1", "dns2", "mx1", "mx2", "webmail", "email", "vpn", "remote",
              "admin", "portal", "api", "dev", "test", "staging", "beta", "alpha",
              "shop", "store", "pay", "checkout", "cdn", "static", "media",
              "img", "images", "assets", "files", "docs", "blog", "forum",
              "support", "help", "kb", "wiki", "status", "monitor", "grafana",
              "kibana", "jenkins", "gitlab", "github", "bitbucket", "jira",
              "hr", "crm", "erp", "sales", "marketing", "finance", "legal",
              "db", "database", "sql", "mongo", "redis", "es", "kafka", "mq",
              "proxy", "gateway", "edge", "node", "app", "web", "site", "old",
              "new", "v2", "v3", "internal", "private", "corp", "intranet"]
    brute_file = results_dir / "brute_input.txt"
    brute_file.write_text("\n".join([f"{s}.{domain}" for s in common]), encoding="utf-8")
    brute_out = results_dir / "brute_results.txt"
    run_cmd(f'dnsx -l "{brute_file}" -o "{brute_out}" -silent -a -retry 3', timeout=120, silent=True)
    if brute_out.exists():
        before = len(all_subs)
        for line in brute_out.read_text().splitlines():
            add_sub(line.split()[0] if line.strip() else "")
        ok(f"brute force: {len(all_subs) - before} found")
        sources_ok += 1

    # 16. ProjectDiscovery Chaos
    info("ProjectDiscovery Chaos")
    try:
        url = f"https://chaos.projectdiscovery.com/public?domain={domain}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        before = len(all_subs)
        for sub in data.get("subdomains", []):
            fqdn = sub.get("host", "")
            if not fqdn and isinstance(sub, str):
                fqdn = sub
            if fqdn:
                add_sub(fqdn)
        ok(f"chaos: {len(all_subs) - before} new")
        sources_ok += 1
    except:
        fail("chaos: failed")

    # 17. Shodan InternetDB (via subfinder output IPs)
    info("Shodan InternetDB")
    try:
        shodan_found = 0
        for sub in list(all_subs)[:50]:
            try:
                ip = socket.gethostbyname(sub)
                url = f"https://internetdb.shodan.io/{ip}"
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read())
                for host in data.get("hostnames", []):
                    if host.endswith(domain):
                        add_sub(host)
                        shodan_found += 1
            except:
                pass
        ok(f"shodan: {shodan_found} new")
        if shodan_found > 0:
            sources_ok += 1
    except:
        fail("shodan: failed")

    # 18. VirusTotal (needs API key)
    info("VirusTotal")
    try:
        url = f"https://www.virustotal.com/api/v3/domains/{domain}/subdomains?limit=40"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        before = len(all_subs)
        for item in data.get("data", []):
            add_sub(item.get("id", ""))
        ok(f"virustotal: {len(all_subs) - before} new")
        sources_ok += 1
    except urllib.error.HTTPError as e:
        if e.code == 401:
            warn("virustotal: needs API key (free at virustotal.com)")
        else:
            fail("virustotal: failed")
    except:
        fail("virustotal: failed")

    # 19. DNSDumpster
    info("DNSDumpster")
    try:
        import http.cookiejar
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        opener.addheaders = [("User-Agent", "Mozilla/5.0")]
        page = opener.open("https://dnsdumpster.com/", timeout=15)
        html = page.read().decode("utf-8", errors="replace")
        csrf_match = re.search(r'csrfmiddlewaretoken["\s]+value=["\']([^"\']+)', html)
        if csrf_match:
            token = csrf_match.group(1)
            data = urllib.parse.urlencode({"targetip": domain, "csrfmiddlewaretoken": token}).encode()
            req = urllib.request.Request("https://dnsdumpster.com/", data=data)
            req.add_header("Referer", "https://dnsdumpster.com/")
            req.add_header("User-Agent", "Mozilla/5.0")
            resp = opener.open(req, timeout=15)
            result_html = resp.read().decode("utf-8", errors="replace")
            before = len(all_subs)
            found = re.findall(r'([a-zA-Z0-9._-]+\.' + re.escape(domain) + r')', result_html)
            for sub in set(found):
                add_sub(sub)
            ok(f"dnsdumpster: {len(all_subs) - before} new")
            sources_ok += 1
        else:
            fail("dnsdumpster: no CSRF token")
    except:
        fail("dnsdumpster: failed")

    # 20. Riddler.io
    info("Riddler.io")
    try:
        url = f"https://riddler.io-api/search?q={domain}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        before = len(all_subs)
        for item in data:
            if isinstance(item, dict):
                add_sub(item.get("hostname", ""))
            elif isinstance(item, str):
                add_sub(item)
        ok(f"riddler: {len(all_subs) - before} new")
        sources_ok += 1
    except:
        fail("riddler: failed")

    # 21. FindSubdomains
    info("FindSubdomains")
    try:
        url = f"https://findsubdomains.com/subdomains-of/{domain}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        before = len(all_subs)
        found = re.findall(r'(?:https?://|">)([a-zA-Z0-9._-]+\.' + re.escape(domain) + r')', html)
        for sub in set(found):
            if not sub.startswith("http"):
                add_sub(sub)
        ok(f"findsubdomains: {len(all_subs) - before} new")
        sources_ok += 1
    except:
        fail("findsubdomains: failed")

    # 22. crt.sh email reverse
    info("crt.sh (email reverse)")
    try:
        url = f"https://crt.sh/?q=%25%25.{domain}&output=json"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read())
        before = len(all_subs)
        for entry in data:
            for sub in entry.get("name_value", "").split("\n"):
                add_sub(sub)
            email = entry.get("issuer_name", "")
            email_match = re.search(r'CN=([^@]+@[^@]+)', email)
            if email_match:
                email_domain = email_match.group(1).split("@")[-1]
                if email_domain.endswith(domain):
                    add_sub(email_domain)
        ok(f"crt.sh email: {len(all_subs) - before} new")
        sources_ok += 1
    except:
        fail("crt.sh email: failed")

    # 23. PassiveTotal (needs API key)
    info("PassiveTotal")
    try:
        url = f"https://api.passivetotal.org/v2/enrichment/subdomain?query={domain}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        before = len(all_subs)
        for sub in data.get("subdomains", []):
            add_sub(f"{sub}.{domain}")
        ok(f"passivetotal: {len(all_subs) - before} new")
        sources_ok += 1
    except urllib.error.HTTPError as e:
        if e.code == 401:
            warn("passivetotal: needs API key (free at riskiq.com)")
        else:
            fail("passivetotal: failed")
    except:
        fail("passivetotal: failed")

    # 24. WhoisXML (needs API key)
    info("WhoisXML")
    try:
        url = f"https://subdomain.whoisxmlapi.com/?apiKey=at_demo&domainName={domain}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        before = len(all_subs)
        for record in data.get("records", []):
            add_sub(record.get("subdomain", ""))
        ok(f"whoisxml: {len(all_subs) - before} new")
        sources_ok += 1
    except urllib.error.HTTPError as e:
        if e.code == 403:
            warn("whoisxml: needs API key (free at whoisxmlapi.com)")
        else:
            fail("whoisxml: failed")
    except:
        fail("whoisxml: failed")

    # 25. SecurityTrails (needs API key)
    info("SecurityTrails")
    try:
        url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        before = len(all_subs)
        for sub_record in data.get("subdomains", []):
            sub = sub_record.get("subdomain", "")
            if sub:
                add_sub(f"{sub}.{domain}")
        ok(f"securitytrails: {len(all_subs) - before} new")
        sources_ok += 1
    except urllib.error.HTTPError as e:
        if e.code == 403:
            warn("securitytrails: needs API key (free at securitytrails.com)")
        else:
            fail("securitytrails: failed")
    except:
        fail("securitytrails: failed")

    sorted_subs = sorted(all_subs)[:3000]
    save(results_dir, "all_subdomains.txt", "\n".join(sorted_subs))

    print(f"\n    {C.DIM}{'─'*50}{C.D}")
    stat("Sources", f"{sources_ok}/{sources_total} responded")
    stat("Total subdomains", f"{C.BG}{len(all_subs)}{C.D}")
    if len(all_subs) > 3000:
        warn(f"Capped to 3,000 for performance (found {len(all_subs)})")
    stat("Selected for scan", f"{C.BG}{len(sorted_subs)}{C.D}")
    print(f"    {C.DIM}{'─'*50}{C.D}")

    for s in sorted_subs[:30]:
        info(s)
    if len(sorted_subs) > 30:
        info(f"{C.DIM}... and {len(sorted_subs)-30} more{C.D}")

    return sorted_subs


# ─────────────────────────────────────────────
# PHASE 2: DNS Resolution + Hidden IP Ranges
# ─────────────────────────────────────────────
def phase2_dns(domain, subdomains, results_dir):
    phase_header(2, "DNS RESOLUTION & IP ANALYSIS")

    if not subdomains:
        return []

    subs_to_resolve = subdomains[:3000]
    info(f"Resolving {len(subs_to_resolve)} subdomains (limited from {len(subdomains)})")

    infile = results_dir / "dns_input.txt"
    infile.write_text("\n".join(subs_to_resolve), encoding="utf-8")

    info("Resolving subdomains via dnsx")
    start_spinner("Resolving DNS records")
    outfile = results_dir / "dns_results.txt"
    run_cmd(f'dnsx -l "{infile}" -o "{outfile}" -silent -a -aaaa -retry 1 -t 50 -rl 500', timeout=120, silent=True)
    stop_spinner()

    ips = set()
    cname_map = {}
    mx_records = []
    txt_records = []

    if outfile.exists():
        for line in outfile.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            found_ips = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
            ips.update(found_ips)
            cname_match = re.search(r'CNAME\s+(.+?)(?:\s|$)', line)
            if cname_match:
                cname_map[line.split()[0]] = cname_match.group(1).rstrip('.')
            if re.search(r'MX\s+', line):
                mx_records.append(line)
            if re.search(r'TXT\s+', line):
                txt_records.append(line)

    # DNS brute force
    info("DNS brute force")
    common_subs = ["www", "mail", "ftp", "smtp", "ns1", "ns2", "webmail", "vpn",
                   "admin", "api", "dev", "test", "staging", "cdn", "shop", "blog"]
    brute_file = results_dir / "dns_brute.txt"
    brute_file.write_text("\n".join([f"{s}.{domain}" for s in common_subs]), encoding="utf-8")
    brute_out = results_dir / "dns_brute_results.txt"
    run_cmd(f'dnsx -l "{brute_file}" -o "{brute_out}" -silent -a -retry 3', timeout=120, silent=True)
    if brute_out.exists():
        for line in brute_out.read_text().splitlines():
            ips.update(re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line))

    # Analyze ranges
    info("Analyzing IP ranges")
    ip_ranges = {}
    cidr_ranges = set()
    for ip in ips:
        parts = ip.split(".")
        if len(parts) == 4:
            cidr = f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
            cidr_ranges.add(cidr)
            ip_ranges.setdefault(cidr, []).append(ip)

    hidden_ranges = {k: v for k, v in ip_ranges.items() if len(v) >= 3}

    stat("Resolved IPs", f"{C.BG}{len(ips)}{C.D}")
    for ip in sorted(ips)[:15]:
        info(ip)
    if len(ips) > 15:
        info(f"{C.DIM}... and {len(ips)-15} more{C.D}")

    stat("Hidden /24 ranges", f"{C.BY}{len(hidden_ranges)}{C.D}")
    for cidr, ips_in_range in sorted(hidden_ranges.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        warn(f"{cidr} ({len(ips_in_range)} IPs)")

    save(results_dir, "all_ips.txt", "\n".join(sorted(ips)))
    save(results_dir, "ip_ranges.json", json.dumps(ip_ranges, indent=2))
    save(results_dir, "cidr_ranges.txt", "\n".join(sorted(cidr_ranges)))
    save(results_dir, "hidden_ranges.json", json.dumps(hidden_ranges, indent=2))
    if cname_map:
        save(results_dir, "cname_map.json", json.dumps(cname_map, indent=2))
    if mx_records:
        save(results_dir, "mx_records.txt", "\n".join(mx_records))
    if txt_records:
        save(results_dir, "txt_records.txt", "\n".join(txt_records))

    return sorted(ips)


# ─────────────────────────────────────────────
# PHASE 3: Port Scanning (Batched naabu)
# ─────────────────────────────────────────────
def phase3_ports(ips, results_dir):
    phase_header(3, "PORT SCANNING")

    if not ips:
        return []

    infile = results_dir / "portscan_input.txt"
    infile.write_text("\n".join(ips), encoding="utf-8")

    batch_size = 100
    total_batches = (len(ips) - 1) // batch_size + 1
    all_results = []

    info(f"Scanning {len(ips)} IPs in {total_batches} batches")
    for i in range(0, len(ips), batch_size):
        batch = ips[i:i+batch_size]
        batch_file = results_dir / f"batch_{i}.txt"
        batch_file.write_text("\n".join(batch), encoding="utf-8")
        batch_out = results_dir / f"batch_{i}_out.txt"
        progress_bar(i // batch_size + 1, total_batches, "naabu")
        run_cmd(
            f'naabu -l "{batch_file}" -o "{batch_out}" -silent -p 80,443,8080,8443,22,21,25,53,110,143,3306,3389,5432,6379,8000,8888,9090,27017,9200,9300 -c 50',
            timeout=120, silent=True
        )
        if batch_out.exists():
            all_results.extend(batch_out.read_text().splitlines())
        batch_file.unlink(missing_ok=True)
        batch_out.unlink(missing_ok=True)
    print()

    unique_results = sorted(set([l.strip() for l in all_results if l.strip()]))

    port_services = {}
    svc_map = {21: "FTP", 22: "SSH", 25: "SMTP", 53: "DNS", 80: "HTTP",
               110: "POP3", 143: "IMAP", 443: "HTTPS", 3306: "MySQL",
               3389: "RDP", 5432: "PostgreSQL", 6379: "Redis",
               8080: "HTTP-Alt", 8443: "HTTPS-Alt", 27017: "MongoDB",
               9200: "Elasticsearch", 9300: "Elasticsearch"}
    for entry in unique_results:
        if ":" in entry:
            _, port = entry.rsplit(":", 1)
            try:
                port_services[entry] = svc_map.get(int(port), "Unknown")
            except:
                pass

    stat("Open ports", f"{C.BG}{len(unique_results)}{C.D}")
    for entry in unique_results[:20]:
        ip, port = entry.split(":")
        svc = port_services.get(entry, "")
        info(f"{ip}:{port} ({svc})")

    save(results_dir, "open_ports.txt", "\n".join(sorted(unique_results)))
    save(results_dir, "port_services.json", json.dumps(port_services, indent=2))
    return unique_results


# ─────────────────────────────────────────────
# PHASE 4: HTTP Probe (Batched httpx)
# ─────────────────────────────────────────────
def phase4_http(subdomains, results_dir):
    phase_header(4, "HTTP PROBING")

    if not subdomains:
        return []

    infile = results_dir / "httpx_input.txt"
    urls = [f"https://{sub}" for sub in subdomains]
    infile.write_text("\n".join(urls), encoding="utf-8")

    batch_size = 500
    total_batches = (len(urls) - 1) // batch_size + 1
    all_results = []

    info(f"Probing {len(urls)} URLs in {total_batches} batches")
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i+batch_size]
        batch_file = results_dir / f"httpx_batch_{i}.txt"
        batch_file.write_text("\n".join(batch), encoding="utf-8")
        batch_out = results_dir / f"httpx_batch_{i}_out.txt"
        progress_bar(i // batch_size + 1, total_batches, "httpx")
        run_cmd(
            f'httpx -l "{batch_file}" -o "{batch_out}" -silent -status-code -title -tech-detect -follow-redirects -content-length -web-server -ports 80,443,8080,8443 -t 100 -timeout 10 -retries 2',
            timeout=300, silent=True
        )
        if batch_out.exists():
            all_results.extend(batch_out.read_text().splitlines())
        batch_file.unlink(missing_ok=True)
        batch_out.unlink(missing_ok=True)
    print()

    live_hosts = sorted(set([l.strip() for l in all_results if l.strip()]))
    stat("Live hosts", f"{C.BG}{len(live_hosts)}{C.D}")
    for h in live_hosts[:15]:
        info(h)

    save(results_dir, "live_hosts.txt", "\n".join(live_hosts))
    return live_hosts


# ─────────────────────────────────────────────
# PHASE 5: Web Crawling (Custom Deep Crawler)
# ─────────────────────────────────────────────
def phase5_crawl(domain, live_hosts, results_dir):
    phase_header(5, "WEB CRAWLING")

    sys.path.insert(0, SCRIPT_DIR)
    try:
        from crawler import DeepCrawler, print_result
    except ImportError:
        fail("crawler.py not found")
        return []

    target_urls = []
    for h in live_hosts:
        url = h.split(" ")[0] if " " in h else h
        if not url.startswith("http"):
            url = f"https://{url}"
        target_urls.append(url)

    if not target_urls:
        target_urls = [f"https://{domain}"]

    max_hosts = min(len(target_urls), 200)
    all_urls = []
    all_interesting = []
    all_api = []
    all_forms = []
    all_params = []
    all_comments = []

    info(f"Deep crawling {max_hosts} hosts (depth=3, concurrency=30)")

    async def crawl_batch(hosts_batch, batch_idx):
        crawler = DeepCrawler(max_depth=3, max_pages=100, concurrency=30, timeout=10)
        batch_results = []
        for url in hosts_batch:
            parsed_url = urllib.parse.urlparse(url)
            host_domain = parsed_url.hostname
            if host_domain:
                result = await crawler.crawl(url, host_domain)
                batch_results.append(result)
                crawler = DeepCrawler(max_depth=3, max_pages=100, concurrency=30, timeout=10)
        return batch_results

    batch_size = 50
    for i in range(0, max_hosts, batch_size):
        batch = target_urls[i:i+batch_size]
        progress_bar(i // batch_size + 1, (max_hosts - 1) // batch_size + 1, "crawling")
        try:
            results = asyncio.run(crawl_batch(batch, i // batch_size))
            for r in results:
                all_urls.extend(r.get("urls", []))
                all_interesting.extend(r.get("interesting", []))
                all_api.extend(r.get("api_endpoints", []))
                all_forms.extend(r.get("forms", []))
                all_params.extend(r.get("params", []))
                all_comments.extend(r.get("comments", []))
        except Exception as e:
            warn(f"Batch {i//batch_size + 1} error: {e}")
    print()

    all_urls = sorted(set(all_urls))
    all_interesting = sorted(set(all_interesting))
    all_api = sorted(set(all_api))
    all_params = sorted(set(all_params))

    save(results_dir, "crawled_urls.txt", "\n".join(all_urls))
    save(results_dir, "interesting_urls.txt", "\n".join(all_interesting))
    if all_api:
        save(results_dir, "api_endpoints.txt", "\n".join(all_api))
    if all_forms:
        save(results_dir, "forms.json", json.dumps(all_forms, indent=2))
    if all_params:
        save(results_dir, "parameters.txt", "\n".join(all_params))
    if all_comments:
        save(results_dir, "comments.json", json.dumps(all_comments[:200], indent=2))

    stat("Crawled URLs", f"{C.BG}{len(all_urls)}{C.D}")
    if all_interesting:
        stat("Interesting URLs", f"{C.BR}{len(all_interesting)}{C.D}")
        for u in all_interesting[:15]:
            warn(u)
    if all_api:
        stat("API Endpoints", f"{C.BY}{len(all_api)}{C.D}")
        for u in all_api[:10]:
            info(u)
    if all_params:
        stat("Parameters", f"{C.BC}{len(all_params)}{C.D}")
    if all_forms:
        stat("Forms", f"{C.BM}{len(all_forms)}{C.D}")
    if all_comments:
        stat("Interesting Comments", f"{C.BM}{len(all_comments)}{C.D}")

    if not all_urls:
        info("No URLs crawled (site may block crawlers)")

    return all_urls


# ─────────────────────────────────────────────
# PHASE 6: Sensitive File Discovery
# ─────────────────────────────────────────────
def phase6_sensitive(live_hosts, results_dir):
    phase_header(6, "SENSITIVE FILE DISCOVERY")

    paths = [
        "/.env", "/.env.local", "/.env.production", "/.env.development",
        "/.git/config", "/.git/HEAD",
        "/phpinfo.php", "/info.php", "/test.php",
        "/robots.txt", "/sitemap.xml",
        "/.htaccess", "/.htpasswd",
        "/.DS_Store", "/server-status", "/server-info",
        "/.well-known/security.txt",
    ]

    urls = []
    for h in live_hosts:
        url = h.split(" ")[0] if " " in h else h
        if not url.startswith("http"):
            url = f"https://{url}"
        urls.append(url.rstrip("/"))

    if not urls:
        return []

    batch_size = 20
    total_batches = min(len(urls), 50) // batch_size + 1
    all_found = []

    info(f"Checking {min(len(urls), 50)} hosts x {len(paths)} paths")
    for i in range(0, min(len(urls), 50), batch_size):
        batch = urls[i:i+batch_size]
        urls_file = results_dir / f"sensitive_batch_{i}.txt"
        check_urls = [f"{base}{p}" for base in batch for p in paths]
        urls_file.write_text("\n".join(check_urls), encoding="utf-8")
        batch_out = results_dir / f"sensitive_out_{i}.txt"
        progress_bar(i // batch_size + 1, total_batches, "httpx")
        run_cmd(
            f'httpx -l "{urls_file}" -o "{batch_out}" -silent -mc 200,301,302,403 -content-length -title -t 100 -timeout 10 -retries 1',
            timeout=300, silent=True
        )
        if batch_out.exists():
            all_found.extend(batch_out.read_text().splitlines())
        urls_file.unlink(missing_ok=True)
        batch_out.unlink(missing_ok=True)
    print()

    found = sorted(set([l.strip() for l in all_found if l.strip()]))
    stat("Sensitive files found", f"{C.BR}{len(found)}{C.D}")
    for f in found[:20]:
        warn(f)

    return found


# ─────────────────────────────────────────────
# PHASE 7: Domain Info
# ─────────────────────────────────────────────
def phase7_domain_info(domain, results_dir):
    phase_header(7, "DOMAIN INFORMATION")

    # WHOIS
    if check_tool("whois"):
        info("WHOIS lookup")
        whois_data = run_cmd(f'whois {domain}', timeout=30)
    else:
        info("WHOIS lookup (python-whois)")
        try:
            import whois as python_whois
            w = python_whois.whois(domain)
            whois_data = str(w)
        except:
            whois_data = ""
    if whois_data:
        save(results_dir, "whois.txt", whois_data)
        ok("WHOIS data saved")

    # DNS records
    info("DNS records")
    dns_records = {}
    for rtype in ["A", "AAAA", "MX", "NS", "TXT", "SOA", "CNAME"]:
        output = run_cmd(f'nslookup -type={rtype} {domain}', timeout=10)
        if output and "Address:" in output:
            dns_records[rtype] = output
    save(results_dir, "dns_records.json", json.dumps(dns_records, indent=2))
    ok(f"DNS records: {len(dns_types)} types" if False else f"DNS records: {len(dns_records)} types")

    # Google dorks
    info("Google dorking hints")
    dorks = [
        f'site:{domain} filetype:pdf', f'site:{domain} filetype:doc OR filetype:docx',
        f'site:{domain} filetype:xls OR filetype:xlsx', f'site:{domain} intitle:"index of"',
        f'site:{domain} inurl:admin', f'site:{domain} inurl:login',
        f'site:{domain} "password"', f'site:{domain} "confidential"',
        f'site:{domain} "internal use only"', f'site:{domain} ext:sql | ext:bak | ext:old',
        f'site:{domain} inurl:api', f'site:{domain} inurl:debug',
    ]
    for d in dorks:
        info(f'{C.DIM}{d}{C.D}')
    save(results_dir, "google_dorks.txt", "\n".join(dorks))


# ─────────────────────────────────────────────
# PHASE 8: Final Report
# ─────────────────────────────────────────────
def generate_report(domain, results_dir, data, elapsed):
    phase_header(8, "FINAL REPORT")

    report = results_dir / "REPORT.md"
    lines = []

    lines.append(f"# RECONPRO Recon Report: {domain}")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Scan Time:** {timer_str(elapsed)}")
    lines.append(f"**Pipeline:** RECONPRO v3.1\n")

    lines.append("## Executive Summary")
    lines.append(f"- **Subdomains:** {len(data.get('subdomains', []))}")
    lines.append(f"- **IP Addresses:** {len(data.get('ips', []))}")
    lines.append(f"- **Open Ports:** {len(data.get('open_ports', []))}")
    lines.append(f"- **Live Hosts:** {len(data.get('live_hosts', []))}")
    lines.append(f"- **Crawled URLs:** {len(data.get('crawled_urls', []))}")
    lines.append(f"- **API Endpoints:** {len(data.get('api_endpoints', []))}")
    lines.append(f"- **Parameters:** {len(data.get('parameters', []))}")
    lines.append(f"- **Forms:** {len(data.get('forms', []))}")
    lines.append(f"- **Comments:** {len(data.get('comments', []))}")
    lines.append(f"- **Sensitive Files:** {len(data.get('sensitive_files', []))}")
    lines.append(f"- **Hidden IP Ranges:** {len(data.get('hidden_ranges', {}))}\n")

    total = len(data.get('subdomains', [])) + len(data.get('open_ports', [])) + len(data.get('sensitive_files', []))
    risk = "CRITICAL" if total > 100 else "HIGH" if total > 50 else "MEDIUM" if total > 20 else "LOW"
    lines.append(f"**Risk Level:** {risk}\n")

    lines.append("## Subdomains (Top 100)")
    for s in data.get('subdomains', [])[:100]:
        lines.append(f"- {s}")
    lines.append("")

    lines.append("## IP Addresses")
    for ip in data.get('ips', []):
        lines.append(f"- {ip}")
    lines.append("")

    if data.get('hidden_ranges'):
        lines.append("## Hidden IP Ranges")
        for cidr, ips_list in data['hidden_ranges'].items():
            lines.append(f"- **{cidr}** ({len(ips_list)} IPs)")
        lines.append("")

    lines.append("## Open Ports")
    services = data.get('port_services', {})
    for port in data.get('open_ports', []):
        svc = services.get(port, "")
        lines.append(f"- {port} ({svc})")
    lines.append("")

    lines.append("## Live Hosts")
    for h in data.get('live_hosts', []):
        lines.append(f"- {h}")
    lines.append("")

    if data.get('crawled_urls'):
        lines.append("## Crawled URLs (Interesting)")
        for u in data.get('crawled_urls', [])[:100]:
            lines.append(f"- {u}")
        lines.append("")

    if data.get('api_endpoints'):
        lines.append("## API Endpoints")
        for u in data.get('api_endpoints', []):
            lines.append(f"- `{u}`")
        lines.append("")

    if data.get('parameters'):
        lines.append("## Parameters Found")
        for p in data.get('parameters', []):
            lines.append(f"- `{p}`")
        lines.append("")

    if data.get('forms'):
        lines.append("## Forms")
        for f in data.get('forms', []):
            lines.append(f"- **{f.get('method', 'GET')}** `{f.get('action', '')}` — params: {', '.join(f.get('params', []))}")
        lines.append("")

    if data.get('comments'):
        lines.append("## Interesting Comments")
        for c in data.get('comments', [])[:30]:
            lines.append(f"- [{c.get('type', '')}] `{c.get('url', '')}`: {c.get('comment', '')[:200]}")
        lines.append("")

    lines.append("## Sensitive Files")
    if data.get('sensitive_files'):
        for f in data['sensitive_files']:
            lines.append(f"- **{f}**")
    else:
        lines.append("None found")
    lines.append("")

    if data.get('google_dorks'):
        lines.append("## Google Dorks")
        for d in data['google_dorks']:
            lines.append(f"- `{d}`")
        lines.append("")

    lines.append("## Tools Used")
    lines.append("| Tool | Purpose |")
    lines.append("|------|---------|")
    for tool, purpose in [
        ("subfinder", "Subdomain enumeration"), ("amass", "Subdomain enumeration (passive)"),
        ("crt.sh", "Certificate transparency"), ("certspotter", "Certificate transparency"),
        ("rapiddns", "DNS history"), ("hackertarget", "Subdomain discovery"),
        ("alienvault OTX", "Threat intelligence"), ("threatcrowd", "Threat intelligence"),
        ("threatminer", "Threat intelligence"), ("anubis", "Subdomain discovery"),
        ("subdomaincenter", "Subdomain discovery"), ("wayback machine", "URL history"),
        ("dnsx", "DNS resolution"), ("naabu", "Port scanning"),
        ("httpx", "HTTP probing + tech detection"), ("custom crawler", "Deep async web crawling + JS analysis"),
        ("whois", "Domain information"),
    ]:
        lines.append(f"| {tool} | {purpose} |")

    report.write_text("\n".join(lines), encoding="utf-8")
    ok(f"Report saved: {report}")

    print(f"\n{C.BOLD}{C.BC}{LINE*72}")
    print(f"  SCAN COMPLETE: {domain}")
    print(f"{LINE*72}{C.D}\n")

    summary = [
        ("Subdomains", len(data.get('subdomains', []))),
        ("IP Addresses", len(data.get('ips', []))),
        ("Open Ports", len(data.get('open_ports', []))),
        ("Live Hosts", len(data.get('live_hosts', []))),
        ("Crawled URLs", len(data.get('crawled_urls', []))),
        ("API Endpoints", len(data.get('api_endpoints', []))),
        ("Parameters", len(data.get('parameters', []))),
        ("Sensitive Files", len(data.get('sensitive_files', []))),
        ("Hidden Ranges", len(data.get('hidden_ranges', {}))),
    ]
    max_label = max(len(l) for l, _ in summary)
    for label, val in summary:
        color = C.BR if "File" in label else C.BG
        print(f"    {C.DIM}│{C.D}  {label:<{max_label}}  {color}{C.BOLD}{val}{C.D}")

    print(f"\n    {C.DIM}│{C.D}  {'Scan Time':<{max_label}}  {C.BY}{timer_str(elapsed)}{C.D}")
    print(f"    {C.DIM}│{C.D}  {'Risk Level':<{max_label}}  {C.BR}{risk}{C.D}")
    print(f"\n    {C.DIM}╰{'─'*50}╯{C.D}")
    print(f"    {C.BG}✔ Results saved to: {results_dir.absolute()}{C.D}\n")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

    os.system("cls" if sys.platform == "win32" else "clear")
    banner()

    print(f"    {C.DIM}{'─'*50}{C.D}")
    print(f"    {C.BC}Enter target domain to begin reconnaissance{C.D}")
    print(f"    {C.DIM}{'─'*50}{C.D}\n")

    try:
        domain = input(f"    {C.BG}❯{C.D} {C.BOLD}Target: {C.D}").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)

    if not domain:
        fail("No target specified")
        sys.exit(1)

    domain = domain.lower().replace("https://", "").replace("http://", "").rstrip("/")
    parts = domain.split(".")
    if len(parts) > 2:
        domain = ".".join(parts[-2:])

    print(f"\n    {C.DIM}{'─'*50}{C.D}")
    stat("Target", domain, C.BG)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path(f"recon_{domain}_{timestamp}")
    results_dir.mkdir(exist_ok=True)
    stat("Output", str(results_dir.absolute()), C.BC)

    tools_found = []
    for t in ["subfinder", "amass", "dnsx", "naabu", "httpx", "whois"]:
        if check_tool(t):
            tools_found.append(t)
    stat("Tools", f"{len(tools_found)}/6 available", C.BY)
    print(f"    {C.DIM}{'─'*50}{C.D}\n")

    data = {}
    start = time.time()

    data["subdomains"] = phase1_subdomains(domain, results_dir)
    data["ips"] = phase2_dns(domain, data["subdomains"], results_dir)

    port_results = phase3_ports(data["ips"], results_dir)
    data["open_ports"] = [p for p in port_results if isinstance(p, str) and ":" in p]
    data["port_services"] = {}
    svc_file = results_dir / "port_services.json"
    if svc_file.exists():
        data["port_services"] = json.loads(svc_file.read_text())

    data["live_hosts"] = phase4_http(data["subdomains"], results_dir)
    data["crawled_urls"] = phase5_crawl(domain, data["live_hosts"], results_dir)
    data["sensitive_files"] = phase6_sensitive(data["live_hosts"], results_dir)

    api_file = results_dir / "api_endpoints.txt"
    if api_file.exists():
        data["api_endpoints"] = api_file.read_text().splitlines()
    params_file = results_dir / "parameters.txt"
    if params_file.exists():
        data["parameters"] = params_file.read_text().splitlines()
    forms_file = results_dir / "forms.json"
    if forms_file.exists():
        data["forms"] = json.loads(forms_file.read_text())
    comments_file = results_dir / "comments.json"
    if comments_file.exists():
        data["comments"] = json.loads(comments_file.read_text())
    phase7_domain_info(domain, results_dir)

    dork_file = results_dir / "google_dorks.txt"
    if dork_file.exists():
        data["google_dorks"] = dork_file.read_text().splitlines()

    hr_file = results_dir / "hidden_ranges.json"
    if hr_file.exists():
        data["hidden_ranges"] = json.loads(hr_file.read_text())

    elapsed = time.time() - start
    generate_report(domain, results_dir, data, elapsed)


if __name__ == "__main__":
    main()
