| # | Pregunta | Técnica | RAG | Tokens in | Tokens out | ms | Auto | Evaluación manual (0-2) |
|---|---|---|---|---|---|---|---|---|
| 1 | Q1 | zero-shot | sí | 112 | 100 | 1495.2 | OK |  |
| 2 | Q1 | few-shot | sí | 257 | 40 | 764.6 | OK |  |
| 3 | Q1 | cot | sí | 132 | 207 | 1443.2 | OK |  |
| 4 | Q2 | zero-shot | sí | 179 | 31 | 732.0 | OK |  |
| 5 | Q2 | few-shot | sí | 324 | 31 | 692.8 | OK |  |
| 6 | Q2 | cot | sí | 199 | 159 | 1452.8 | OK |  |
| 7 | Q3 | zero-shot | sí | 182 | 39 | 1110.1 | manual |  |
| 8 | Q3 | few-shot | sí | 327 | 48 | 1188.2 | manual |  |
| 9 | Q3 | cot | sí | 202 | 248 | 1676.0 | manual |  |
| 10 | Q4 | zero-shot | sí | 172 | 29 | 676.9 | manual |  |
| 11 | Q4 | few-shot | sí | 317 | 9 | 2028.4 | manual |  |
| 12 | Q4 | cot | sí | 192 | 83 | 1383.8 | manual |  |
| 13 | Q1 | zero-shot | no | 70 | 23 | 1201.6 | FALLA |  |
| 14 | Q2 | zero-shot | no | 68 | 18 | 867.9 | FALLA |  |
| 15 | Q3 | zero-shot | no | 71 | 27 | 1096.5 | manual |  |
| 16 | Q4 | zero-shot | no | 61 | 17 | 708.2 | manual |  |

## Respuestas completas

### 1. Q1 | zero-shot | rag=True
**Pregunta:** ¿Cuánto cuestan en total 2 laptops y 3 mouse?

**Respuesta:** Según el catálogo:
- Laptop: $2500000 cada una
- Mouse inalámbrico: $45000 cada uno

El costo total sería:
- 2 laptops: $2500000 x 2 = $5000000
- 3 mouse: $45000 x 3 = $135000

Total a pagar: $5135000

### 2. Q1 | few-shot | rag=True
**Pregunta:** ¿Cuánto cuestan en total 2 laptops y 3 mouse?

**Respuesta:** 2 laptops y 3 mouse cuestan en total $5135000 (2 x $2500000 + 3 x $45000).

### 3. Q1 | cot | rag=True
**Pregunta:** ¿Cuánto cuestan en total 2 laptops y 3 mouse?

**Respuesta:** Paso 1: Busco el precio de la laptop en el catálogo. El precio de la laptop (id 1) es $2500000.
Paso 2: Calculo el costo de 2 laptops: 2 x $2500000 = $5000000.
Paso 3: Busco el precio del mouse inalámbrico en el catálogo. El precio del mouse inalámbrico (id 2) es $45000.
Paso 4: Calculo el costo de 3 mouse: 3 x $45000 = $135000.
Paso 5: Sumo el costo total de ambos productos: $5000000 + $135000 = $5135000.

Respuesta final: El total por 2 laptops y 3 mouse es $5135000.

### 4. Q2 | zero-shot | rag=True
**Pregunta:** ¿Cuál es el producto más barato y cuánto stock tiene?

**Respuesta:** El producto más barato es el Mouse inalámbrico, con un precio de $45000, y tiene un stock de 50 unidades.

### 5. Q2 | few-shot | rag=True
**Pregunta:** ¿Cuál es el producto más barato y cuánto stock tiene?

**Respuesta:** El producto más barato es el Mouse inalámbrico, con un precio de $45000, y tiene un stock de 50 unidades.

### 6. Q2 | cot | rag=True
**Pregunta:** ¿Cuál es el producto más barato y cuánto stock tiene?

