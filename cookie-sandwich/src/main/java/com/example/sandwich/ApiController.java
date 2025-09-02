package com.example.sandwich;

import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ApiController {

    // Sets an HttpOnly session cookie to simulate a protected cookie
    @GetMapping(value = "/set-session", produces = MediaType.TEXT_PLAIN_VALUE)
    public String setSession(HttpServletResponse response) {
        Cookie c = new Cookie("PHPSESSID", "secret-session");
        c.setHttpOnly(true);
        c.setPath("/");
        response.addCookie(c);
        return "ok";
    }

    // Reflects the 'session' cookie from request into JSON, overwriting any URL param
    // This is intentionally vulnerable: it mimics analytics that reflect cookie value
    @GetMapping(value = "/json", produces = MediaType.APPLICATION_JSON_VALUE)
    public String json(@RequestParam(value = "session", required = false) String ignored,
                       HttpServletRequest request, HttpServletResponse response) {
        String reflected = null;
        Cookie[] cookies = request.getCookies();
        if (cookies != null) {
            for (Cookie ck : cookies) {
                if ("session".equals(ck.getName())) {
                    reflected = ck.getValue();
                }
            }
        }
        if (reflected == null) {
            reflected = "";
        }
        response.setHeader("Access-Control-Allow-Origin", request.getHeader("Origin") != null ? request.getHeader("Origin") : "*");
        response.setHeader("Vary", "Origin");
        response.setHeader("Access-Control-Allow-Credentials", "true");
        return "{\"session\":\"" + reflected.replace("\"", "\\\"") + "\"}";
    }
}


