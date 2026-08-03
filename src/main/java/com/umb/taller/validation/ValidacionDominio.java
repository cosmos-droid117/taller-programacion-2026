package com.umb.taller.validation;

/**
 * Interfaz funcional genérica para validaciones del dominio.
 *
 * Figura 18 - Autoría propia
 */
@FunctionalInterface
public interface ValidacionDominio<T> {
    boolean validar(T entidad);
}
