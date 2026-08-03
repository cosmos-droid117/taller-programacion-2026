package com.umb.taller.exception;

/**
 * Excepción base abstracta del dominio de la aplicación.
 *
 * Figura 16 - Autoría propia
 */
public abstract class AppException extends Exception {
    public AppException(String mensaje) {
        super(mensaje);
    }
}
