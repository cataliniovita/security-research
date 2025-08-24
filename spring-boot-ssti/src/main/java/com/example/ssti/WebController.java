package com.example.ssti;

import jakarta.servlet.http.HttpServletRequest;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class WebController {

    @GetMapping("/")
    public String index(HttpServletRequest request, Model model) {
        String referer = request.getHeader("Referer");
        if (referer == null) {
            referer = "";
        }
        // Intentionally reflect the Referer into the template model
        model.addAttribute("Referer", referer);
        return "index";
    }
}


