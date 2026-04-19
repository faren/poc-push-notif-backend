package com.poc.pushnotif.dto;

import com.poc.pushnotif.enums.NotificationCategory;
import com.poc.pushnotif.enums.NotificationStatus;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record TrackStatusRequest(
        @NotBlank(message = "messageId must not be blank") String messageId,
        @NotNull(message = "status must not be null") NotificationStatus status,
        @NotNull(message = "category must not be null") NotificationCategory category
) {}
