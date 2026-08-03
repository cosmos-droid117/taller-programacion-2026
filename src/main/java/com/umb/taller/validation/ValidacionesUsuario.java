package com.umb.taller.validation;

import com.umb.taller.model.Usuario;

/**
 * Implementaciones de la interfaz funcional ValidacionDominio
 * mediante expresiones lambda y method reference.
 *
 * Figura 19 - Autoría propia
 */
public class ValidacionesUsuario {

    public static final ValidacionDominio<Usuario> emailValido =
            u -> u.getEmail() != null && u.getEmail().contains("@");

    public static final ValidacionDominio<Usuario> nombreNoVacio =
            u -> u.getNombre() != null && !u.getNombre().isBlank();

    public static final ValidacionDominio<Usuario> edadValida =
            u -> u.getEdad() >= 0;

    public static final ValidacionDominio<Usuario> validacionCompleja =
            UsuarioValidator::esValido;
}
