package com.umb.taller.exception;

/**
 * Excepción intermedia para errores propios del dominio.
 *
 * Figura 16 - Autoría propia
 */
public class DomainException extends AppException {
    public DomainException(String mensaje) {
        super(mensaje);
    }
}
