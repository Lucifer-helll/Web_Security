# Access Control Vulnerabilities

Access control is the security layer that decides what an authenticated or unauthenticated user is allowed to do. A broken access control vulnerability exists when an application lets a user access data, functions, or actions that should be restricted.

Authentication answers: "Who are you?"

Access control answers: "What are you allowed to access or perform?"

Authorization is the process of enforcing access control decisions.

## Why Access Control Matters

Access control failures are usually high-impact because they often allow attackers to:

- View another user's private data.
- Modify another user's account or records.
- Access administrator functionality.
- Perform privileged actions as a normal user.
- Bypass business rules such as payment, approval, limits, or ownership checks.
- Read, create, update, or delete resources through APIs.
- Escalate from a low-privileged account to a high-privileged account.

These bugs are common because developers often protect visible UI elements but forget to enforce authorization on the server side.

## Core Concepts

### Subject

The user, service, API client, or process making the request.

Examples:

- Anonymous visitor
- Normal authenticated user
- Moderator
- Administrator
- Internal service account

### Object

The resource being accessed.

Examples:

- User profile
- Order
- Invoice
- Message
- File
- Admin endpoint
- API record

### Action

The operation being performed on the object.

Examples:

- Read
- Create
- Update
- Delete
- Approve
- Export
- Invite
- Transfer

### Policy

The rule that defines whether a subject can perform an action on an object.

Example:

```text
User A can view only orders owned by User A.
Only administrators can delete users.
Only managers can approve refunds above a fixed amount.
```

## Access Control Models

### Vertical Access Control

Vertical access control restricts access based on privilege level or role.

Example:

- Normal users can view their profile.
- Admin users can manage all users.

A vertical privilege escalation bug occurs when a lower-privileged user can access higher-privileged functionality.

Example vulnerable request:

```http
GET /admin/deleteUser?username=carlos HTTP/1.1
Host: vulnerable-app.com
Cookie: session=normal-user-session
```

If a normal user can perform this action, vertical access control is broken.

### Horizontal Access Control

Horizontal access control restricts access between users at the same privilege level.

Example:

- User A can view User A's invoice.
- User B can view User B's invoice.
- User A must not view User B's invoice.

A horizontal privilege escalation bug occurs when one normal user can access another normal user's data.

Example vulnerable request:

```http
GET /my-account?id=123 HTTP/1.1
Host: vulnerable-app.com
Cookie: session=user-a-session
```

If changing `id=123` to `id=124` exposes another user's account, horizontal access control is broken.

### Context-Dependent Access Control

Context-dependent access control restricts actions based on state, workflow, or business logic.

Example:

- A user can edit an order only before shipment.
- A user can apply a coupon only once.
- A reviewer can approve a request only after it is submitted.
- A user must complete payment before downloading a paid file.

These vulnerabilities appear when the application allows a user to skip steps, repeat actions, or perform actions in the wrong state.

## Common Types of Access Control Vulnerabilities

## 1. Unprotected Admin Functionality

Some applications expose administrator pages without proper server-side checks.

Examples:

```text
/admin
/administrator
/admin-panel
/admin/deleteUser
/manage-users
/console
```

Testing approach:

1. Log in as a normal user.
2. Browse directly to administrative paths.
3. Try privileged actions, not only page access.
4. Check whether the server blocks the request.

Important point: hiding admin links from the UI is not access control.

## 2. Admin URL Disclosure

Sometimes admin functionality is hidden at an unpredictable path but disclosed in client-side files.

Common places to inspect:

- `robots.txt`
- JavaScript files
- HTML comments
- Source maps
- API documentation
- Mobile app traffic
- Error messages

Example:

```text
Disallow: /administrator-panel
```

If a normal user can access the disclosed path, the application is vulnerable.

## 3. Parameter-Based Access Control

Applications sometimes trust request parameters to decide a user's role.

Dangerous examples:

```http
Cookie: Admin=true
Cookie: role=admin
Cookie: isAdmin=1
```

```http
POST /login HTTP/1.1

username=wiener&password=peter&role=admin
```

```json
{
  "username": "wiener",
  "isAdmin": true
}
```

If the user can modify these values and gain privileges, the application is vulnerable.

Secure applications must derive authorization from trusted server-side state, not user-controlled parameters.

## 4. Platform Misconfiguration

Access control can be bypassed because of web server, framework, proxy, or routing behavior.

Examples:

