package com.umb.taller.manager;

/**
 * God Class original: concentra múltiples responsabilidades
 * (creación de usuarios, envío de correos, generación de reportes,
 * validación de email y logging) en una sola clase.
 *
 * Viola el principio de Responsabilidad Única (SRP) y el principio
 * de Inversión de Dependencias (DIP).
 *
 * Figura 12 - Autoría propia
 */
public class UserManager {
    createUser(); sendEmail(); generateReport(); validateEmail(); logActivity();
}
