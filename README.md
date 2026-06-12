# RECONPRO

**Advanced Red Team Reconnaissance Pipeline with Animated Terminal UI**

```
                                                                     
    ▄█████ ██  ██ █████▄ ██████ █████▄  ▄█████ ▄█████ ▄████▄ ██  ██ ██████ 
    ██      ▀██▀  ██▄▄██ ██▄▄   ██▄▄██▄ ▀▀▀▄▄▄ ██     ██  ██ ██  ██   ██   
    ▀█████   ██   ██▄▄█▀ ██▄▄▄▄ ██   ██ █████▀ ▀█████ ▀████▀ ▀████▀   ██   
                                                                       
```

A comprehensive 8-phase red team reconnaissance pipeline with **25+ subdomain sources**, animated terminal UI, progress bars, spinners, hidden IP range detection, batch processing, and cross-platform support.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-green?logo=windows&logoColor=white)
![Tools](https://img.shields.io/badge/Tools-25+-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Version](https://img.shields.io/badge/Version-3.1-cyan)

---

## Features

- **Prompt-Based Interactive UI** — Enter target domain, no CLI args needed
- **Animated Terminal** — Spinners, progress bars, phase indicators
- **15+ Subdomain Sources** — Maximum coverage from free APIs
- **Batch Processing** — No more timeouts on large targets
- **Hidden IP Range Detection** — Find /24 CIDR patterns
- **Custom Deep Crawler** — Async Python crawler, finds hidden APIs, JS endpoints, comments, forms
- **Cross-Platform** — Works on Windows & Linux
- **Professional Reports** — Markdown with risk assessment

---

## Preview

```
──────────────────────────────────────────────────
  Enter target domain to begin reconnaissance
──────────────────────────────────────────────────

❯ Target: tesla.com

├─ Target:      tesla.com
├─ Output:      recon_tesla.com_20260612_085125
├─ Tools:       5/7 available
──────────────────────────────────────────────────

● ○ ○ ○ ○ ○ ○ ○  PHASE 1/8: SUBDOMAIN ENUMERATION

    ▸ subfinder (primary)
    ⠋ Running subfinder
    ✔ subfinder: 1089 subdomains
    ▸ crt.sh (certificate transparency)
    ✔ crt.sh: 5144 subdomains
    ...

● ● ● ● ● ○ ○ ○  PHASE 4/8: HTTP PROBING

    httpx ████████████████████████████████████████ 100%
    ├─ Live hosts: 393

══════════════════════════════════════════════════
  SCAN COMPLETE: tesla.com
══════════════════════════════════════════════════

    │  Subdomains       1088
    │  IP Addresses     257
    │  Open Ports       248
    │  Live Hosts       393
    │  Sensitive Files  1987
    │  Scan Time        14m 22s
    │  Risk Level       CRITICAL

    ╰──────────────────────────────────────────╯
```

---

## Pipeline Phases

| Phase | Name | Description |
|-------|------|-------------|
| 1 | Subdomain Enumeration | 15 sources + DNS brute force |
| 2 | DNS Resolution | Bulk resolve + hidden IP ranges |
| 3 | Port Scanning | Batched naabu (19 ports) |
| 4 | HTTP Probing | Batched httpx with tech detection |
| 5 | Web Crawling | Custom deep async crawler |
| 6 | Sensitive File Discovery | .env, .git, phpinfo, etc. |
| 7 | Domain Information | WHOIS, DNS records, Google dorks |
| 8 | Final Report | Markdown report + summary |

---

## Subdomain Sources (25+)

| # | Source | Type |
|---|--------|------|
| 1 | subfinder | Primary enumeration |
| 2 | crt.sh (API) | Certificate transparency |
| 3 | amass (passive) | Passive enumeration |
| 4 | crt.sh (curl) | Fallback |
| 5 | rapiddns | DNS history |
| 6 | hackertarget | API-based discovery |
| 7 | AlienVault OTX | Threat intelligence |
| 8 | bufferover.run | TLS certificate data |
| 9 | ThreatCrowd | Threat intelligence |
| 10 | Anubis | Passive DNS |
| 11 | SubdomainCenter | API-based discovery |
| 12 | CertSpotter | Certificate transparency |
| 13 | Wayback Machine | URL history |
| 14 | ThreatMiner | Threat intelligence |
| 15 | DNS brute force | Active enumeration |
| 16 | ProjectDiscovery Chaos | Bug bounty dataset |
| 17 | Shodan InternetDB | IoT/device discovery |
| 18 | VirusTotal | Malware intelligence |
| 19 | DNSDumpster | DNS recon |
| 20 | Riddler.io | Passive DNS |
| 21 | FindSubdomains | Subdomain finder |
| 22 | crt.sh email (reverse) | Certificate + email |
| 23 | PassiveTotal | Risk intelligence |
| 24 | WhoisXML API | Whois data |
| 25 | SecurityTrails | Historical DNS |

---

## Installation

### Prerequisites

- **Python 3.8+** — [python.org](https://www.python.org/downloads/)
- **Go 1.21+** — [go.dev](https://go.dev/dl/)

### Quick Install

```bash
# Clone the repo
git clone https://github.com/QASIM1401/reconpro.git
cd reconpro

# Install Python dependencies
pip install -r requirements.txt

# Install Go tools (required)
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
```

---

## Usage

```bash
python recon.py
```

The tool will:
1. Show the RECONPRO banner
2. Prompt `❯ Target: ` — enter your domain
3. Run all 8 phases with animated output
4. Save results to `recon_<domain>_<timestamp>/`

---

## Output Structure

```
recon_example.com_20260612_085125/
├── REPORT.md              # Full markdown report
├── all_subdomains.txt     # All discovered subdomains
├── all_ips.txt            # Resolved IP addresses
├── hidden_ranges.json     # Hidden /24 CIDR ranges
├── open_ports.txt         # Open ports
├── port_services.json     # Port → service mapping
├── live_hosts.txt         # Live HTTP hosts with tech
├── interesting_urls.txt   # Crawled URLs (admin, API, etc.)
├── whois.txt              # WHOIS data
├── dns_records.json       # DNS records
├── google_dorks.txt       # Dorking queries
└── ...
```

---

## Tools Used

| Tool | Purpose | Required |
|------|---------|----------|
| subfinder | Subdomain enumeration | Yes |
| httpx | HTTP probing + tech detection | Yes |
| naabu | Port scanning | Yes |
| dnsx | DNS resolution | Yes |
| Python aiohttp | Custom deep web crawler | Yes |
| whois | Domain information | No |

---

## Legal Disclaimer

This tool is for **authorized security testing only**. Always obtain written permission before scanning any system you don't own. Unauthorized access to computer systems is illegal and punishable by law.

---

## Author

**Qasim Ali**
- GitHub: [@QASIM1401](https://github.com/QASIM1401)
- Email: qasim.sec1401@proton.me

---

## License

MIT License - see [LICENSE](LICENSE) for details.