```text
/admin
/admin/
/admin%2f
/admin%252f
/ADMIN
/Admin
/admin/.
/admin/..
/admin//deleteUser
```

Other bypass methods:

- Changing HTTP method: `GET`, `POST`, `PUT`, `DELETE`, `PATCH`, `HEAD`
- Adding or removing trailing slashes
- Using URL encoding or double encoding
- Changing path case
- Adding path traversal sequences
- Using alternate headers such as `X-Original-URL` or `X-Rewrite-URL`

Example:

```http
POST / HTTP/1.1
Host: vulnerable-app.com
X-Original-URL: /admin/deleteUser
Content-Type: application/x-www-form-urlencoded

username=carlos
```

If middleware protects `/admin/deleteUser` but the backend honors `X-Original-URL`, authorization can be bypassed.

## 5. Method-Based Access Control Bypass

Some applications enforce access control only for specific HTTP methods.

Example:

```http
POST /admin/deleteUser HTTP/1.1
```

The server blocks this for normal users, but:

```http
GET /admin/deleteUser?username=carlos HTTP/1.1
```

or:

```http
HEAD /admin/deleteUser?username=carlos HTTP/1.1
```

may bypass the check.

Testing approach:

1. Capture a privileged request.
2. Send it as a lower-privileged user.
3. Change the HTTP method.
4. Check whether the action still executes.

## 6. Insecure Direct Object References

Insecure Direct Object Reference, often called IDOR, occurs when an application exposes a direct reference to an object and does not verify ownership or authorization.

Examples:

```text
/user/1001
/invoice/7362
/download?file=report.pdf
/api/orders/9004
/messages?user_id=12
```

If changing the identifier gives access to another user's object, the application is vulnerable.

Common object identifiers:

- Numeric IDs
- UUIDs
- Usernames
- Email addresses
- Filenames
- Account numbers
- Order IDs
- Document IDs
- Base64-encoded IDs
- Hashed or encrypted-looking values

Important point: unpredictable IDs reduce guessing, but they do not replace authorization checks.

## 7. IDOR With GUIDs or Unpredictable IDs

Some applications use GUIDs or long random identifiers. This can make enumeration harder, but the vulnerability still exists if authorization is missing.

Ways to discover valid identifiers:

- Public profiles
- Shared links
- Email notifications
- Application responses
- JavaScript variables
- Search results
- Referer headers
- Browser history
- Logs or exported files

Example:

```text
/user/7d0b0a2f-6f89-4e4b-b9c4-1e2c2bb8d301
```

If User A can use User B's GUID to access User B's record, it is still IDOR.

## 8. Multi-Step Process Access Control Flaws

Applications sometimes check authorization at the first step but not later steps.

Example workflow:

1. Admin opens user management page.
2. Admin selects a user.
3. Admin confirms deletion.
4. Server deletes the user.

If only step 1 checks admin privileges, a normal user may directly send the final deletion request.

Testing approach:

1. Perform the workflow as a privileged user.
2. Capture every request.
3. Replay each request as a lower-privileged user.
4. Try skipping earlier steps.

## 9. Referer-Based Access Control

Some applications make authorization decisions based on the `Referer` header.

Example:

```http
GET /admin/deleteUser?username=carlos HTTP/1.1
Host: vulnerable-app.com
Referer: https://vulnerable-app.com/admin
Cookie: session=normal-user-session
```

This is insecure because the `Referer` header is user-controlled and can be removed or modified.

## 10. Location-Based Access Control

Some applications restrict functionality based on IP address, region, or network location.

Potential bypasses:

- Spoofed forwarding headers if the application trusts them incorrectly.
- Misconfigured reverse proxies.
- Access through alternate hostnames or internal routes.
- Weak separation between internal and external interfaces.

Headers to test carefully:

```text
X-Forwarded-For: 127.0.0.1
X-Real-IP: 127.0.0.1
Client-IP: 127.0.0.1
Forwarded: for=127.0.0.1
X-Originating-IP: 127.0.0.1
```

Only test this in authorized environments.

## 11. API Access Control Failures

APIs commonly expose access control bugs because endpoints are easy to call directly.

Common API issues:

- Missing authorization on `GET`, `POST`, `PUT`, `PATCH`, or `DELETE`.
- User can change `userId`, `accountId`, `tenantId`, or `organizationId`.
- Admin-only fields are accepted from normal users.
- Mass assignment allows privilege changes.
- GraphQL resolvers miss object-level checks.
- Backend trusts frontend role flags.
- One endpoint is protected, but another equivalent endpoint is not.

