package com.umb.taller.repository;

import com.umb.taller.model.Usuario;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Implementación concreta del repositorio de Usuario (en memoria).
 *
 * Figura 21 - Autoría propia
 */
public class UsuarioRepositoryImpl implements Repository<Usuario, String> {

    private final Map<String, Usuario> datos = new HashMap<>();

    public Usuario findById(String id) {
        return datos.get(id);
    }

    public Usuario save(Usuario u) {
        datos.put(u.getId(), u);
        return u;
    }

    public void deleteById(String id) {
        datos.remove(id);
    }

    public List<Usuario> findAll() {
        return new ArrayList<>(datos.values());
    }
}
