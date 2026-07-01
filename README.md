# Domótica API

API REST para un sistema de domótica IoT basado en dispositivos **ESPHome** y comunicación **MQTT** y **API nativa ESPHome**. Permite gestionar clientes, usuarios, dispositivos, ubicaciones y facturación, integrando **MySQL** para datos relacionales y **MongoDB** para datos de sensores en tiempo real.

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
- [Integracion ESPHome nativa](#integracion-esphome-nativa)
- [Topicos MQTT](#topicos-mqtt)
- [Roles y permisos](#roles-y-permisos)

---

## Descripcion del proyecto

Este backend expone una API REST que actua como punto central de un sistema IoT de domótica. Sus responsabilidades principales son:

- Autenticar usuarios con JWT y control de acceso por roles.
- Gestionar el modelo de negocio: clientes, ubicaciones, dispositivos y facturación.
- Conectarse directamente a dispositivos ESPHome via **API nativa** (aioesphomeapi) para descubrir entidades y controlarlas en tiempo real.
- Recibir datos de sensores/actuadores desde dispositivos ESPHome via **MQTT**.
- Almacenar lecturas de sensores en MongoDB y metadatos relacionales en MySQL.
- Exponer endpoints para que un frontend consulte el estado de los dispositivos en tiempo real.

```
ESPHome device
     |
     |--- Native API (TCP :6053) ---> FastAPI (aioesphomeapi)  <--- control commands
     |
     |--- MQTT (eventos) -----------> Broker MQTT --> FastAPI (paho-mqtt)
                                                          |
                                                       MongoDB
                                                       MySQL
                                                          |
                                                   React / Cliente
```

---

## Arquitectura

| Capa                     | Tecnologia              | Rol                                                        |
| ------------------------ | ----------------------- | ---------------------------------------------------------- |
| API                      | FastAPI 0.136           | Framework principal, documentacion automatica              |
| Base de datos relacional | MySQL + SQLAlchemy      | Clientes, usuarios, dispositivos, facturación              |
| Base de datos documental | MongoDB + Motor         | Documentos de dispositivos, lecturas de sensores           |
| Mensajeria               | MQTT (paho-mqtt)        | Eventos en tiempo real desde dispositivos                  |
| Control nativo IoT       | aioesphomeapi           | Conexion directa a dispositivos ESPHome, control y estados |
| Autenticacion            | JWT (python-jose)       | Tokens de acceso con roles                                 |
| Migraciones              | Alembic                 | Control de versiones del esquema MySQL                     |

---

## Requisitos previos

- Python 3.10+
- MySQL 8.0+
- MongoDB 6.0+
- Broker MQTT (Mosquitto recomendado)
- Dispositivos ESPHome con `api:` habilitado en su configuracion YAML
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

Las colecciones creadas automaticamente son:

| Coleccion          | Contenido                                              |
| ------------------ | ------------------------------------------------------ |
| `devices`          | Documentos de dispositivos con sensores embebidos      |
| `sensor_readings`  | Serie de tiempo de lecturas MQTT                       |
| `actuator_logs`    | Logs de actuadores via MQTT                            |
| `esphome_states`   | Ultimo estado de cada entidad ESPHome (upsert)         |
| `esphome_readings` | Serie de tiempo de estados ESPHome (API nativa)        |

### MQTT (Mosquitto)

```bash
# Windows — instalar desde https://mosquitto.org/download/
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
MONGO_DB_NAME=domotic

# JWT
SECRET_KEY=cambia-esta-clave-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# MQTT
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# ESPHome API nativa
ESPHOME_DEFAULT_PORT=6053
ESPHOME_DEFAULT_PASSWORD=
```

Para produccion con SSL en MySQL, agregar `?ssl-mode=REQUIRED` al `DATABASE_URL`. El engine lo convierte automaticamente al formato que entiende PyMySQL.

> El archivo `.env` esta en `.gitignore` y nunca debe subirse al repositorio.

---

## Migraciones

Las migraciones son gestionadas con **Alembic**. El esquema MySQL se controla por versiones.

### Primera instalacion

Con la base de datos `domotic` ya creada y el archivo `.env` configurado, aplicar todas las migraciones existentes para crear las tablas:

```bash
alembic upgrade head
```

### Comandos de uso frecuente

```bash
# Ver el estado actual
alembic current

# Ver historial de migraciones
alembic history

# Revertir la ultima migracion
alembic downgrade -1
```

### Al modificar un modelo

```bash
alembic revision --autogenerate -m "descripcion_del_cambio"
alembic upgrade head
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
python run.py
# o directamente:
uvicorn main:app --reload --port 8000
```

La documentacion interactiva estara disponible en:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## Estructura del proyecto

```
backend/
├── main.py                  # Punto de entrada, startup/shutdown de servicios
├── run.py                   # Lanzador uvicorn
├── seed.py                  # Script de datos iniciales
├── alembic.ini              # Configuracion de Alembic
├── requirements.txt
├── .env                     # Variables de entorno (no subir a git)
├── .gitignore
├── alembic/
│   ├── env.py
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
    ├── clients/
    │   ├── models.py         # Modelo SQLAlchemy Client
    │   ├── schemas.py        # ClientCreate, ClientUpdate, ClientResponse
    │   └── router.py         # CRUD /clients
    ├── users/
    │   ├── models.py         # Modelo SQLAlchemy User (con RoleEnum)
    │   ├── schemas.py        # UserCreate, UserUpdate, UserResponse
    │   └── router.py         # CRUD /users
    ├── locations/
    │   ├── models.py         # Modelo SQLAlchemy Location
    │   ├── schemas.py        # LocationCreate, LocationUpdate, LocationResponse
    │   └── router.py         # CRUD /locations
    ├── billing/
    │   ├── models.py         # Modelo SQLAlchemy Invoice
    │   ├── schemas.py        # InvoiceCreate, InvoiceUpdate, InvoiceResponse
    │   └── router.py         # CRUD /billing
    ├── devices/
    │   ├── models.py         # Modelo SQLAlchemy ClientDevice
    │   ├── schemas.py        # ClientDeviceCreate, ClientDeviceResponse
    │   ├── mongo_schemas.py  # Schemas Pydantic para documentos MongoDB
    │   └── router.py         # CRUD /devices
    ├── mqtt/
    │   ├── handler.py        # Cliente MQTT, suscripcion a topicos, ingestion a MongoDB
    │   └── router.py         # GET /mqtt/status, POST /mqtt/publish
    └── esphome/
        ├── manager.py        # ESPHomeManager: conexiones, entidades, estados, comandos
        ├── schemas.py        # ESPHomeConnectRequest, ESPHomeSwitchCommand, etc.
        └── router.py         # Endpoints /esphome
```

---

## Rutas de la API

### Autenticacion

| Metodo | Ruta          | Descripcion                             | Acceso      |
| ------ | ------------- | --------------------------------------- | ----------- |
| POST   | `/auth/login` | Login con email y password, retorna JWT | Publico     |
| GET    | `/auth/me`    | Retorna el usuario autenticado actual   | Autenticado |

### Clients

| Metodo | Ruta            | Descripcion                | Acceso                 |
| ------ | --------------- | -------------------------- | ---------------------- |
| GET    | `/clients/`     | Listar todos los clientes  | Admin                  |
| GET    | `/clients/{id}` | Obtener un cliente         | Admin / propio cliente |
| POST   | `/clients/`     | Crear cliente              | Admin                  |
| PUT    | `/clients/{id}` | Actualizar cliente         | Admin                  |
| DELETE | `/clients/{id}` | Eliminar cliente (cascada) | Admin                  |

### Users

| Metodo | Ruta          | Descripcion        | Acceso         |
| ------ | ------------- | ------------------ | -------------- |
| GET    | `/users/`     | Listar usuarios    | Admin          |
| GET    | `/users/{id}` | Obtener un usuario | Admin / propio |
| POST   | `/users/`     | Crear usuario      | Admin          |
| PUT    | `/users/{id}` | Actualizar usuario | Admin / propio |
| DELETE | `/users/{id}` | Eliminar usuario   | Admin          |

### Locations

| Metodo | Ruta               | Descripcion           | Acceso          |
| ------ | ------------------ | --------------------- | --------------- |
| GET    | `/locations/`      | Listar ubicaciones    | Admin / Tecnico |
| GET    | `/locations/{id}`  | Obtener una ubicacion | Autenticado     |
| POST   | `/locations/`      | Crear ubicacion       | Admin           |
| PUT    | `/locations/{id}`  | Actualizar ubicacion  | Admin           |
| DELETE | `/locations/{id}`  | Eliminar ubicacion    | Admin           |

### Billing

| Metodo | Ruta             | Descripcion             | Acceso                 |
| ------ | ---------------- | ----------------------- | ---------------------- |
| GET    | `/billing/`      | Listar facturas         | Admin                  |
| GET    | `/billing/{id}`  | Obtener una factura     | Admin / cliente propio |
| POST   | `/billing/`      | Crear factura           | Admin                  |
| PUT    | `/billing/{id}`  | Actualizar estado/monto | Admin                  |
| DELETE | `/billing/{id}`  | Eliminar factura        | Admin                  |

### Devices

| Metodo | Ruta                           | Descripcion                              | Acceso      |
| ------ | ------------------------------ | ---------------------------------------- | ----------- |
| GET    | `/devices/`                    | Listar client devices (SQL)              | Admin       |
| GET    | `/devices/{id}`                | Obtener un client device                 | Autenticado |
| POST   | `/devices/`                    | Registrar client device                  | Admin       |
| PUT    | `/devices/{id}`                | Actualizar client device                 | Admin       |
| DELETE | `/devices/{id}`                | Eliminar client device                   | Admin       |
| POST   | `/devices/mongo`               | Crear documento de dispositivo (MongoDB) | Admin       |
| GET    | `/devices/mongo`               | Listar documentos de dispositivos        | Autenticado |
| GET    | `/devices/mongo/{device_id}`   | Obtener documento de dispositivo         | Autenticado |
| GET    | `/devices/mongo/{device_id}/readings` | Lecturas recientes del dispositivo | Autenticado |

### MQTT

| Metodo | Ruta                    | Descripcion                     | Acceso          |
| ------ | ----------------------- | ------------------------------- | --------------- |
| GET    | `/mqtt/status`          | Estado de la conexion al broker | Autenticado     |
| POST   | `/mqtt/publish/{topic}` | Publicar mensaje a un topico    | Admin / Tecnico |

### ESPHome (API nativa)

| Metodo | Ruta                                       | Descripcion                                      | Acceso          |
| ------ | ------------------------------------------ | ------------------------------------------------ | --------------- |
| POST   | `/esphome/{device_id}/connect`             | Conectar a un dispositivo ESPHome                | Admin           |
| DELETE | `/esphome/{device_id}/disconnect`          | Desconectar un dispositivo                       | Admin           |
| GET    | `/esphome/status`                          | Listar todas las conexiones activas              | Autenticado     |
| GET    | `/esphome/{device_id}/entities`            | Listar entidades del dispositivo                 | Autenticado     |
| GET    | `/esphome/{device_id}/states`              | Ultimo estado de cada entidad (MongoDB)          | Autenticado     |
| GET    | `/esphome/{device_id}/readings`            | Serie de tiempo de estados (MongoDB)             | Autenticado     |
| POST   | `/esphome/{device_id}/switch/{key}/control`| Controlar un switch (encender/apagar)            | Admin / Tecnico |
| POST   | `/esphome/{device_id}/light/{key}/control` | Controlar una luz (on/off, brillo, RGB)          | Admin / Tecnico |

---

## Integracion ESPHome nativa

La integracion usa **aioesphomeapi** para conectarse directamente a los dispositivos ESPHome a traves de su API nativa (puerto TCP 6053). Esto permite descubrir entidades automaticamente y enviar comandos de control sin necesidad de MQTT.

### Configuracion del dispositivo ESPHome

El unico requisito en el YAML del dispositivo es habilitar el bloque `api:`:

```yaml
esphome:
  name: esp32-001

esp32:
  board: esp32-s3-devkitc-1
  variant: esp32s3
  framework:
    type: arduino

api:
  password: ""   # dejar vacio o establecer una password

ota:
  - platform: esphome
    password: ""

wifi:
  ssid: "TuRed"
  password: "TuPassword"

logger:

# Ejemplo: switch GPIO
switch:
  - platform: gpio
    pin: GPIO2
    name: "LED"

# Ejemplo: sensor de temperatura interno
sensor:
  - platform: internal_temperature
    name: "CPU Temperature"
    update_interval: 10s
```

> No se requiere configurar topicos ni estructuras de mensajes. ESPHome expone todas las entidades automaticamente via la API nativa.

### Flujo de uso

#### 1. Conectar al dispositivo

Primero obtener el IP del dispositivo (via ping o DHCP del router):

```bash
ping esp32-001.local
```

Luego conectar desde la API:

```http
POST /esphome/ESP32_001/connect
Authorization: Bearer <token>
Content-Type: application/json

{
  "host": "192.168.1.100",
  "port": 6053,
  "password": ""
}
```

Respuesta:
```json
{
  "device_id": "ESP32_001",
  "host": "192.168.1.100",
  "port": 6053,
  "connected": true
}
```

#### 2. Descubrir entidades

```http
GET /esphome/ESP32_001/entities
Authorization: Bearer <token>
```

Respuesta:
```json
[
  {
    "key": 646037088,
    "name": "LED",
    "object_id": "led",
    "entity_type": "switch",
    "unit": null
  },
  {
    "key": 1234567890,
    "name": "CPU Temperature",
    "object_id": "cpu_temperature",
    "entity_type": "sensor",
    "unit": "°C"
  }
]
```

> El campo `key` es el identificador numerico que se usa en los endpoints de control.

#### 3. Controlar un switch

```http
POST /esphome/ESP32_001/switch/646037088/control
Authorization: Bearer <token>
Content-Type: application/json

{ "state": true }   # encender
{ "state": false }  # apagar
```

#### 4. Controlar una luz RGB

```http
POST /esphome/ESP32_001/light/987654321/control
Authorization: Bearer <token>
Content-Type: application/json

{
  "state": true,
  "brightness": 0.8,
  "red": 1.0,
  "green": 0.0,
  "blue": 0.5
}
```

#### 5. Consultar estados almacenados en MongoDB

Cada vez que el dispositivo envia un cambio de estado, se almacena automaticamente. Para ver el ultimo estado de cada entidad:

```http
GET /esphome/ESP32_001/states
Authorization: Bearer <token>
```

Para ver el historial de estados (serie de tiempo):

```http
GET /esphome/ESP32_001/readings?limit=50
Authorization: Bearer <token>
```

#### 6. Ver conexiones activas

```http
GET /esphome/status
Authorization: Bearer <token>
```

Respuesta:
```json
[
  {
    "device_id": "ESP32_001",
    "host": "192.168.1.100",
    "port": 6053,
    "connected": true
  }
]
```

### Diferencias entre MQTT y API nativa

| Caracteristica         | MQTT                              | API nativa (aioesphomeapi)              |
| ---------------------- | --------------------------------- | --------------------------------------- |
| Protocolo              | Pub/Sub sobre TCP                 | Binario (protobuf) sobre TCP            |
| Puerto                 | 1883                              | 6053                                    |
| Descubrimiento         | Manual (topicos fijos)            | Automatico (list_entities_services)     |
| Control de dispositivo | Publicar en topico de actuador    | Llamada directa (switch_command, etc.)  |
| Configuracion ESPHome  | Requiere bloque `mqtt:` + topicos | Solo requiere bloque `api:`             |
| Conexion               | Broker intermediario              | Directa dispositivo-servidor            |
| Ambos pueden coexistir | Si                                | Si                                      |

---

## Topicos MQTT

| Topico                              | Direccion      | Descripcion           |
| ----------------------------------- | -------------- | --------------------- |
| `domotica/sensors/{device_id}`      | ESPHome -> API | Lectura de sensores   |
| `domotica/actuators/{device_id}`    | API -> ESPHome | Comandos a actuadores |

### Estructura del mensaje MQTT (sensores)

```json
{
  "sensor_name": "temperature",
  "sensor_type": "dht",
  "value": 23.5,
  "unit": "°C"
}
```

---

## Roles y permisos

| Rol          | Descripcion                                                           |
| ------------ | --------------------------------------------------------------------- |
| `admin`      | Acceso total: gestiona clientes, usuarios, dispositivos y facturación |
| `technician` | Puede ver y operar dispositivos, no gestiona clientes ni facturación  |
| `viewer`     | Solo lectura sobre los dispositivos de su cliente                     |
