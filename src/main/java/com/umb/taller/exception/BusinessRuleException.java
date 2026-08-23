package com.umb.taller.exception;

/**
 * Se lanza cuando se incumple una regla de negocio del dominio.
 *
 * Figura 16 - Autoría propia
 */
public class BusinessRuleException extends DomainException {
    public BusinessRuleException(String regla) {
        super("Regla de negocio violada: " + regla);
    }
}