Example vulnerable request:

```http
PATCH /api/users/123 HTTP/1.1
Content-Type: application/json
Cookie: session=normal-user-session

{
  "email": "attacker@example.com",
  "role": "admin"
}
```

If the server accepts `role`, this is a privilege escalation issue.

## 12. Multi-Tenant Access Control Failures

In SaaS applications, users often belong to organizations, teams, projects, or tenants.

High-risk identifiers:

```text
organizationId
tenantId
workspaceId
teamId
projectId
accountId
companyId
```

Common bugs:

- User from Tenant A can access Tenant B's records.
- API filters by user ID but not tenant ID.
- Invitation links expose another tenant.
- Export endpoints leak cross-tenant data.
- Search endpoints return objects from multiple tenants.
- Background jobs process records without tenant scoping.

Every object-level check should include both identity and tenant boundary.

## 13. Forced Browsing

Forced browsing means directly requesting resources or paths that are not linked in the UI.

Examples:

```text
/backup.zip
/users/export
/admin/report
/debug
/staging
/old
/internal
```

If sensitive resources are accessible only because the user knows the URL, access control is broken.

## 14. File Access Control Bugs

File-related endpoints often contain authorization flaws.

Examples:

```text
/download?file=123.pdf
/attachments/1001
/api/files/5542
/uploads/private/report.pdf
```

Test for:

- Accessing another user's files.
- Changing file IDs.
- Guessing filenames.
- Reusing signed URLs after logout.
- Expired links that do not expire.
- Public storage buckets with private files.
- File metadata leaking private links.

## 15. Function-Level Authorization Bugs

Function-level authorization controls access to actions, not just records.

Examples:

- Delete user
- Add team member
- Change role
- Refund payment
- Export data
- Approve request
- Disable MFA
- Rotate API key

The server must verify that the user is allowed to perform the action every time the action is requested.

## 16. Object-Level Authorization Bugs

Object-level authorization controls access to specific records.

Example:

```text
Can this user access this exact invoice?
Can this user update this exact project?
Can this user download this exact file?
```

This is the most common source of IDOR vulnerabilities.

## 17. Field-Level Authorization Bugs

Field-level authorization controls which fields a user can read or update.

Example:

```json
{
  "id": 10,
  "name": "Alice",
  "email": "alice@example.com",
  "role": "admin",
  "salary": 120000
}
```

A normal user may be allowed to see `name`, but not `salary` or `role`.

Common issue: the API returns sensitive fields and the frontend simply hides them.

## 18. Mass Assignment

Mass assignment occurs when an application automatically binds request body fields to server-side objects.

Example:

```json
{
  "name": "attacker",
  "email": "attacker@example.com",
  "isAdmin": true,
  "role": "admin",
  "balance": 999999
}
```

If the server updates restricted fields, the application is vulnerable.

Prevention:

- Use allowlists for accepted fields.
- Ignore or reject restricted fields.
- Use separate DTOs or request models for different roles.
- Enforce field-level authorization on the server.

## Testing Methodology

## Step 1: Map the Application

Identify:

- Roles
- Users
- Resources
- Actions
- Workflows
- API endpoints
- Object identifiers
- Admin functionality
- Tenant or organization boundaries

Useful account setup:

- Anonymous user
- Normal User A
- Normal User B
- Admin or higher-privileged user
- User from another organization or tenant, if applicable

## Step 2: Capture Requests

Use an intercepting proxy such as Burp Suite.

Capture:

- Login and logout
- Profile access
- Resource creation
- Resource viewing
- Resource update
- Resource deletion
- Admin actions
- File download
- Export actions
- Invitation and approval workflows
- API traffic

## Step 3: Test Vertical Privilege Escalation

1. Capture a privileged request as an admin.
2. Replace the admin session with a normal user session.
3. Send the request.
4. Check whether the action succeeds.
5. Test page access and direct action execution separately.

Expected secure behavior:

```text
403 Forbidden
404 Not Found
Redirect to login only when unauthenticated
No state change
No sensitive data returned
```

## Step 4: Test Horizontal Privilege Escalation

1. Create or identify a resource as User A.
2. Create or identify a similar resource as User B.
3. Send User A's request using User B's identifiers.
4. Check for data exposure or unauthorized state change.

Identifiers to modify:

```text
id
user
userId
uid
account
accountId
customer
customerId
order
orderId
invoice
invoiceId
file
fileId
document
documentId
tenant
tenantId
org
orgId
```

