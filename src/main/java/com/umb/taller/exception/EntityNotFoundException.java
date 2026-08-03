package com.umb.taller.exception;

/**
 * Se lanza cuando no se encuentra una entidad con el id solicitado.
 *
 * Figura 16 - Autoría propia
 */
public class EntityNotFoundException extends DomainException {
    public EntityNotFoundException(String id) {
        super("No se encontró la entidad con id: " + id);
    }
}
