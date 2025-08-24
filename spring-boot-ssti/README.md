# Spring Boot 3.3.4 Thymeleaf SSTI Demo (Docker)

This reproduces the Referer double-evaluation bug pattern described here: https://modzero.com/en/blog/spring_boot_ssti/

## Build and Run

```bash
# From repo root
docker build -t spring-ssti /Users/kesselbach/security-research/spring-boot-ssti

# Run
docker run --rm -p 8081:8081 --name spring-ssti spring-ssti
```

## Test / Exploit

Send a crafted Referer header, e.g., to evaluate `${7*7}`:

```bash
curl -s -H "Referer='+${7*7}+'" http://localhost:8081/
```

If vulnerable, the rendered text should contain `49`.

Note: This is intentionally insecure for research purposes; do not deploy to production.
