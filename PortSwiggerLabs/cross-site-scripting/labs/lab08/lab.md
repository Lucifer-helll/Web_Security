> platform -> PortSwigger
> Target ->  Lab: Stored XSS into anchor href attribute with double quotes HTML-encoded
----
*where is Vulnerability: in comment field website field* ![alt text](image.png)
*Goal:alert*

---


#### Steps:
1. Open the lab in your browser.
2. Navigate to the blog post page.
3. In the comment field, enter the following payload in the "Website" field.
4. vulnerabilty ![alt text](image-1.png)
5. ![alt text](image-2.png) -> `href` attribute contains `javascript:alert(1)` -> clicking triggers execution of `alert(1)`.
6. solve the lab ![alt text](image-3.png)
