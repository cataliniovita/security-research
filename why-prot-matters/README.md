# Why Protocol Matters - Vulnerable Lab

This lab demonstrates a protocol-handler based origin validation flaw inspired by the write-up “Why Protocol Matters: Evil PWA Attack on Casdoor”.

Reference: [Blog post](https://blog.slonser.info/posts/why-protocol-matters/)

## Summary

- The vulnerable check incorrectly allows any custom protocol as long as the host ends with `.chromiumapp.org`.
- A Progressive Web App (PWA) registers a custom protocol handler via `protocol_handlers` in `manifest.json`.
- An OAuth-like `/authorize` endpoint validates `redirect_uri` via a weak `is_valid_origin` check that uses suffix matching without enforcing `https://`.
- The attacker uses a `web+slonser://z.chromiumapp.org` redirect to capture the authorization code via the PWA handler route.

## Components

- `app.py`: Flask app exposing:
  - `/manifest.json`: PWA manifest registering `web+slonser` protocol → `/call?q=%s`
  - `/install`: Page to install the PWA
  - `/authorize`: Insecure OAuth-like endpoint
  - `/attack`: Convenience page to trigger the attack flow
  - `/call`: Protocol handler landing page (captures `q`)

## Run (local)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
FLASK_APP=app.py flask run --host 0.0.0.0 --port 8080
```

Then visit:
- http://localhost:8080/install — install the PWA
- http://localhost:8080/attack — trigger the flow

## Expected Behavior

1. Install the PWA (registering the custom protocol `web+slonser`).
2. Visit `/attack` and click the link to start authorization.
3. The server validates `redirect_uri` using suffix match on `.chromiumapp.org` but does not require `https://`.
4. Browser resolves `web+slonser://z.chromiumapp.org` to the PWA handler `/call?q=...`.
5. The authorization code appears on the handler page indicating code exfiltration.

## Intended Vulnerability (Do not deploy to prod)

The `is_valid_origin` function intentionally mirrors the flaw:

- Accepts `*.chromiumapp.org` regardless of protocol.
- Allows arbitrary custom schemes like `web+slonser://`.

A more robust check would also require `https://` for the `.chromiumapp.org` suffix, e.g. enforce scheme before suffix, as suggested by the blog:

```go
(strings.HasSuffix(originHostOnly, ".chromiumapp.org") && strings.HasPrefix(originHostOnly, "https://"))
```

## Legal/Ethical Notice

For educational and authorized testing only. Do not misuse. See the reference for context and details: [Why Protocol Matters](https://blog.slonser.info/posts/why-protocol-matters/).
