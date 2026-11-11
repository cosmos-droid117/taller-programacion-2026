# Sistema Bancario Web

Este proyecto consiste en el desarrollo de una aplicación web de simulación bancaria implementada en el lado del cliente (client-side) utilizando tecnologías estándar: HTML5, CSS3 y JavaScript (ES6). Su propósito es modelar operaciones financieras básicas bajo un diseño orientado a objetos.

---

## Características y Requerimientos Funcionales

El sistema cumple con las siguientes operaciones esenciales:

1. **Creación de Cuentas:** Permite registrar cuentas nuevas especificando un número único, el nombre del titular y un saldo inicial no negativo.
2. **Depósitos:** Incrementa el saldo de una cuenta existente al ingresar un monto positivo mayor a cero.
3. **Retiros:** Permite extraer fondos de una cuenta, validando que el monto solicitado sea mayor a cero y no supere el saldo disponible.
4. **Consulta de Saldo e Historial:** Muestra de forma detallada el saldo actual y un registro cronológico de los movimientos realizados (aperturas, depósitos y retiros).

### Reglas de Negocio y Restricciones
* El número de cuenta debe ser único dentro del sistema.
* El nombre del titular es obligatorio.
* El saldo inicial y los montos de operación no pueden ser negativos ni iguales a cero (excepto el saldo inicial que puede ser cero).
* Gestión de excepciones mediante bloques `try/catch` para reportar errores visuales en la interfaz sin interrumpir la ejecución del programa.
* Persistencia local de los datos utilizando `localStorage` para conservar las cuentas tras recargar la página.

---

## Arquitectura y Lógica del Sistema

El código se encuentra estructurado bajo un paradigma orientado a objetos para desacoplar la lógica del negocio de la interfaz de usuario:

* **Clase `Cuenta`:** Modela individualmente cada cuenta bancaria. Almacena las propiedades de número, titular, saldo y un arreglo de movimientos. Implementa los métodos `depositar(monto)`, `retirar(monto)` y `consultarSaldo()`, encargados de aplicar las validaciones correspondientes.
* **Clase `Banco`:** Administra el conjunto total de cuentas. Implementa los métodos `crearCuenta(...)` y `buscarCuenta(...)`, además de gestionar la persistencia de los datos en el almacenamiento local del navegador (`localStorage`).
* **Controladores de Eventos:** Capturan las interacciones de los formularios en el DOM, ejecutan las acciones requeridas sobre las clases de negocio e interactúan dinámicamente con la interfaz para mostrar resultados o notificar errores.

---

## Estructura del Proyecto

El proyecto está compuesto por un único archivo autocontenido para facilitar su despliegue y ejecución:

* `index.html`: Contiene la estructura semántica de la interfaz, las hojas de estilo en cascada integradas (diseño minimalista en modo oscuro) y toda la lógica en JavaScript.

---

## Instrucciones de Ejecución

Al tratarse de una solución desarrollada enteramente del lado del cliente, **no requiere la instalación de servidores web, Node.js ni bases de datos externas**.

1. Clone el repositorio o descargue el archivo fuente del proyecto (`index.html`).
2. Abra el archivo `index.html` utilizando cualquier navegador web moderno (Google Chrome, Mozilla Firefox, Microsoft Edge, Safari).
3. Comience a interactuar creando una cuenta, realizando transacciones y consultando los movimientos directamente en pantalla.