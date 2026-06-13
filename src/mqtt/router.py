from fastapi import APIRouter
from src.mqtt.handler import mqtt_handler

router = APIRouter()


@router.get("/status")
async def get_mqtt_status():
    return {
        "connected": mqtt_handler.client.is_connected()
    }


@router.post("/publish/{topic:path}")
async def publish_message(topic: str, payload: dict):
    mqtt_handler.publish(f"domotica/{topic}", payload)
    return {"message": f"Published to domotica/{topic}"}
