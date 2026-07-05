# 🎯 Platform: PortSwigger
### 📝 Target: Lab - SQL injection with filter bypass via XML encoding

> **Vulnerability Location:** `<storeId>` node in the XML body of the stock check feature.
> **Goal:** Perform a SQL injection attack to bypass the filter, retrieve the admin user's credentials from the `users` table, and log in.

---

## 🔍 Analysis & Attack Flow
### The Mechanism (WAF Bypass via XML Entities)
*   **The Obstacle:** The application employs a Web Application Firewall (WAF) or input filter that detects and blocks plain-text SQL injection keywords like `UNION` and `SELECT`.
*   **The Bypass:** The application accepts data in XML format. XML parsers inherently resolve XML entities (like hex encoding) before passing the parsed data to the underlying application logic (and subsequently the database).
*   **How it Works:** By encoding our malicious SQL payload into XML hex entities, the WAF inspects the request, sees only harmless-looking XML entities, and allows it through. Once inside, the XML parser decodes the hex entities back into the raw SQL payload (`UNION SELECT...`) right before executing the query.

---

## 🚀 Exploitation Steps

### Step 1: Intercept and Test the Stock Check
*   Capture the HTTP POST request to the `/product/stock` endpoint in Burp Suite Repeater.
*   Observe that the application uses XML to submit the `productId` and `storeId`.
*   Attempting a standard payload like `1 UNION SELECT NULL` in the `<storeId>` tag will likely be blocked or filtered.

### Step 2: Utilize Hackvertor for Hex Encoding
*   Highlight the SQL injection payload within the `<storeId>` tags.
*   Right-click and navigate to **Extensions > Hackvertor > Encode > hex_entities**.
*   Hackvertor will wrap the payload in dynamic tags: `<@hex_entities>...<@/hex_entities>`. Burp Suite will automatically encode the contents in real-time when the request is sent.

### Step 3: Construct and Send the Payload
*   **Target Payload:** We need to concatenate the username and password from the `users` table.
*   **Final Hackvertor Tagged Payload:**
    ```xml
    <storeId>
        <@hex_entities>1 UNION select username || '~' || password from users<@/hex_entities>
    </storeId>
    ```
*   Send the request.

### Step 4: Extract Credentials
*   Analyze the HTTP response. Since the XML parser decoded our payload, the database executed the `UNION SELECT` statement.
*   The response successfully reflects the concatenated credentials:
    > `administrator~7higech6ngvdtor613wx`
*   **Extracted Password:** `7higech6ngvdtor613wx`

### Step 5: Authenticate
*   Navigate to the `/my-account` login page.
*   Log in using the username `administrator` and the extracted password.
*   🎉 **Lab is solved!**
