from urllib.parse import urlparse, urlencode
import json

from flask import Flask, request, redirect, make_response, render_template, send_from_directory


app = Flask(__name__)


# Insecure allow-list check mimicking the logic discussed in the article
# NOTE: This intentionally contains the protocol-agnostic hasSuffix issue.

def is_valid_origin(origin: str) -> bool:
    try:
        parsed = urlparse(origin)
    except Exception:
        return False

    if not parsed.scheme:
        return False

    origin_host_only = f"{parsed.scheme}://{parsed.hostname}" if parsed.hostname else ""

    # Intentionally vulnerable: allows any scheme for chromiumapp.org suffix
    if (
        origin_host_only == "http://localhost"
        or origin_host_only == "https://localhost"
        or origin_host_only == "http://127.0.0.1"
        or origin_host_only == "http://casdoor-authenticator"
        or (origin_host_only.endswith(".chromiumapp.org"))
    ):
        return True

    return False


@app.route("/")

def index():
    return render_template("index.html")


@app.route("/manifest.json")

def manifest():
    # PWA manifest registers a custom protocol that forwards to /call
    manifest_json = {
        "name": "Why Protocol Matters PWA",
        "short_name": "ProtLab",
        "start_url": "/",
        "display": "standalone",
        "icons": [],
        "protocol_handlers": [
            {"protocol": "web+slonser", "url": "/call?q=%s"}
        ],
    }
    resp = make_response(json.dumps(manifest_json))
    resp.headers["Content-Type"] = "application/manifest+json"
    return resp


@app.route("/install")

def install():
    # Page that links the manifest to allow install
    return render_template("install.html")


@app.route("/call")

def handler_call():
    # This simulates the PWA being invoked via protocol handler
    q = request.args.get("q", "")
    return render_template("call.html", q=q)


@app.route("/authorize")

def authorize():
    # Simulated OAuth authorization endpoint with weak redirect_uri origin validation
    client_id = request.args.get("client_id", "example-client")
    redirect_uri = request.args.get("redirect_uri")
    state = request.args.get("state", "state123")

    if not redirect_uri:
        return "missing redirect_uri", 400

    if not is_valid_origin(redirect_uri):
        return "invalid redirect origin", 400

    # Issue a fake code and redirect
    params = {"code": "demo-code-123", "state": state}
    sep = "&" if ("?" in redirect_uri) else "?"
    return redirect(f"{redirect_uri}{sep}{urlencode(params)}")


@app.route("/attack")

def attack():
    # Build the malicious redirect_uri using custom protocol with chromiumapp domain
    malicious_redirect = "web+slonser://z.chromiumapp.org"
    auth_url = (
        "/authorize?"
        + urlencode(
            {
                "client_id": "CLIENT_ID",
                "response_type": "code",
                "redirect_uri": malicious_redirect,
                "scope": "read",
                "state": "state_data",
            }
        )
    )
    return render_template("attack.html", auth_url=auth_url)


@app.route("/README")

def readme_route():
    return send_from_directory(".", "README.md")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)


