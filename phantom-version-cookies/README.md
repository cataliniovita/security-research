# Phantom $Version Cookies Demo (Tomcat legacy parsing)

Reproduces behaviors from PortSwigger research: https://portswigger.net/research/bypassing-wafs-with-the-phantom-version-cookie

## Build & Run (Docker)

```bash
docker build -t phantom-cookies /Users/kesselbach/security-research/phantom-version-cookies
docker run --rm -p 8090:8090 --name phantom-cookies phantom-cookies
```

## Endpoints

- /echo — prints parsed cookies as seen by Tomcat/Spring
- /reflect?name=foo&value=bar — sets a cookie and UNSAFELY reflects $Path/$Domain if provided as headers

## Examples

1) Trigger legacy parsing with $Version=1 and quoted values:
```bash
curl -s -H 'Cookie: $Version=1; foo="bar"; $Path=/abc; $Domain=example.com' \
     http://localhost:8090/echo
```

2) Unsafe reflection of $Path and $Domain into Set-Cookie:
```bash
curl -i -H '$Path: /attacker' -H '$Domain: evil.example' \
     'http://localhost:8090/reflect?name=foo&value=bar'
```

3) Cookie splitting via multiple Cookie headers:
```bash
curl -s -H 'Cookie: param1=value1;' -H 'Cookie: param2=value2;' http://localhost:8090/echo
```

Note: This is intentionally insecure, for research only. Do not deploy to production.
