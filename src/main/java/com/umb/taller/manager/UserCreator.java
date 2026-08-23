package com.umb.taller.manager;

import com.umb.taller.model.Usuario;

/**
 * Clase responsable únicamente de la creación de usuarios.
 * Resultado de aplicar el principio de Responsabilidad Única (SRP)
 * sobre la God Class UserManager.
 *
 * Figura 13 - Autoría propia
 */
public class UserCreator {
    public Usuario crear(String nombre, String email) {
        return new Usuario(nombre, email);
    }
}
