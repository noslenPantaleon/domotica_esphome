# MasterGrow Backend

FastAPI backend for the MasterGrow indoor greenhouse management system.

## Features

- **User Authentication**: JWT-based authentication with registration and login
- **Grow Room Management**: Create and manage multiple grow rooms
- **Plant Tracking**: Track plants, species, and care logs
- **Sensor Integration**: Configure sensors and store time-series readings
- **Actuator Control**: Control lights, pumps, fans, and other devices
- **MQTT Communication**: Real-time communication with ESP32 devices
- **Dual Database**: PostgreSQL for relational data, MongoDB for time-series data

## Setup

1. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file with:

   ```
   POSTGRESQL_URL=postgresql://user:password@localhost/mastergrow
   MONGODB_URL=mongodb://localhost:27017/mastergrow
   SECRET_KEY=your-secret-key-change-this-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   MQTT_BROKER=localhost
   MQTT_PORT=1883
   MQTT_USERNAME=
   MQTT_PASSWORD=
   ```

3. **Database Setup**:
   - Install PostgreSQL and create a database
   - Install MongoDB
   - Tables will be created automatically on startup

4. **Run the Application**:

   ```bash
   python run.py
   ```

   Or with uvicorn:

   ```bash
   uvicorn main:app --reload
   ```

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## Key Endpoints

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /growrooms/` - List user's grow rooms
- `POST /growrooms/` - Create new grow room
- `GET /sensors/{sensor_id}/readings` - Get sensor readings
- `PUT /actuators/{actuator_id}/control` - Control actuator
- `GET /mqtt/status` - Check MQTT connection status

## MQTT Topics

- `mastergrow/sensors/{sensor_id}` - Sensor data from ESP32
- `mastergrow/actuators/{actuator_id}` - Actuator commands to ESP32

## Architecture

- **PostgreSQL**: Stores users, grow rooms, plants, sensors, actuators configurations
- **MongoDB**: Stores time-series sensor readings and actuator logs
- **MQTT**: Real-time communication between backend and ESP32 devices
- **FastAPI**: Async web framework with automatic OpenAPI docs
