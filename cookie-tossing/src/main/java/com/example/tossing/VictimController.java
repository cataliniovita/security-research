package com.example.tossing;

import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
public class VictimController {

    // Simple home to help manual testing
    @GetMapping(value = "/", produces = MediaType.TEXT_HTML_VALUE)
    public String index() {
        return """
                <html><body>
                <h2>Cookie Tossing Demo</h2>
                <p><a href='/login?user=victim'>Login as victim</a></p>
                <p><a href='/api/profile'>Call /api/profile (uses SESSION cookie)</a></p>
                </body></html>
                """;
    }

    // Victim login sets a host-only cookie SESSION=<user>-session scoped to '/'
    @GetMapping("/login")
    public String login(@RequestParam(defaultValue = "victim") String user, HttpServletResponse response) {
        Cookie c = new Cookie("SESSION", user + "-session");
        c.setPath("/");
        // Important: host-only (no domain attribute)
        c.setHttpOnly(true);
        c.setSecure(false);
        response.addCookie(c);
        return "Logged in as " + user + ". SESSION=" + URLEncoder.encode(c.getValue(), StandardCharsets.UTF_8) + " (host-only)";
    }

    // Vulnerable API: picks the FIRST occurrence of name=SESSION as it appears in the Cookie header
    // Simulates apps that trust cookie order and do not validate session store
    @GetMapping(value = "/api/profile", produces = MediaType.APPLICATION_JSON_VALUE)
    public Map<String, Object> profile(@RequestHeader(value = "Cookie", required = false) String cookieHeader,
                                       HttpServletRequest request) {
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("path", request.getRequestURI());
        out.put("cookieHeader", cookieHeader == null ? "" : cookieHeader);

        String chosenSession = null;
        if (cookieHeader != null) {
            // Very naive split on ';' then '=' and trim. Keeps original order.
            for (String pair : cookieHeader.split(";")) {
                String[] kv = pair.trim().split("=", 2);
                if (kv.length == 2) {
                    String name = kv[0];
                    String value = kv[1];
                    if ("SESSION".equals(name)) {
                        chosenSession = value;
                        break; // take the first one only (attacker can win with path-specific precedence)
                    }
                }
            }
        }

        out.put("chosenSession", chosenSession == null ? "" : chosenSession);

        // Fake profile derived from chosen session value
        String user = chosenSession == null ? "anonymous" : chosenSession.replace("-session", "");
        out.put("user", user);
        out.put("message", "Hello, " + user + "!");

        // Echo also parsed cookies as the server sees (for transparency)
        Map<String, String> parsed = request.getCookies() == null ? Map.of() : Arrays.stream(request.getCookies())
                .collect(Collectors.toMap(Cookie::getName, Cookie::getValue));
        out.put("serverParsedCookies", parsed);

        return out;
    }
}



