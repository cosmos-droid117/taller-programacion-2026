package com.umb.taller.service;

import com.umb.taller.exception.EntityNotFoundException;
import com.umb.taller.model.Usuario;
import com.umb.taller.repository.Repository;

/**
 * Servicio que depende de la abstracción Repository y no de una
 * implementación concreta, cumpliendo con el principio de Inversión
 * de Dependencias (DIP).
 *
 * Figura 22 - Autoría propia
 */
public class UsuarioService {

    private final Repository<Usuario, String> repository;

    public UsuarioService(Repository<Usuario, String> repository) {
        this.repository = repository;
    }

    public Usuario buscar(String id) throws EntityNotFoundException {
        Usuario u = repository.findById(id);
        if (u == null) throw new EntityNotFoundException(id);
        return u;
    }
}
