package com.hotelreservation.auth.controller;

import com.hotelreservation.auth.dto.ApiResponse;
import com.hotelreservation.auth.dto.SigninRequest;
import com.hotelreservation.auth.dto.SignupRequest;
import com.hotelreservation.auth.entity.User;
import com.hotelreservation.auth.service.AuthService;
import com.hotelreservation.auth.util.JwtUtil;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/auth")
@CrossOrigin(origins = "*")
public class AuthController {
    
    @Autowired
    private AuthService authService;
    
    @Autowired
    private JwtUtil jwtUtil;
    
    @PostMapping("/signup")
    public ResponseEntity<ApiResponse<Map<String, Object>>> signup(@Valid @RequestBody SignupRequest request) {
        try {
            Map<String, Object> userData = authService.signup(request);
            return ResponseEntity.status(HttpStatus.CREATED)
                    .body(ApiResponse.success("User registered successfully", userData));
        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                    .body(ApiResponse.error(e.getMessage(), "REGISTRATION_FAILED"));
        }
    }
    
    @PostMapping("/signin")
    public ResponseEntity<ApiResponse<Map<String, Object>>> signin(@Valid @RequestBody SigninRequest request) {
        try {
            Map<String, Object> authData = authService.signin(request);
            return ResponseEntity.ok(ApiResponse.success("Login successful", authData));
        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(ApiResponse.error("Invalid email or password", "INVALID_CREDENTIALS"));
        }
    }
    
    @GetMapping("/validate")
    public ResponseEntity<ApiResponse<Map<String, Object>>> validateToken(@RequestHeader("Authorization") String authHeader) {
        try {
            String token = authHeader.substring(7); // Remove "Bearer "
            
            if (!jwtUtil.validateToken(token)) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                        .body(ApiResponse.error("Invalid or expired token", "INVALID_TOKEN"));
            }
            
            String email = jwtUtil.extractEmail(token);
            User user = authService.getUserByEmail(email);
            
            Map<String, Object> response = new HashMap<>();
            response.put("userId", user.getId().toString());
            response.put("username", user.getUsername());
            response.put("email", user.getEmail());
            response.put("role", user.getRole().name());
            
            return ResponseEntity.ok(ApiResponse.success("Token is valid", response));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(ApiResponse.error("Invalid or expired token", "INVALID_TOKEN"));
        }
    }
    
    @GetMapping("/profile")
    public ResponseEntity<ApiResponse<Map<String, Object>>> getProfile(@RequestHeader("Authorization") String authHeader) {
        try {
            String token = authHeader.substring(7);
            String email = jwtUtil.extractEmail(token);
            User user = authService.getUserByEmail(email);
            
            Map<String, Object> profile = new HashMap<>();
            profile.put("userId", user.getId().toString());
            profile.put("username", user.getUsername());
            profile.put("email", user.getEmail());
            profile.put("firstName", user.getFirstName());
            profile.put("lastName", user.getLastName());
            profile.put("dateOfBirth", user.getDateOfBirth());
            profile.put("role", user.getRole().name());
            profile.put("memberSince", user.getCreatedAt());
            profile.put("totalBookings", user.getTotalBookings());
            profile.put("totalReviews", user.getTotalReviews());
            profile.put("isVerified", user.getIsVerified());
            
            return ResponseEntity.ok(ApiResponse.success("Profile retrieved successfully", profile));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(ApiResponse.error("Invalid token", "INVALID_TOKEN"));
        }
    }
    
    @GetMapping("/health")
    public ResponseEntity<ApiResponse<Map<String, Object>>> health() {
        Map<String, Object> health = new HashMap<>();
        health.put("service", "authentication-service");
        health.put("status", "UP");
        health.put("database", "CONNECTED");
        health.put("version", "1.0.0");
        
        return ResponseEntity.ok(ApiResponse.success("Authentication service is healthy", health));
    }
}