**Respuesta:** Paso 1: Revisar la lista de productos y sus precios en el catálogo:
- Laptop: $2500000
- Mouse inalámbrico: $45000
- Teclado: $90000
- Monitor: $780000
- Audífonos: $120000

Paso 2: Identificar el producto con el precio más bajo, que es el Mouse inalámbrico con un precio de $45000.

Paso 3: Verificar el stock del Mouse inalámbrico en el catálogo, que es 50 unidades.

Respuesta final: El producto más barato es el Mouse inalámbrico y tiene un stock de 50 unidades.

### 7. Q3 | zero-shot | rag=True
**Pregunta:** ¿Qué productos puedo comprar con 100000 pesos?

**Respuesta:** Con 100000 pesos puedes comprar los siguientes productos:

- Mouse inalámbrico ($45000)
- Teclado ($90000)

### 8. Q3 | few-shot | rag=True
**Pregunta:** ¿Qué productos puedo comprar con 100000 pesos?

**Respuesta:** Con 100000 pesos puedes comprar el siguiente producto:
- Mouse inalámbrico ($45000)

(También te alcanza para 1 Teclado, que cuesta $90000).

### 9. Q3 | cot | rag=True
**Pregunta:** ¿Qué productos puedo comprar con 100000 pesos?

**Respuesta:** Paso 1: Analizar el presupuesto disponible, que es de $100000.
Paso 2: Revisar los precios de los productos en el catálogo:
- Laptop: $2500000 (excede el presupuesto)
- Mouse inalámbrico: $45000 (dentro del presupuesto)
- Teclado: $90000 (dentro del presupuesto)
- Monitor: $780000 (excede el presupuesto)
- Audífonos: $120000 (excede el presupuesto)

Paso 3: Identificar qué productos individuales se pueden comprar (Mouse inalámbrico y Teclado). También es posible comprar combinaciones que no superen los $100000 (por ejemplo, un mouse inalámbrico y un teclado suman $135000, lo cual excede el presupuesto, por lo que solo se puede comprar uno a la vez).

Respuesta final: Con 100000 pesos puedes comprar el Mouse inalámbrico ($45000) o el Teclado ($90000).

### 10. Q4 | zero-shot | rag=True
**Pregunta:** ¿Venden tablets?

**Respuesta:** No vendo tablets. Lo que tengo disponible en el catálogo es: Laptop, Mouse inalámbrico, Teclado, Monitor y Audífonos.

### 11. Q4 | few-shot | rag=True
**Pregunta:** ¿Venden tablets?

**Respuesta:** No, en el catálogo no hay tablets.

### 12. Q4 | cot | rag=True
**Pregunta:** ¿Venden tablets?

**Respuesta:** Paso 1: Revisar el catálogo disponible en busca de "tablets".
Paso 2: El catálogo contiene los siguientes productos: Laptop, Mouse inalámbrico, Teclado, Monitor y Audífonos.
Paso 3: No se encuentra ninguna tablet en el catálogo, por lo que no se vende ese producto.

Respuesta final: Lo siento, no vendemos tablets.

### 13. Q1 | zero-shot | rag=False
**Pregunta:** ¿Cuánto cuestan en total 2 laptops y 3 mouse?

**Respuesta:** Lo siento, pero el catálogo no está disponible y no tengo información sobre los precios de las laptops y los mouse.

### 14. Q2 | zero-shot | rag=False
**Pregunta:** ¿Cuál es el producto más barato y cuánto stock tiene?

**Respuesta:** El catálogo no está disponible, por lo que no puedo ver los productos ni su stock.

### 15. Q3 | zero-shot | rag=False
**Pregunta:** ¿Qué productos puedo comprar con 100000 pesos?

**Respuesta:** El catálogo no está disponible, por lo que no puedo decirte qué productos puedes comprar con 100000 pesos.

### 16. Q4 | zero-shot | rag=False
**Pregunta:** ¿Venden tablets?

**Respuesta:** El catálogo no está disponible, por lo que no puedo confirmar si vendemos tablets.
