# API de Picking con FastAPI

## Descripción

Esta API permite consultar pedidos y registrar la recogida de sus productos durante la preparación de una compra en una tienda online.

El proyecto utiliza una base de datos simulada en memoria mediante un diccionario de Python. No requiere instalar un gestor de base de datos.

## Funcionalidades

- Listar los pedidos de prueba.
- Consultar un pedido por su identificador.
- Registrar la cantidad recogida de un producto.
- Validar que el pedido y el producto existan.
- Impedir recoger más unidades de las solicitadas.
- Actualizar el estado del pedido a `EN_PROCESO` o `COMPLETADO`.

## Requisitos

- Python 3.10 o superior instalado.
- Una terminal.
- Conexión a internet para instalar las dependencias inicialmente.

Las instrucciones siguientes están preparadas para Windows y deben ejecutarse desde la carpeta del proyecto.

## Estructura del proyecto

```text
picking/
├── database.py
├── schemas.py
├── main.py
└── README.md
```

| Archivo | Función |
| --- | --- |
| `database.py` | Contiene los pedidos y productos de prueba. |
| `schemas.py` | Define y valida los datos de entrada de una recogida. |
| `main.py` | Contiene la aplicación FastAPI y sus endpoints. |
| `README.md` | Explica la instalación y el uso del proyecto. |

## Instalación

### 1. Extraer el proyecto

Descomprimir el archivo ZIP y abrir una terminal dentro de la carpeta que contiene `main.py`.

### 2. Crear un entorno virtual

```powershell
py -m venv .venv
```

Si el equipo utiliza el comando `python` en lugar de `py`:

```powershell
python -m venv .venv
```

Solo es necesario utilizar uno de los dos comandos.

### 3. Instalar las dependencias

```powershell
.\.venv\Scripts\python.exe -m pip install "fastapi[standard]"
```

Este comando instala FastAPI y las herramientas necesarias para ejecutar el servidor dentro del entorno virtual. No es necesario activar el entorno porque se utiliza directamente su ejecutable.

La instalación se realiza una vez por entorno, no cada vez que se inicia la API.

## Ejecución

Desde la carpeta del proyecto:

```powershell
.\.venv\Scripts\fastapi.exe dev main.py
```

Con la configuración predeterminada, la API estará disponible en:

http://127.0.0.1:8000

Para abrir la documentación interactiva y probar las operaciones:

http://127.0.0.1:8000/docs

La ruta `/` no está implementada; abrir únicamente la dirección base puede devolver `Not Found`. Utilizar `/docs` o los endpoints descritos a continuación.

Para detener el servidor, pulsar `Ctrl + C` en la terminal.

## Datos de prueba

Los pedidos iniciales definidos en `database.py` son:

| Pedido | SKU | Producto | Ubicación | Cantidad solicitada |
| --- | --- | --- | --- | --- |
| 1001 | CAM-001 | Camiseta | A-01 | 3 |
| 1001 | PAN-002 | Pantalón | B-04 | 2 |
| 1002 | ZAP-003 | Zapatos | C-02 | 1 |

Todos comienzan en estado `PENDIENTE` y con cero unidades recogidas.

El SKU es el código que identifica un producto. Cada elemento de la lista `productos` representa una línea del pedido con sus cantidades solicitadas y recogidas.

## Endpoints

### Consultar todos los pedidos

```http
GET /pedidos
```

Devuelve la lista de pedidos y el avance de recogida de sus productos.

### Consultar un pedido

```http
GET /pedidos/{pedido_id}
```

Ejemplo:

```http
GET /pedidos/1001
```

Devuelve el pedido indicado. Si no existe, responde con un error `404`.

### Registrar una recogida

```http
POST /pedidos/{pedido_id}/recogidas
```

El cuerpo de la petición debe ser JSON:

```json
{
  "sku": "CAM-001",
  "cantidad": 2
}
```

| Campo | Tipo | Regla |
| --- | --- | --- |
| `sku` | Texto | Debe ser no vacío y coincidir con un producto del pedido. |
| `cantidad` | Número entero | Debe ser mayor que cero y no superar la cantidad pendiente. |

La cantidad enviada se suma a lo que ya se ha recogido; no reemplaza el total anterior. Cada petición válida registra una nueva recogida.

Respuesta de ejemplo para el pedido 1001 partiendo de los datos iniciales:

```json
{
  "mensaje": "Recogida registrada",
  "pedido_id": 1001,
  "sku": "CAM-001",
  "cantidad_recogida": 2,
  "cantidad_pendiente": 1,
  "estado": "EN_PROCESO"
}
```

## Prueba paso a paso desde la documentación

1. Iniciar el servidor y abrir http://127.0.0.1:8000/docs.
2. Abrir `GET /pedidos`, pulsar **Try it out** y después **Execute** para ver los pedidos.
3. Abrir `POST /pedidos/{pedido_id}/recogidas` y pulsar **Try it out**.
4. Introducir `1001` en `pedido_id`.
5. Enviar el siguiente cuerpo y pulsar **Execute**:

```json
{
  "sku": "CAM-001",
  "cantidad": 2
}
```

El pedido estará `EN_PROCESO`; quedará una camiseta por recoger.

6. En el mismo endpoint, registrar la camiseta restante:

```json
{
  "sku": "CAM-001",
  "cantidad": 1
}
```

7. Registrar los dos pantalones:

```json
{
  "sku": "PAN-002",
  "cantidad": 2
}
```

La última respuesta mostrará el estado `COMPLETADO`.

8. Consultar `GET /pedidos/1001` para comprobar las cantidades finales.

Cada bloque JSON se envía en una petición separada. Para repetir la prueba desde cero, detener y volver a iniciar el servidor.

## Estados del pedido

| Estado | Significado |
| --- | --- |
| `PENDIENTE` | No se ha registrado ninguna recogida. |
| `EN_PROCESO` | Se ha recogido alguna unidad, pero todavía faltan productos. |
| `COMPLETADO` | Se recogieron todas las unidades solicitadas. |

Completar el picking indica que terminó la recogida; no significa que el pedido ya se haya enviado.

## Validaciones y errores

| Situación | Código HTTP |
| --- | --- |
| Consulta o recogida correcta | `200` |
| La cantidad supera las unidades pendientes | `400` |
| El pedido no existe | `404` |
| El producto no pertenece al pedido | `404` |
| Faltan campos o los datos no cumplen el esquema | `422` |

Ejemplo de una recogida que supera las unidades pendientes:

```json
{
  "detail": "Solo quedan 1 unidades por recoger"
}
```

También se pueden probar cantidades como `0`, `-1` o `1.5`, que deben producir un error `422`.

## Funcionamiento de la base de datos simulada

`database.py` define el diccionario `pedidos_db`. Al iniciar la aplicación, Python carga esos datos en memoria y los endpoints consultan y modifican el mismo diccionario.

Los cambios no se escriben en el archivo `database.py`. Al reiniciar el servidor, los datos vuelven a sus valores iniciales. En modo desarrollo, guardar cambios en el código puede provocar una recarga y reiniciar también los datos.

Esta versión debe ejecutarse con un único proceso de servidor, ya que cada proceso tendría su propia copia de los datos. El bloqueo incluido en la operación de recogida protege las actualizaciones dentro de ese proceso.

## Alcance del proyecto

Es una implementación académica con datos simulados. No incluye persistencia, autenticación, control de stock, historial de recogidas ni creación de pedidos mediante la API. Los pedidos iniciales se definen en `database.py`.

No existe deduplicación de peticiones: si se envía dos veces una recogida y todavía quedan unidades pendientes, ambas se sumarán.
