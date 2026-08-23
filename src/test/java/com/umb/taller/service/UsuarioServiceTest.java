package com.umb.taller.service;

import com.umb.taller.exception.BusinessRuleException;
import com.umb.taller.exception.DomainException;
import com.umb.taller.exception.EntityNotFoundException;
import com.umb.taller.exception.ValidationException;
import com.umb.taller.exception.AppException;
import com.umb.taller.model.Usuario;
import com.umb.taller.repository.Repository;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

/**
 * Pruebas unitarias con JUnit 5 y AssertJ.
 *
 * Figura 23 - Autoría propia
 */
class UsuarioServiceTest {

    @Test
    void deberiaEncontrarUsuarioExistente() throws EntityNotFoundException {
        Repository<Usuario, String> repo = Mockito.mock(Repository.class);
        Usuario u = new Usuario("1", "Samuel", "samuel@umb.edu.co");
        Mockito.when(repo.findById("1")).thenReturn(u);
        UsuarioService service = new UsuarioService(repo);
        assertThat(service.buscar("1")).isEqualTo(u);
    }

    @Test
    void deberiaLanzarEntityNotFoundExceptionSiNoExiste() {
        Repository<Usuario, String> repo = Mockito.mock(Repository.class);
        Mockito.when(repo.findById("999")).thenReturn(null);
        UsuarioService service = new UsuarioService(repo);
        assertThatThrownBy(() -> service.buscar("999"))
            .isInstanceOf(EntityNotFoundException.class);
    }

    @Test
    void validationExceptionDebeGuardarMensaje() {
        var ex = new ValidationException("email");
        assertThat(ex.getMessage()).contains("email");
    }

    @Test
    void businessRuleExceptionDebeGuardarMensaje() {
        var ex = new BusinessRuleException("edad mínima");
        assertThat(ex.getMessage()).contains("edad mínima");
    }

    @Test
    void jerarquiaDeExcepcionesDebeSerCorrecta() {
        var ex = new EntityNotFoundException("1");
        assertThat(ex).isInstanceOf(DomainException.class);
        assertThat(ex).isInstanceOf(AppException.class);
    }
}