## Step 5: Test Context-Dependent Authorization

Try to:

- Skip workflow steps.
- Repeat one-time actions.
- Use expired links or tokens.
- Access resources after logout.
- Access resources after role removal.
- Edit locked or archived records.
- Approve your own request.
- Perform actions in the wrong order.

## Step 6: Test HTTP Method and Routing Bypasses

Try:

```text
GET
POST
PUT
PATCH
DELETE
HEAD
OPTIONS
```

Also try:

```text
/admin
/admin/
/admin//
/admin/.
/admin/../admin
/%61dmin
/admin%2fdeleteUser
/admin%252fdeleteUser
```

## Step 7: Test Header-Based Bypasses

Headers worth testing in authorized labs:

```text
X-Original-URL: /admin
X-Rewrite-URL: /admin
X-Forwarded-For: 127.0.0.1
X-Real-IP: 127.0.0.1
X-Forwarded-Host: localhost
X-Host: localhost
Referer: https://target/admin
```

## Step 8: Test APIs Separately From UI

Do not rely only on browser navigation.

Test:

- REST endpoints
- GraphQL queries and mutations
- Mobile API traffic
- Hidden endpoints in JavaScript
- Old API versions
- Bulk endpoints
- Export endpoints
- Search endpoints
- Autocomplete endpoints
- File endpoints

## GraphQL Access Control Testing

GraphQL can hide multiple authorization problems behind a single endpoint.

Test:

- Queries for another user's object.
- Mutations using another user's ID.
- Admin-only mutations as a normal user.
- Nested objects that leak restricted data.
- Introspection exposure.
- Field-level leaks.
- Batch queries that bypass checks.

Example:

```graphql
query {
  user(id: "123") {
    id
    email
    role
    invoices {
      id
      amount
    }
  }
}
```

Each resolver must enforce authorization for the object and field it returns.

## Common Status Codes

### Secure Responses

```text
401 Unauthorized: user is not authenticated.
403 Forbidden: user is authenticated but not authorized.
404 Not Found: sometimes used to avoid revealing that a resource exists.
```

### Suspicious Responses

```text
200 OK with another user's data.
204 No Content after an unauthorized state change.
302 redirect but action still happens.
500 error that leaks data or confirms object existence.
Different response lengths for valid and invalid object IDs.
```

## Impact

Access control vulnerabilities can lead to:

- Account takeover.
- Data leakage.
- Data modification.
- Data deletion.
- Privilege escalation.
- Tenant isolation failure.
- Financial fraud.
- Compliance violations.
- Full administrative compromise.

Severity depends on:

- Sensitivity of accessed data.
- Privilege level gained.
- Whether state-changing actions are possible.
- Number of affected users or tenants.
- Ease of exploitation.
- Whether exploitation requires authentication.

## Prevention

## 1. Deny by Default

Access should be blocked unless explicitly allowed.

## 2. Enforce Authorization Server-Side

Never rely on:

- Hidden buttons
- Disabled UI controls
- Client-side JavaScript checks
- User-controlled cookies
- Request parameters
- Referer headers

## 3. Check Authorization on Every Request

Every protected request must verify:

- Who is making the request.
- What object is being accessed.
- What action is being performed.
- Whether the current context allows it.

## 4. Use Centralized Authorization Logic

Avoid scattered checks across controllers. Use shared authorization middleware, policy objects, guards, or service-layer checks.

## 5. Enforce Object Ownership

Always check whether the requested object belongs to the user or the user's tenant.

Example secure logic:

```text
SELECT * FROM invoices
WHERE id = :invoice_id
AND owner_user_id = :current_user_id;
```

For multi-tenant apps:

```text
SELECT * FROM projects
WHERE id = :project_id
AND tenant_id = :current_tenant_id;
```

## 6. Use Allowlisted Input Models

Only accept fields that the current user is allowed to set.

## 7. Avoid Exposing Sensitive Identifiers

Use indirect references where appropriate, but do not depend on obscurity. Authorization checks are still required.

## 8. Log and Monitor Authorization Failures

Monitor:

- Repeated 403 responses
- Sequential ID probing
- Cross-tenant access attempts
- Admin endpoint requests from normal users
- Suspicious method changes
- Header-based bypass attempts

## 9. Test Access Control Automatically

Include tests for:

- Normal user cannot access admin endpoints.
- User A cannot access User B's resources.
- Tenant A cannot access Tenant B's resources.
- Restricted fields cannot be updated.
- Locked resources cannot be modified.
- Removed users lose access immediately.

