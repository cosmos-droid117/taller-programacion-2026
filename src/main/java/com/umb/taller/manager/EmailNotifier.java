package com.umb.taller.manager;

/**
 * Clase encargada exclusivamente del manejo de correos
 * (envío de bienvenida y validación de email).
 *
 * Figura 14 - Autoría propia
 */
public class EmailNotifier {
    public void enviarBienvenida(String email) {
        // lógica de envío de correo
    }

    public boolean validarEmail(String email) {
        return email != null && email.contains("@");
    }
}
