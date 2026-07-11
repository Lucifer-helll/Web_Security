>> platform portswigger
>>> ### Target -> Lab: Reflected XSS into a JavaScript string with single quote and backslash escaped


----
**Where is vuln search parameter**
**Goal alert**

----

### Steps
1. Open the lab
2. inject xss payload ![alt text](image.png)
3.  ![alt text](image-1.png) i'm already in script tag
4. so closed script tag and make new tag thank alert
```html
</script><script>alert(1)</script>
```
5. ![alt text](image-2.png) hit the payload
6. than solve the lab.....![alt text](image-3.png)
