# 🎯 Platform: PortSwigger

### 📝 Target: Lab - Visible error-based SQL injection

> **Vulnerability Location:** `TrackingId` cookie
> **Goal:** Find a way to leak the password for the `administrator` user, then log in to their account.

---

## 🔍 Analysis

### Understand the Error Mechanism

- Unlike blind SQLi, this application displays verbose database error messages directly in the HTTP response body.
- Injecting invalid syntax (like an unescaped single quote or mismatched comment) throws an "Unterminated string literal" error, proving the backend is evaluating our input and showing the result.
- **Database Info:** Contains a `users` table with `username` and `password` columns.

---

## 🚀 Exploitation

### Step 1: Force a Type Conversion (CAST) Error

- **Logic:** The goal is to force the database to evaluate a subquery (fetching the password) and then intentionally cause an error by trying to convert that string (the password) into an incompatible data type, like an integer or boolean. The database will complain and leak the string in the error message.
- **Initial Attempts:** Using `CAST(... AS int)` without proper commenting resulted in standard syntax errors rather than execution.

### Step 2: Extracting the Data via Boolean Casting

- **Working Payload:**
  ```sql
  ' AND CAST((select password from users LIMIT 1) As Bool) --
  ```
  _Note: The `--` successfully comments out the rest of the query, allowing the `CAST` function to execute._
- **Result / Extracted Data:** The application throws a fatal error because a password string cannot be converted to a boolean. The response explicitly leaks the password:
  > `ERROR: invalid input syntax for type boolean: "sjdhew0wzqxsugne968a"`

---

## 🛠️ Steps to Reproduce

1. **Access** the lab environment.
2. **Capture** the GET request in Burp Suite and locate the `TrackingId` cookie.
3. **Inject Payload:** Replace the cookie value with the injection payload: `' AND CAST((select password from users LIMIT 1) As Bool) --`.
4. **Analyze Response:** Look at the rendered response or HTML source to find the database error message revealing the password (`sjdhew0wzqxsugne968a`).
5. **Authenticate:** Log in to the application using the username `administrator` and the extracted password.
6. 🎉 **Lab is solved!**
