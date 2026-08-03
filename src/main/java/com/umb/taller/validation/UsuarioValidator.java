package com.umb.taller.validation;

import com.umb.taller.model.Usuario;

/**
 * Clase con lógica de validación compleja de Usuario, referenciada
 * mediante method reference (UsuarioValidator::esValido) en Figura 19.
 */
public class UsuarioValidator {

    public static boolean esValido(Usuario usuario) {
        return usuario != null
                && usuario.getNombre() != null && !usuario.getNombre().isBlank()
                && usuario.getEmail() != null && usuario.getEmail().contains("@")
                && usuario.getEdad() >= 0;
    }
}
