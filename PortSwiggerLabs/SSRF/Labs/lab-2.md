// Portswigger labs ---> platform
## lab: 2 -- Basic SSRf again another back-end system
## Difficulty Level : Apprentice

### Where I Found Vulnerabilty ?
URL: /product?productId=1 and You choose any product in this labs
Parameter: StockApi(check stock button)
And hame isme 192.168.0.x:8080 se reqeust lagwani hai

### step ?
1. check stock button click and intercept in burp
2. send to intruder and change stockapi value -> http://192.168.0.x:8080
3. add x in intruder and i find 200 ok and send repeater
4. and change -> http://192.168.0.167:8080/admin/delete?username=carlos
5. lab solve


### Working Payloads ?
http://192.168.0.x:8080
http://192.168.0.167:8080/admin/delete?username=carlos

### Why it Worked ?
- Admin panel 192.168.0.x:8080 pe tha — directly accessible nahi tha bahar se
- Server internally 192.168.0.x range ko access kar sakta tha
- Hum bahar se directly us IP pe nahi ja sakte the, lekin server ja sakta tha
- Intruder ne 1-255 range bruteforce karke sahi IP (167) dhundh di
- Firewall sirf external requests block karti hai — internal server-to-server allowed tha

### What I Learned ?
- SSRF sirf localhost tak limited nahi hoti — internal network (192.168.x.x) bhi target ho sakta hai
- Jab exact IP pata na ho toh Burp Intruder se 1-255 range fuzz karo
- 200 OK response matlab sahi IP mil gayi — baaki sab 500/404 denge
- Backend systems apna admin panel internal IP pe expose karte hain — SSRF se yahi risk hai
- Always check: koi bhi parameter jo URL/IP leta ho wo SSRF ka entry point hai
