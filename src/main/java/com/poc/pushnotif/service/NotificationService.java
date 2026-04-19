package com.poc.pushnotif.service;

import com.poc.pushnotif.dto.SendNotificationRequest;
import com.poc.pushnotif.dto.TrackStatusRequest;

public interface NotificationService {

    String sendNotification(SendNotificationRequest request);

    void trackStatus(TrackStatusRequest request);
}
