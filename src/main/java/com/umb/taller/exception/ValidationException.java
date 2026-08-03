package com.umb.taller.exception;

/**
 * Se lanza cuando un campo no cumple con las reglas de validación.
 *
 * Figura 16 - Autoría propia
 */
public class ValidationException extends DomainException {
    public ValidationException(String campo) {
        super("El campo '" + campo + "' no es válido");
    }
}