## Secure Design Checklist

- Access control is enforced on the server.
- Authorization checks are applied to every endpoint.
- Admin functions require admin role checks.
- Object ownership is checked before read, update, and delete.
- Tenant boundaries are enforced in every query.
- APIs do not accept restricted fields from normal users.
- Sensitive fields are not returned to unauthorized users.
- URL knowledge alone does not grant access.
- HTTP method changes do not bypass authorization.
- Routing normalization does not bypass authorization.
- Workflow state is checked before sensitive actions.
- Signed URLs expire and are scoped to the correct user.
- Authorization failures are logged.
- Automated tests cover negative access cases.

## Reporting Template

```text
Title:
Broken access control allows [user type] to [action] [resource]

Summary:
The application fails to enforce authorization on [endpoint/function/resource]. A [low-privileged/normal] user can [impact].

Affected endpoint:
[HTTP method] [path]

Steps to reproduce:
1. Log in as [user/role].
2. Capture the request to [endpoint].
3. Modify [parameter/session/header].
4. Send the request.
5. Observe that [unauthorized data/action] is allowed.

Expected result:
The server should reject the request with 403 or equivalent and no state change should occur.

Actual result:
The server returns [data] or performs [action].

Impact:
[Explain data exposure, privilege escalation, tenant breach, account takeover, or business impact.]

Recommendation:
Enforce server-side authorization for [object/action/role] and add tests covering unauthorized access attempts.
```

## Key Takeaways

- Access control must be enforced on the server, not in the UI.
- Always test with at least two users and different roles.
- IDOR is an object-level authorization failure.
- Admin link hiding is not protection.
- Every endpoint, method, object, field, and workflow step needs authorization.
- In multi-tenant applications, tenant isolation must be verified everywhere.
- Unpredictable IDs are not a substitute for permission checks

# What is IAAA?

IAAA stands for **Identification, Authentication, Authorization, and Accounting** — the four pillars that form the complete foundation of access control. Each one answers a different question:

## 1. Identification — "Who are you claiming to be?"

This is the first step, where a user claims an identity — usually through a username, email, or user ID. There's no proof involved yet, just a claim.

- Example: Entering a username into a login form.
- Weak identification issues: predictable user IDs, enumeration vulnerabilities (e.g. `/api/users/1001`, `/api/users/1002`).

## 2. Authentication — "Prove you are who you say you are"

This verifies the claimed identity — through a password, OTP, biometric, token, or certificate.

- Factors: Something you know (password), something you have (OTP/token), something you are (fingerprint/face).
- Common vulnerabilities: weak passwords, broken MFA, JWT signature bypass, session fixation, credential stuffing.

## 3. Authorization — "What are you allowed to access or perform?"

Once authenticated, the system decides what resources/actions the verified user is allowed to access.

- Types: Role-Based Access Control (RBAC), Attribute-Based Access Control (ABAC).
- Common vulnerabilities: IDOR, privilege escalation, missing function-level access control, broken object-level authorization (BOLA).

## 4. Accounting (also called Auditing) — "What did you do, and when?"

This tracks the actions an authenticated and authorized user performed within the system — through logging, monitoring, and audit trails.

- Purpose: forensics, compliance, anomaly detection, non-repudiation.
- Real-world importance: in the event of a breach, accounting logs are what reveal exactly what the attacker did.
- Common weaknesses: insufficient logging, log tampering, no alerting on suspicious activity (OWASP's "Insufficient Logging & Monitoring" issue).

## Quick Summary Table

| Pillar         | Question it answers         | Example Mechanism        |
| -------------- | --------------------------- | ------------------------ |
| Identification | Who are you claiming to be? | Username, Email, User ID |
| Authentication | Can you prove it?           | Password, OTP, Biometric |
| Authorization  | What are you allowed to do? | RBAC, ABAC, Permissions  |
| Accounting     | What did you actually do?   | Logs, Audit Trails, SIEM |

## Why IAAA matters for VAPT/Access Control testing

Whenever you're testing access control, always check which pillar is being broken:

- Identification bypass → user enumeration
- Authentication bypass → weak login, 2FA bypass
- Authorization bypass → IDOR, privilege escalation (this is the core focus of your README)
- Accounting gap → missing logs, undetectable attacks

Access control vulnerabilities are mostly **Authorization** failures, but the root cause can sometimes trace back to weak Identification or Authentication.
