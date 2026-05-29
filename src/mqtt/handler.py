import json
import asyncio
from typing import Dict, Any
import paho.mqtt.client as mqtt
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.config.settings import settings
from src.database.mongodb import get_mongo_db


class MQTTHandler:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.mongo_db = None

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT broker with result code {rc}")
        # Subscribe to topics
        self.client.subscribe("domotica/sensores/#")
        self.client.subscribe("domotica/actuadores/#")

    def on_message(self, client, userdata, msg):
        print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
        asyncio.create_task(self.process_message(msg.topic, msg.payload.decode()))

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

    async def handle_sensor_data(self, sensor_id: str, data: Dict[str, Any]):
        if not self.mongo_db:
            self.mongo_db = await get_mongo_db()

        # Store sensor reading
        reading_doc = {
            "sensor_id": int(sensor_id),
            "timestamp": data.get("timestamp"),
            **data
        }
        await self.mongo_db.sensor_readings.insert_one(reading_doc)
        print(f"Stored sensor reading for sensor {sensor_id}")

    async def handle_actuator_data(self, actuator_id: str, data: Dict[str, Any]):
        if not self.mongo_db:
            self.mongo_db = await get_mongo_db()

        # Store actuator log
        log_doc = {
            "actuator_id": int(actuator_id),
            "timestamp": data.get("timestamp"),
            **data
        }
        await self.mongo_db.actuator_logs.insert_one(log_doc)
        print(f"Stored actuator log for actuator {actuator_id}")

    def start(self):
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