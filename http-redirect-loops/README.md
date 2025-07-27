# HTTP Redirect Loops & SSRF Vulnerability Demo

This project demonstrates a server-side request forgery (SSRF) vulnerability involving HTTP redirect loops, inspired by the research described in [Assetnote's Novel SSRF Technique Involving HTTP Redirect Loops](https://slcyber.io/assetnote-security-research-center/novel-ssrf-technique-involving-http-redirect-loops/).

## Overview

The included `vulnerable_server.py` is a simple Flask web application that exposes an endpoint `/fetch-url`. This endpoint fetches a user-supplied URL and returns information about the HTTP response and any redirects that occurred. The server is intentionally designed to mimic real-world SSRF-prone logic, including error states that can leak sensitive information under certain redirect conditions.

## How It Works

- **Endpoint:** `/fetch-url?url=<target_url>`
- The server fetches the provided URL using Python's `requests` library, following redirects by default.
- It tracks the full redirect chain and the number of redirects.
- If the number of redirects exceeds 5, the server simulates an application error state and leaks the full redirect chain and the final HTTP response body (even if it is sensitive).
- If the response is valid JSON and there are 5 or fewer redirects, it returns the parsed data.
- If the response is not valid JSON, it returns a generic error without leaking the body.

## SSRF Redirect Loop Technique

This server is designed to help demonstrate a novel SSRF exploitation technique:

- **Redirect Loop:** By crafting a chain of HTTP redirects (potentially with varying status codes), an attacker can trigger the server's error state that leaks the full redirect chain and the final response body.
- **Practical Impact:** In real-world scenarios, this can be used to exfiltrate sensitive data (such as cloud metadata credentials) from otherwise blind SSRF vulnerabilities, by forcing the application to reveal the full HTTP response after a certain number of redirects.
- **Reference:** See the [Assetnote research article](https://slcyber.io/assetnote-security-research-center/novel-ssrf-technique-involving-http-redirect-loops/) for a detailed explanation and real-world exploitation example.

## Example Usage

1. **Start the server:**
   ```bash
   python3 vulnerable_server.py
   ```

2. **Trigger the SSRF logic:**
   - Host a redirect loop server (see the Flask example in the referenced article) that issues a series of HTTP redirects, incrementing the status code or redirect count.
   - Make a request to the vulnerable server:
     ```bash
     curl 'http://localhost:5000/fetch-url?url=http://<redirect-loop-server>/start'
     ```
   - If the redirect chain is long enough (>5), the server will return the full redirect chain and the final response body.

## Flask Redirect Loop Example

Here is a minimal Flask app that creates a redirect loop, as described in the article:

```python
from flask import Flask, redirect, request
app = Flask(__name__)

@app.route('/redir')
def redir():
    count = int(request.args.get('count', 0)) + 1
    if count >= 10:
        return redirect('http://example.com', code=302)
    return redirect(f'/redir?count={count}', code=302)

@app.route('/start')
def start():
    return redirect('/redir', code=302)

if __name__ == '__main__':
    app.run(port=8000)
```

## Security Implications

- This project is for educational and research purposes only.
- The logic in `vulnerable_server.py` is intentionally insecure to demonstrate how SSRF vulnerabilities can be exploited using redirect loops.
- **Do not deploy this code in production.**

## References
- [Novel SSRF Technique Involving HTTP Redirect Loops (Assetnote)](https://slcyber.io/assetnote-security-research-center/novel-ssrf-technique-involving-http-redirect-loops/) 