from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.dependencies import get_current_user, require_role
from src.database.mongodb import database as mongo_db
from src.esphome.manager import esphome_manager
from src.esphome.schemas import (
    ESPHomeConnectRequest,
    ESPHomeConnectionStatus,
    ESPHomeEntityInfo,
    ESPHomeLightCommand,
    ESPHomeSwitchCommand,
)
from src.users.models import RoleEnum, User

router = APIRouter()


# ── Connection management ───────────────────────────────────────────────────

@router.post("/{device_id}/connect", status_code=status.HTTP_200_OK)
async def connect_device(
    device_id: str,
    body:      ESPHomeConnectRequest,
    _:         User = Depends(require_role(RoleEnum.admin)),
):
    """Connect to an ESPHome device via the native API. Admin only."""
    try:
        await esphome_manager.connect(device_id, body.host, body.port, body.password)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    return {"device_id": device_id, "host": body.host, "port": body.port, "connected": True}


@router.delete("/{device_id}/disconnect", status_code=status.HTTP_200_OK)
async def disconnect_device(
    device_id: str,
    _:         User = Depends(require_role(RoleEnum.admin)),
):
    """Disconnect from an ESPHome device. Admin only."""
    if not esphome_manager.is_connected(device_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not connected")
    await esphome_manager.disconnect(device_id)
    return {"device_id": device_id, "connected": False}


@router.get("/status", response_model=List[ESPHomeConnectionStatus])
async def list_connections(
    _: User = Depends(get_current_user),
):
    """List all currently connected ESPHome devices."""
    return esphome_manager.list_connections()


# ── Entity discovery ────────────────────────────────────────────────────────

@router.get("/{device_id}/entities", response_model=List[ESPHomeEntityInfo])
async def list_entities(
    device_id: str,
    _:         User = Depends(get_current_user),
):
    """Return all entities exposed by a connected ESPHome device."""
    entities = esphome_manager.get_entities(device_id)
    if entities is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not connected")
    return entities


# ── State history from MongoDB ──────────────────────────────────────────────

@router.get("/{device_id}/states")
async def get_latest_states(
    device_id: str,
    _:         User = Depends(get_current_user),
):
    """Return the latest state for every entity of a device (from MongoDB)."""
    cursor = mongo_db.esphome_states.find({"device_id": device_id}, {"_id": 0})
    docs = [doc async for doc in cursor]
    if not docs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No states found for this device")
    return docs


@router.get("/{device_id}/readings")
async def get_state_readings(
    device_id: str,
    limit:     int = 100,
    _:         User = Depends(get_current_user),
):
    """Return the most recent time-series state readings for a device."""
    cursor = (
        mongo_db.esphome_readings
        .find({"device_id": device_id}, {"_id": 0})
        .sort("timestamp", -1)
        .limit(limit)
    )
    return [doc async for doc in cursor]


# ── Device control ──────────────────────────────────────────────────────────

@router.post("/{device_id}/switch/{key}/control")
async def control_switch(
    device_id: str,
    key:       int,
    body:      ESPHomeSwitchCommand,
    _:         User = Depends(require_role(RoleEnum.technician)),
):
    """Turn a switch on or off. Requires technician role or above."""
    if not esphome_manager.is_connected(device_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not connected")
    try:
        await esphome_manager.switch_command(device_id, key, body.state)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    return {"device_id": device_id, "key": key, "state": body.state}


@router.post("/{device_id}/light/{key}/control")
async def control_light(
    device_id: str,
    key:       int,
    body:      ESPHomeLightCommand,
    _:         User = Depends(require_role(RoleEnum.technician)),
):
    """Control a light entity (on/off, brightness, RGB, color temp). Requires technician role or above."""
    if not esphome_manager.is_connected(device_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not connected")
    try:
        await esphome_manager.light_command(
            device_id,
            key,
            body.state,
            brightness=body.brightness,
            red=body.red,
            green=body.green,
            blue=body.blue,
            color_temp=body.color_temp,
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    return {"device_id": device_id, "key": key, **body.model_dump()}
