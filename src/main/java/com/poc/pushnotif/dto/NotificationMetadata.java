package com.poc.pushnotif.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record NotificationMetadata(
        @NotBlank(message = "messageId must not be blank") String messageId,
        @NotNull(message = "timestamp must not be null") Long timestamp
) {}
