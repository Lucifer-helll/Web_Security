**PortSwigger Labs - Platform**
`Lab - 1 Basic SSRF Against Local Server :
Difficulty Level - Apprentice`

### Where Vulnerability Found ?
URL: /product?productId=1
Parameter: stockApi (Check Stock button ke request mein)


### Steps
1. Check Stock button click kiya aur Burp mein intercept kiya
2. Request mein stockApi parameter mila
3. stockApi ki value change ki → http://localhost/admin
4. /admin panel open ho gaya
5. Carlos ko delete kiya → /admin/delete?username=carlos

### Working Payload
http://localhost/admin
http://localhost/admin/delete?username=carlos

### Why It Worked ?
Server khud /admin fetch kar raha tha
Admin panel sirf localhost se accessible tha
Isliye normal user access nahi kar sakta lekin server kar sakta hai

### What I Learned ?
- stockApi parameter directly URL fetch karta tha
- Server-side request thi isliye firewall bypass ho gayi
- localhost pe restricted panels SSRF se accessible ho sakte hain
