package com.poc.pushnotif.dto;

import com.poc.pushnotif.enums.NotificationCategory;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record SendNotificationRequest(
        @NotBlank(message = "targetToken must not be blank") String targetToken,
        @NotNull(message = "category must not be null") NotificationCategory category,
        @NotBlank(message = "title must not be blank") String title,
        @NotBlank(message = "body must not be blank") String body,
        @Valid @NotNull(message = "metadata must not be null") NotificationMetadata metadata
) {}
