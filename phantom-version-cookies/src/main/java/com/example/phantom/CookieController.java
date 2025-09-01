package com.example.phantom;

import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class CookieController {

    // Echo parsed cookies (Tomcat will apply legacy parsing if $Version=1 is present)
    @GetMapping(value = "/echo", produces = MediaType.TEXT_PLAIN_VALUE)
    public String echo(HttpServletRequest request) {
        Cookie[] cookies = request.getCookies();
        if (cookies == null || cookies.length == 0) {
            return "no cookies";
        }
        StringBuilder sb = new StringBuilder();
        for (Cookie c : cookies) {
            sb.append(c.getName()).append("=").append(c.getValue()).append("\n");
        }
        return sb.toString();
    }

    // Reflect $Path and $Domain unsafely from headers (INTENTIONALLY VULNERABLE)
    @GetMapping(value = "/reflect", produces = MediaType.TEXT_PLAIN_VALUE)
    public String reflect(
        HttpServletResponse response,
        @RequestHeader(value = "$Path", required = false) String legacyPath,
        @RequestHeader(value = "$Domain", required = false) String legacyDomain,
        @RequestParam(value = "name", defaultValue = "foo") String name,
        @RequestParam(value = "value", defaultValue = "bar") String value
    ) {
        Cookie cookie = new Cookie(name, value);
        if (legacyPath != null) {
            cookie.setPath(legacyPath);
        }
        if (legacyDomain != null) {
            cookie.setDomain(legacyDomain);
        }
        response.addCookie(cookie);
        return "set: " + name + "=" + value +
            (legacyPath != null ? "; Path=" + legacyPath : "") +
            (legacyDomain != null ? "; Domain=" + legacyDomain : "");
    }
}


