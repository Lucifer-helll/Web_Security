# PortSwigger

## Lab: Stored DOM XSS

### Vulnerability

Blog comments are fetched and inserted into the page with `innerHTML`. The custom `escapeHTML()` function only escapes the first `<` and `>` characters, so later HTML in a stored comment remains active.

### Goal

Trigger `alert(1)` from a stored blog comment.

### Workflow

1. Open a blog post and submit a harmless comment. Inspect the page and the JavaScript responsible for loading comments.

   ![Comment rendering and script source](image.png)

2. The script retrieves comments, then renders the comment body using:

   ```js
   commentBodyPElement.innerHTML = escapeHTML(comment.body);
   ```

   ![Comment-loading code](image-1.png)

   ![Vulnerable DOM sink](image-2.png)

3. `escapeHTML()` is incomplete because `String.replace()` without a global regular expression replaces only the first occurrence of each character:

   ```js
   function escapeHTML(html) {
     return html.replace('<', '&lt;').replace('>', '&gt;');
   }
   ```

4. Submit this comment payload:

   ```html
   <script><img src=x onerror=alert(1)>
   ```

   The first `<script>` tag is rendered as harmless text after escaping. The following `<img>` tag is not fully escaped, however, and is parsed by `innerHTML`. Its invalid `src` triggers the `onerror` handler, which executes `alert(1)`.

   ![Payload submitted](image-4.png)

5. Reload or view the post. The stored payload executes when the comment is rendered.

   ![Alert triggered](image-3.png)

The lab is solved.

### Secure Approach

Render untrusted text with `textContent` rather than `innerHTML`:

```js
commentBodyPElement.textContent = comment.body;
```
