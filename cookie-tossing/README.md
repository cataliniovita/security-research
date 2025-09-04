# Cookie Tossing Demo (path specificity precedence)

Based on Thomas Houhou's research on cookie tossing, path specificity, and duplicate cookie precedence.

- Article: [Cookie Tossing: Self-XSS Exploitation, Multi-Step Process Hijacking, and Targeted Action Poisoning](https://www.thomashouhou.com/post/cookie-tossing-attacks/)

## Build & Run (Docker)
```bash
docker build -t cookie-tossing /Users/kesselbach/security-research/cookie-tossing
docker run --rm -p 8082:8082 --name cookie-tossing cookie-tossing
```

## Endpoints
- `/login?user=victim` — sets a host-only `SESSION=victim-session` at path `/` (HttpOnly=true)
- `/api/profile` — vulnerable: picks the FIRST `SESSION=` from the raw `Cookie` header (trusts order)
- `/attacker.html` — gadget to set `SESSION` with `domain=<parent>` and specific `path` to win precedence

## Why vulnerable?
When duplicate cookies with the same name are present, browsers send both. Many apps use the first one from the `Cookie` header without validating its source. The browser orders cookies by path specificity first, then by age. By injecting a `SESSION` cookie for the parent domain with a more specific path (e.g., `/api`), the attacker ensures their cookie appears before the victim's host-only cookie for requests to `/api/*`.

This mirrors the behavior described in the article above.

## Local PoC
The cleanest demonstration is with two hostnames that share a parent domain. For simplicity on localhost, many browsers still allow `domain=localhost` for testing; if yours doesn't, use `/etc/hosts` to create a parent domain.

### Option A: Single host quick demo
1) Start the app and visit:
   - http://localhost:8082/login
2) Open http://localhost:8082/attacker.html and set:
   - Parent domain: `localhost`
   - Attacker session value: `attacker-session`
   - Specific path: `/api`
   Then click "Toss Cookie".
3) Visit http://localhost:8082/api/profile
   - Observe `chosenSession` is `attacker-session`, even though the server also has a host-only `SESSION=victim-session`.

### Option B: Two subdomains (closer to real-world)
Edit `/etc/hosts`:
```bash
127.0.0.1 victim.local attacker.local
```
Run the app and use the same port.

- Victim flow sets a host-only cookie on `victim.local`:
  1) Visit `http://victim.local:8082/login?user=victim`
  2) Confirm `SESSION=victim-session` is set (host-only, no `domain=`)
- Attacker gadget on a sibling host injects a parent-domain cookie:
  3) Visit `http://attacker.local:8082/attacker.html`
     - Parent domain: `local`
     - Attacker session value: `attacker-session`
     - Specific path: `/api`
     Click Toss
- Trigger target endpoint on the victim host:
  4) Visit `http://victim.local:8082/api/profile`
  5) Observe JSON shows `chosenSession` = `attacker-session` and raw `cookieHeader` lists the attacker cookie before the victim one for the `/api/*` path.

Notes:
- Some browsers may not accept `domain=local`. If so, choose a parent like `mydemo.test` in `/etc/hosts`:
```bash
127.0.0.1 victim.mydemo.test attacker.mydemo.test
```
Use `domain=mydemo.test` in the attacker gadget.

## Defense ideas (from the article)
- Bind session cookies to host-only and exact path when feasible.
- Validate session identifiers against the server-side session store and ignore duplicates by order; pick by store validation, not by header order.
- For multi-host environments, avoid shared higher-order parent domains for user-controllable subdomains.

## Credits
- Research and inspiration: [Thomas Houhou's post](https://www.thomashouhou.com/post/cookie-tossing-attacks/)
