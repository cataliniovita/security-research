from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/fetch-url')
def fetch_url():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing url parameter'}), 400
    try:
        # Follow redirects (default: True)
        resp = requests.get(url, timeout=5)
        redirect_chain = []
        for r in resp.history:
            redirect_chain.append({
                'status_code': r.status_code,
                'url': r.url,
                'headers': dict(r.headers)
            })
        num_redirects = len(resp.history)
        if num_redirects > 5:
            # Simulate the application error state: leak the full redirect chain and final response
            return jsonify({
                'error': 'NetworkException: Too many redirects or error state',
                'status_code': resp.status_code,
                'headers': dict(resp.headers),
                'body': resp.text,
                'num_redirects': num_redirects,
                'redirect_chain': redirect_chain
            }), 500
        else:
            try:
                data = resp.json()
                return jsonify({
                    'data': data,
                    'status_code': resp.status_code,
                    'headers': dict(resp.headers),
                    'num_redirects': num_redirects,
                    'redirect_chain': redirect_chain
                })
            except json.JSONDecodeError:
                # Only return a generic error, do NOT leak the body
                return jsonify({
                    'error': 'Exception: Invalid JSON',
                    'status_code': resp.status_code,
                    'headers': dict(resp.headers),
                    'num_redirects': num_redirects,
                    'redirect_chain': redirect_chain
                }), 400
    except requests.exceptions.RequestException as e:
        # Network error, leak error details
        return jsonify({'error': f'NetworkException: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True) 