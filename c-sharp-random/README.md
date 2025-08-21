# C# Random Vulnerability Reproduction (Dockerized)

This demo reproduces predictable token generation caused by per-request time-seeded `new Random()` as discussed by Doyensec: [Trivial C# Random Exploitation](https://blog.doyensec.com/2025/08/19/trivial-exploit-on-C-random.html).

## Build and Run (Docker)

```bash
# From repo root
cd /security-research

# Build image
docker build -t csharp-random-vuln ./c-sharp-random

# Run container on port 8080
docker run --rm -p 8080:8080 --name csharp-random-vuln csharp-random-vuln
```

## Test the vulnerable endpoint

Open:

- http://localhost:8080/password-reset

Optional query parameters:

- `min` and `max` to set the range for `Random.Next(min, max)`

Examples:

- `http://localhost:8080/password-reset?min=100000&max=999999`

## Reproducing the timing issue

Because the endpoint constructs `new Random()` per request, which defaults to a time-based seed, two requests created within the same ~1ms window can share the same seed and produce the same token. Use a race/repeater tool (e.g., Burp Repeater with a race group) to send two requests closely together and observe duplicate tokens.

## Notes

- This is intentionally insecure and for research only. Do not deploy to production.
- Correct fix: use `System.Security.Cryptography.RandomNumberGenerator` or `RandomNumberGenerator.GetInt32` for cryptographically secure randomness.
