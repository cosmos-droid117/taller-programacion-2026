package com.umb.taller.repository;

import java.util.List;

/**
 * Interfaz genérica de repositorio, base para aplicar el principio
 * de Inversión de Dependencias (DIP).
 *
 * Figura 20 - Autoría propia
 */
public interface Repository<T, ID> {
    T findById(ID id);
    T save(T entity);
    void deleteById(ID id);
    List<T> findAll();
}
