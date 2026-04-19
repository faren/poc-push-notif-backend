package com.poc.pushnotif.service;

import com.google.firebase.messaging.FirebaseMessaging;
import com.google.firebase.messaging.FirebaseMessagingException;
import com.google.firebase.messaging.Message;
import com.google.firebase.messaging.Notification;
import com.poc.pushnotif.dto.SendNotificationRequest;
import com.poc.pushnotif.dto.TrackStatusRequest;
import com.poc.pushnotif.enums.NotificationStatus;
import com.poc.pushnotif.exception.FcmException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class NotificationServiceImpl implements NotificationService {

    private static final Logger log = LoggerFactory.getLogger(NotificationServiceImpl.class);

    private final FirebaseMessaging firebaseMessaging;

    public NotificationServiceImpl(FirebaseMessaging firebaseMessaging) {
        this.firebaseMessaging = firebaseMessaging;
    }

    @Override
    public String sendNotification(SendNotificationRequest request) {
        String messageId = request.metadata().messageId();
        String category  = request.category().name();

        // Log SENT before calling FCM — guaranteed even if FCM throws
        logStatus(NotificationStatus.SENT, category, messageId);

        Message fcmMessage = Message.builder()
                .setToken(request.targetToken())
                .setNotification(
                        Notification.builder()
                                .setTitle(request.title())
                                .setBody(request.body())
                                .build()
                )
                // Data payload: Flutter reads these via RemoteMessage.data
                .putData("messageId", messageId)
                .putData("category",  category)
                .putData("timestamp", String.valueOf(request.metadata().timestamp()))
                .build();

        try {
            String fcmResponseId = firebaseMessaging.send(fcmMessage);
            logStatus(NotificationStatus.DELIVERED, category, messageId);
            log.info("FCM accepted message. fcmResponseId={}", fcmResponseId);
            return fcmResponseId;

        } catch (FirebaseMessagingException e) {
            log.error("FCM send failed for messageId={}, category={}: {} (errorCode={})",
                    messageId, category, e.getMessage(), e.getMessagingErrorCode());
            throw new FcmException("FCM send failed: " + e.getMessage(), e);
        }
    }

    @Override
    public void trackStatus(TrackStatusRequest request) {
        logStatus(request.status(), request.category().name(), request.messageId());
    }

    private void logStatus(NotificationStatus status, String category, String id) {
        log.info("[NOTIF-LOG] status: {}, category: {}, id: {}", status, category, id);
    }
}
