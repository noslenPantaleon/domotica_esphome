# Domótica API

API REST para un sistema de domótica IoT basado en dispositivos **ESPHome** y comunicación **MQTT**. Permite gestionar clientes, usuarios, dispositivos, ubicaciones y facturación, integrando **MySQL** para datos relacionales y **MongoDB** para datos de sensores en tiempo real.

---

## Tabla de contenidos

- [Descripcion del proyecto](#descripcion-del-proyecto)
- [Arquitectura](#arquitectura)
- [Requisitos previos](#requisitos-previos)
- [Configuracion de bases de datos](#configuracion-de-bases-de-datos)
- [Instalacion del proyecto](#instalacion-del-proyecto)
- [Variables de entorno](#variables-de-entorno)
- [Migraciones](#migraciones)
- [Seed inicial](#seed-inicial)
- [Ejecutar el servidor](#ejecutar-el-servidor)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Rutas de la API](#rutas-de-la-api)
- [Topicos MQTT](#topicos-mqtt)
- [Roles y permisos](#roles-y-permisos)

---

## Descripcion del proyecto

Este backend expone una API REST que actua como punto central de un sistema IoT de domótica. Sus responsabilidades principales son:

- Autenticar usuarios con JWT y control de acceso por roles.
- Gestionar el modelo de negocio: clientes, ubicaciones, dispositivos y facturación.
- Recibir datos de sensores/actuadores desde dispositivos ESPHome via MQTT.
- Almacenar lecturas de sensores en MongoDB y metadatos relacionales en MySQL.
- Exponer endpoints para que un frontend React consulte el estado de los dispositivos en tiempo real.

```
ESPHome  <---------------------->  FastAPI  (aioesphomeapi)
   |                                   |
   |------- MQTT (eventos) ----------->|
               (broker)                |
                                   React / Cliente
```

---

## Arquitectura

| Capa | Tecnologia | Rol |
|---|---|---|
| API | FastAPI 0.136 | Framework principal, documentacion automatica |
| Base de datos relacional | MySQL + SQLAlchemy | Clientes, usuarios, dispositivos, facturación |
| Base de datos documental | MongoDB + Motor | Documentos de dispositivos, lecturas de sensores |
| Mensajeria | MQTT (paho-mqtt) | Eventos en tiempo real desde dispositivos |
| Autenticacion | JWT (python-jose) | Tokens de acceso con roles |
| Migraciones | Alembic | Control de versiones del esquema MySQL |

---

## Requisitos previos

- Python 3.10+
- MySQL 8.0+
- MongoDB 6.0+
- Broker MQTT (Mosquitto recomendado)
- Git

---

## Configuracion de bases de datos

### MySQL

1. Instalar MySQL Server y abrir el cliente:

```bash
mysql -u root -p
```

2. Crear la base de datos:

```sql
CREATE DATABASE domotic CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. Crear un usuario dedicado (opcional pero recomendado):

```sql
CREATE USER 'domotic_user'@'localhost' IDENTIFIED BY 'tu_password';
GRANT ALL PRIVILEGES ON domotic.* TO 'domotic_user'@'localhost';
FLUSH PRIVILEGES;
```

### MongoDB

1. Instalar MongoDB y asegurarse de que el servicio esté corriendo:

```bash
# Windows
net start MongoDB

# Linux/Mac
sudo systemctl start mongod
```

2. No es necesario crear la base de datos manualmente. MongoDB crea `domotic` automáticamente al insertar el primer documento.

### MQTT (Mosquitto)

```bash
# Windows — instalar desde https://mosquitto.org/download/
# Iniciar el servicio
net start mosquitto
```

---

## Instalacion del proyecto

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd domotica_project/backend

# 2. Crear entorno virtual
python -m venv .venv

# 3. Activar entorno virtual
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt
```

---

## Variables de entorno

Crear un archivo `.env` en la raiz del proyecto (`backend/.env`):

```env
# Base de datos MySQL
DATABASE_URL=mysql+pymysql://root:tu_password@localhost/domotic

# Base de datos MongoDB
MONGODB_URL=mongodb://localhost:27017/domotic

# JWT
SECRET_KEY=cambia-esta-clave-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# MQTT
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
```

> El archivo `.env` esta en `.gitignore` y nunca debe subirse al repositorio.

---

## Migraciones

Las migraciones son gestionadas con **Alembic**. El esquema MySQL se controla por versiones.

```bash
# Aplicar todas las migraciones pendientes (primera vez o tras actualizar)
alembic upgrade head

# Generar una nueva migracion despues de modificar un modelo
alembic revision --autogenerate -m "descripcion_del_cambio"

# Ver el estado actual
alembic current

# Ver historial de migraciones
alembic history

# Revertir la ultima migracion
alembic downgrade -1
```

---

## Seed inicial

Antes de hacer la primera peticion autenticada es necesario crear el primer cliente y usuario administrador:

```bash
python seed.py
```

Esto crea:
- Un cliente base llamado `Mi Empresa`
- Un usuario administrador con email `admin@domotic.com` y password `admin1234`

> Cambiar la password despues del primer login.

---

## Ejecutar el servidor

```bash
uvicorn main:app --reload --port 8000
```

La documentacion interactiva estara disponible en:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## Estructura del proyecto

```
backend/
├── main.py                  # Punto de entrada de la aplicacion
├── seed.py                  # Script de datos iniciales
├── alembic.ini              # Configuracion de Alembic
├── requirements.txt
├── .env                     # Variables de entorno (no subir a git)
├── .gitignore
├── alembic/
│   ├── env.py               # Configuracion de migraciones
│   └── versions/            # Archivos de migracion generados
└── src/
    ├── config/
    │   └── settings.py      # Configuracion global (pydantic-settings)
    ├── database/
    │   ├── mysql.py          # Engine y sesion SQLAlchemy
    │   └── mongodb.py        # Cliente Motor (MongoDB async)
    ├── auth/
    │   ├── router.py         # POST /auth/login, GET /auth/me
    │   ├── service.py        # Hash de passwords, creacion de JWT
    │   ├── schemas.py        # Token, TokenData
    │   └── dependencies.py   # get_current_user, require_role
    ├── clientes/
    │   ├── models.py         # Modelo SQLAlchemy Cliente
    │   ├── schemas.py        # ClienteCreate, ClienteUpdate, ClienteResponse
    │   └── router.py         # CRUD /clientes
    ├── usuarios/
    │   ├── models.py         # Modelo SQLAlchemy Usuario (con RolEnum)
    │   ├── schemas.py        # UsuarioCreate, UsuarioUpdate, UsuarioResponse
    │   └── router.py         # CRUD /usuarios
    ├── ubicaciones/
    │   ├── models.py         # Modelo SQLAlchemy Ubicacion
    │   ├── schemas.py        # UbicacionCreate, UbicacionUpdate, UbicacionResponse
    │   └── router.py         # CRUD /ubicaciones
    ├── facturacion/
    │   ├── models.py         # Modelo SQLAlchemy Facturacion (con EstadoFacturaEnum)
    │   ├── schemas.py        # FacturacionCreate, FacturacionUpdate, FacturacionResponse
    │   └── router.py         # CRUD /facturacion
    ├── dispositivos/
    │   ├── models.py         # Modelo SQLAlchemy ClienteDispositivo
    │   ├── schemas.py        # ClienteDispositivoCreate, Response
    │   ├── mongo_schemas.py  # Schemas Pydantic para documentos MongoDB
    │   └── router.py         # CRUD /dispositivos
    └── mqtt/
        ├── handler.py        # Cliente MQTT, suscripcion a topicos
        └── router.py         # GET /mqtt/status, POST /mqtt/publish
```

---

## Rutas de la API

### Autenticacion

| Metodo | Ruta | Descripcion | Acceso |
|---|---|---|---|
| POST | `/auth/login` | Login con email y password, retorna JWT | Publico |
| GET | `/auth/me` | Retorna el usuario autenticado actual | Autenticado |

### Clientes

| Metodo | Ruta | Descripcion | Acceso |
|---|---|---|---|
| GET | `/clientes/` | Listar todos los clientes | Admin |
| GET | `/clientes/{id}` | Obtener un cliente | Admin / propio cliente |
| POST | `/clientes/` | Crear cliente | Admin |
| PUT | `/clientes/{id}` | Actualizar cliente | Admin |
| DELETE | `/clientes/{id}` | Eliminar cliente (cascada) | Admin |

### Usuarios

| Metodo | Ruta | Descripcion | Acceso |
|---|---|---|---|
| GET | `/usuarios/` | Listar usuarios | Admin |
| GET | `/usuarios/{id}` | Obtener un usuario | Admin / propio |
| POST | `/usuarios/` | Crear usuario | Admin |
| PUT | `/usuarios/{id}` | Actualizar usuario | Admin / propio |
| DELETE | `/usuarios/{id}` | Eliminar usuario | Admin |

### Ubicaciones

| Metodo | Ruta | Descripcion | Acceso |
|---|---|---|---|
| GET | `/ubicaciones/` | Listar ubicaciones | Admin / Tecnico |
| GET | `/ubicaciones/{id}` | Obtener una ubicacion | Autenticado |
| POST | `/ubicaciones/` | Crear ubicacion | Admin |
| PUT | `/ubicaciones/{id}` | Actualizar ubicacion | Admin |
| DELETE | `/ubicaciones/{id}` | Eliminar ubicacion | Admin |

### Facturacion

| Metodo | Ruta | Descripcion | Acceso |
|---|---|---|---|
| GET | `/facturacion/` | Listar facturas | Admin |
| GET | `/facturacion/{id}` | Obtener una factura | Admin / cliente propio |
| POST | `/facturacion/` | Crear factura | Admin |
| PUT | `/facturacion/{id}` | Actualizar estado/monto | Admin |
| DELETE | `/facturacion/{id}` | Eliminar factura | Admin |

### Dispositivos

| Metodo | Ruta | Descripcion | Acceso |
|---|---|---|---|
| GET | `/dispositivos/` | Listar dispositivos del cliente | Autenticado |
| GET | `/dispositivos/{id}` | Obtener un dispositivo (SQL + Mongo) | Autenticado |
| POST | `/dispositivos/` | Registrar dispositivo | Admin / Tecnico |
| PUT | `/dispositivos/{id}` | Actualizar dispositivo | Admin / Tecnico |
| DELETE | `/dispositivos/{id}` | Eliminar dispositivo | Admin |
| GET | `/dispositivos/{id}/sensores` | Listar sensores del dispositivo (Mongo) | Autenticado |
| POST | `/dispositivos/{id}/sensores` | Agregar sensor al dispositivo | Admin / Tecnico |

### MQTT

| Metodo | Ruta | Descripcion | Acceso |
|---|---|---|---|
| GET | `/mqtt/status` | Estado de la conexion al broker | Autenticado |
| POST | `/mqtt/publish/{topic}` | Publicar mensaje a un topico | Admin / Tecnico |

---

## Topicos MQTT

| Topico | Direccion | Descripcion |
|---|---|---|
| `domotica/sensores/{dispositivo_id}` | ESPHome -> API | Lectura de sensores |
| `domotica/actuadores/{dispositivo_id}` | API -> ESPHome | Comandos a actuadores |

---

## Roles y permisos

| Rol | Descripcion |
|---|---|
| `admin` | Acceso total: gestiona clientes, usuarios, dispositivos y facturación |
| `tecnico` | Puede ver y operar dispositivos, no gestiona clientes ni facturación |
| `visualizador` | Solo lectura sobre los dispositivos de su cliente |

---

## Notas de desarrollo

- Las rutas marcadas como **pendientes** en la tabla estan definidas como stubs y seran implementadas progresivamente.
- Para agregar una nueva migracion tras modificar un modelo: `alembic revision --autogenerate -m "nombre"`.
- La documentacion interactiva en `/docs` permite probar todos los endpoints directamente con autenticacion JWT.
