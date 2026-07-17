>>> Target - Lab: User ID controlled by request parameter with data leakage in redirect

---

**Where is Vuln....**: on redirection url
**Goal**: gain carlos api key

---


### Steps 
1. #### open the lab
2. #### login as wiener user -> ![alt text](image.png)
3. #### capture this req.. in burp proxy
4. #### send to repeater than change user id to carlos -> ![alt text](image-1.png) response is 302 foud 
5. #### see this ![alt text](image-2.png) i have carlos api key submit this..
6. #### solve the lab.... ![alt text](image-3.png)




## check `poc.py` for automate attack
