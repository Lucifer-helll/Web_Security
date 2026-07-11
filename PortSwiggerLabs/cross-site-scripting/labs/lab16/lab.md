>> Platform  -> portswigger
>> ### Target -> Lab: Reflected XSS with some SVG markup allowed 

----
**Where is vuln search field**
**Goal alert(1)**

----

### Steps :
1. -> open the lab
2. -> check where is vuln try in seaarch field vunilla xss alert -> ![alt text](image.png)
3. -> tags are blocked.
4. -> try svg tag -> ![alt text](image-1.png)
5. -> but event is block ![alt text](image-2.png)
6. -> now Fuzz event in burp pro intruder -> ![alt text](image-3.png)
7. -> ![alt text](image-4.png)
8. -> after hit and try this payload work -> begin event only work svg animatetransform
```html
<svg><animatetransform onbegin=alert(1) attributeName=transform>
<!-- use xss cheat sheet for this payloads provided by portswigger -->
```
9.  -> final execution -> ![alt text](image-6.png)
    - ![alt text](image-5.png)
10. lab solve -> ![alt text](image-7.png)
