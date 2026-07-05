// PortSwigger Labs ---> Platform
---
## Lab: 3 — Blind SSRF With Out-of-Band Detection
## Difficulty Level : 🟡 PRACTITIONER

---

### Where I Found Vulnerability ?
- **URL:** `/product?productId=1`
- **Parameter:** `Referer` Header ← Not a normal input field, its a HTTP Header

---

### Steps ?
1. Open any product page and intercept request in Burp
2. Find the `Referer` header in the intercepted request
3. Replace Referer value with your **Burp Collaborator URL**
4. Forward the request
5. Go to Burp Collaborator → Click **Poll Now**
6. DNS/HTTP interaction aaya → Blind SSRF Confirmed ✅

---

### Working Payload ?
```
Referer: https://YOUR-ID.burpcollaborator.net
```

---

### Why it Worked ?
- Server `Referer` header ki URL ko **background mein fetch** kar raha tha
- Ye fetch response user ko nahi dikhta — isliye **Blind SSRF** hai
- Burp Collaborator ek public server hai jo incoming requests record karta hai
- Jab server ne Collaborator URL fetch ki → humein ping/callback mila
- Normal user ko koi response nahi dikha — sirf Collaborator pe trace tha

---

### What I Learned ?
- Blind SSRF mein response directly nahi dikhta — **out-of-band detection** zaroori hai
- `Referer` header bhi SSRF ka entry point ho sakta hai — sirf URL parameters nahi
- Burp Collaborator / interactsh se server callbacks confirm hote hain
- Agar Collaborator pe DNS/HTTP ping aaye → SSRF confirmed, chahe response kuch bhi ho
- **Basic SSRF vs Blind SSRF:**

| | Basic SSRF | Blind SSRF |
|--|------------|------------|
| Response visible? | ✅ Yes | ❌ No |
| Detection method | Direct response | Out-of-band (Collaborator) |
| Harder to find? | Easy | Hard |

---

### Difficulty Comparison ?
```
Lab 1 → localhost/admin          (Basic - Response visible)
Lab 2 → 192.168.0.x scan        (Basic - Response visible)
Lab 3 → Referer + Collaborator  (Blind - No response) ← Harder
```
