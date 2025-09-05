# Cookie Chaos Django (Django parsing only)

Demonstrates how Django's own cookie parsing can surface prefix bypass scenarios showcased by PortSwigger, without any manual trimming in app code. The app relies solely on `request.COOKIES`.

- PortSwigger article: [Cookie Chaos: How to bypass __Host and __Secure cookie prefixes](https://portswigger.net/research/cookie-chaos-how-to-bypass-host-and-secure-cookie-prefixes)
- Django docs (session security note): [How to use sessions — Session security](https://docs.djangoproject.com/en/5.0/topics/http/sessions/#topics-session-security)

## Build & Run (Docker)
```bash
docker build -t cookie-chaos-django /Users/kesselbach/security-research/cookie-chaos-django
docker run --rm -p 8084:8084 -e DJANGO_SECRET_KEY=$(openssl rand -hex 32) --name cookie-chaos-django cookie-chaos-django
```

## Endpoints
- `/set-host?name=__Host-name&value=Carlos` — sets host-only cookie at `/`
- `/reflect?target=__Host-name` — reads from `request.COOKIES[target]`
- `/static/attacker.html` — gadget to set Unicode‑prefixed cookie with `Domain` and `Path=/`

## PoC (Unicode prefix)
1) Set victim cookie: `http://localhost:8084/set-host?name=__Host-name&value=Carlos`
2) Gadget: `http://localhost:8084/static/attacker.html`
   - CP: `2000` (U+2000) or try `85` (U+0085), `A0` (U+00A0)
   - Domain: `localhost`
   - Value: `ATTACKER`
3) Reflect: `http://localhost:8084/reflect?target=__Host-name`
   - Observe the value from `request.COOKIES` depending on Django/browser behavior.

## Notes/Defense
- Follow Django’s guidance on subdomains and session cookies.
- Prefer host‑only cookies; validate sessions against server state.

## Credits
- Research: PortSwigger (Zakhar Fedotkin)
