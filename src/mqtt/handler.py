import json
import asyncio
from typing import Dict, Any, Optional

import paho.mqtt.client as mqtt
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.config.settings import settings
from src.database.mongodb import get_mongo_db
from src.devices.mongo_schemas import SensorReading


class MQTTHandler:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.mongo_db: Optional[AsyncIOMotorDatabase] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT broker with result code {rc}")
        # Subscribe to topics
        self.client.subscribe("domotica/sensors/#")
        self.client.subscribe("domotica/actuators/#")

    def on_message(self, client, userdata, msg):
        print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
        if self.loop is None:
            print("MQTT handler has no event loop bound — dropping message")
            return
        asyncio.run_coroutine_threadsafe(
            self.process_message(msg.topic, msg.payload.decode()), self.loop
        )

    async def process_message(self, topic: str, payload: str):
        try:
            data = json.loads(payload)
            topic_parts = topic.split("/")

            if len(topic_parts) >= 3:
                device_type = topic_parts[1]  # sensors or actuators
                device_id = topic_parts[2]

                if device_type == "sensors":
                    await self.handle_sensor_data(device_id, data)
                elif device_type == "actuators":
                    await self.handle_actuator_data(device_id, data)

        except json.JSONDecodeError:
            print(f"Invalid JSON payload: {payload}")
        except Exception as e:
            print(f"Error processing message: {e}")

    async def handle_sensor_data(self, device_id: str, data: Dict[str, Any]):
        if self.mongo_db is None:
            self.mongo_db = await get_mongo_db()

        reading = SensorReading(device_id=device_id, **data)

        # 1. Append the raw reading to the time-series log
        await self.mongo_db.sensor_readings.insert_one(reading.model_dump())

        # 2. Update the matching embedded sensor's current state on the device document
        set_fields = {
            "sensors.$[s].last_value":   reading.value,
            "sensors.$[s].last_reading": reading.timestamp,
        }
        if "quality" in data:
            set_fields["sensors.$[s].last_quality"] = data["quality"]

        result = await self.mongo_db.devices.update_one(
            {"_id": device_id, "sensors.sensor_name": reading.sensor_name},
            {"$set": set_fields},
            array_filters=[{"s.sensor_name": reading.sensor_name}],
        )

        if result.matched_count == 0:
            # Device exists but has no embedded entry for this sensor yet — add one
            new_sensor = {
                "sensor_name":  reading.sensor_name,
                "sensor_type":  reading.sensor_type,
                "unit":         reading.unit,
                "last_reading": reading.timestamp,
                "last_value":   reading.value,
                "last_quality": data.get("quality"),
                "config":       None,
            }
            await self.mongo_db.devices.update_one(
                {"_id": device_id},
                {"$push": {"sensors": new_sensor}},
            )

        print(f"Stored sensor reading for device {device_id} / sensor {reading.sensor_name}")

    async def handle_actuator_data(self, device_id: str, data: Dict[str, Any]):
        if self.mongo_db is None:
            self.mongo_db = await get_mongo_db()

        # Store actuator log
        log_doc = {
            "device_id": device_id,
            "timestamp": data.get("timestamp"),
            **data
        }
        await self.mongo_db.actuator_logs.insert_one(log_doc)
        print(f"Stored actuator log for device {device_id}")

    def start(self, loop: Optional[asyncio.AbstractEventLoop] = None):
        self.loop = loop or asyncio.get_event_loop()

        if settings.mqtt_username:
            self.client.username_pw_set(settings.mqtt_username, settings.mqtt_password)

        self.client.connect(settings.mqtt_broker, settings.mqtt_port, 60)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

    def publish(self, topic: str, payload: Dict[str, Any]):
        self.client.publish(topic, json.dumps(payload))


# Global MQTT handler instance
mqtt_handler = MQTTHandler()
