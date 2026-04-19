package com.poc.pushnotif.controller;

import com.poc.pushnotif.dto.ApiResponse;
import com.poc.pushnotif.dto.SendNotificationRequest;
import com.poc.pushnotif.dto.TrackStatusRequest;
import com.poc.pushnotif.service.NotificationService;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/notifications")
public class NotificationController {

    private static final Logger log = LoggerFactory.getLogger(NotificationController.class);

    private final NotificationService notificationService;

    public NotificationController(NotificationService notificationService) {
        this.notificationService = notificationService;
    }

    @PostMapping("/send")
    public ResponseEntity<ApiResponse<Map<String, String>>> send(
            @Valid @RequestBody SendNotificationRequest request) {

        log.info("Received /send — messageId={}, category={}",
                request.metadata().messageId(), request.category());

        String fcmResponseId = notificationService.sendNotification(request);

        return ResponseEntity.ok(ApiResponse.ok(
                "Notification sent successfully",
                Map.of(
                        "messageId",     request.metadata().messageId(),
                        "fcmResponseId", fcmResponseId
                )
        ));
    }

    @PostMapping("/track-status")
    public ResponseEntity<ApiResponse<Void>> trackStatus(
            @Valid @RequestBody TrackStatusRequest request) {

        log.info("[TRACK-STATUS] Request arrived — messageId={}, status={}",
                request.messageId(), request.status());

        notificationService.trackStatus(request);

        return ResponseEntity.ok(ApiResponse.ok("Status tracked: " + request.status(), null));
    }
}
