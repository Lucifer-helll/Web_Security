>> Target > Lab: User role controlled by request parameter

----
**Where is Vuln..**: cookie header
**Goal**: login as admin than delete carlos

-----

### Steps:
1. Open the lab and login as wiener ![alt text](image.png)
2. after login, check intercept request in burp send to repeater ![alt text](image-1.png)
3. i notice cookie Admin
4. now i change the cookie to admin true and change get parameter /admin ![alt text](image-2.png)
5. now i delete carlos ![alt text](image-3.png)
6. Lab solve ![alt text](image-4.png)


>>> Check poc.py for automate this attack
