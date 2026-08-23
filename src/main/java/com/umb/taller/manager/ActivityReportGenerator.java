package com.umb.taller.manager;

import com.umb.taller.model.Usuario;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Clase encargada exclusivamente de generar reportes de actividad.
 *
 * Figura 15 - Autoría propia
 */
public class ActivityReportGenerator {

    private static final Logger log = LoggerFactory.getLogger(ActivityReportGenerator.class);

    public String generarReporte(Usuario usuario) {
        log.info("Generando reporte para {}", usuario.getNombre());
        return "Reporte de actividad: " + usuario.getNombre();
    }
}
