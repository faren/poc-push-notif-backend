package com.poc.pushnotif.exception;

public class FcmException extends RuntimeException {

    public FcmException(String message, Throwable cause) {
        super(message, cause);
    }
}
