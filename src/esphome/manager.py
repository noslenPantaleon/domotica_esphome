import asyncio
import logging
from typing import Any, Dict, List, Optional

from aioesphomeapi import APIClient
from aioesphomeapi.model import (
    BinarySensorInfo,
    ClimateInfo,
    CoverInfo,
    FanInfo,
    LightInfo,
    NumberInfo,
    SelectInfo,
    SensorInfo,
    SwitchInfo,
    TextSensorInfo,
)

from src.database.mongodb import database as mongo_db
from src.esphome.schemas import ESPHomeStateRecord

logger = logging.getLogger(__name__)

_ENTITY_TYPE = {
    SensorInfo:       "sensor",
    BinarySensorInfo: "binary_sensor",
    SwitchInfo:       "switch",
    LightInfo:        "light",
    ClimateInfo:      "climate",
    CoverInfo:        "cover",
    FanInfo:          "fan",
    TextSensorInfo:   "text_sensor",
    NumberInfo:       "number",
    SelectInfo:       "select",
}


class _Connection:
    """Internal entry for one active ESPHome device connection."""

    def __init__(self, client: APIClient, host: str, port: int):
        self.client   = client
        self.host     = host
        self.port     = port
        # key (int) -> {name, object_id, entity_type, unit}
        self.entities: Dict[int, dict] = {}


class ESPHomeManager:
    """
    Manages persistent aioesphomeapi connections.
    One connection per device_id; device_id maps to the MongoDB _id.
    """

    def __init__(self):
        self._connections: Dict[str, _Connection] = {}

    # ── Public lifecycle ────────────────────────────────────────────────────

    async def connect(self, device_id: str, host: str, port: int, password: str) -> None:
        if device_id in self._connections:
            await self.disconnect(device_id)

        client = APIClient(host, port, password)
        await client.connect(login=True)

        conn = _Connection(client, host, port)
        await self._load_entities(conn)

        # subscribe_states is synchronous in aioesphomeapi v10+
        client.subscribe_states(
            lambda state: asyncio.ensure_future(self._on_state(device_id, state))
        )

        self._connections[device_id] = conn
        logger.info("ESPHome connected: %s (%s:%d) — %d entities", device_id, host, port, len(conn.entities))

    async def disconnect(self, device_id: str) -> None:
        conn = self._connections.pop(device_id, None)
        if conn:
            try:
                await conn.client.disconnect()
            except Exception:
                pass
            logger.info("ESPHome disconnected: %s", device_id)

    async def disconnect_all(self) -> None:
        for device_id in list(self._connections):
            await self.disconnect(device_id)

    # ── Query helpers ───────────────────────────────────────────────────────

    def list_connections(self) -> List[dict]:
        return [
            {
                "device_id":    did,
                "host":         c.host,
                "port":         c.port,
                "connected":    True,
                "entity_count": len(c.entities),
            }
            for did, c in self._connections.items()
        ]

    def get_entities(self, device_id: str) -> Optional[List[dict]]:
        conn = self._connections.get(device_id)
        if not conn:
            return None
        return [
            {
                "key":         key,
                "name":        meta["name"],
                "object_id":   meta["object_id"],
                "entity_type": meta["entity_type"],
                "unit":        meta["unit"],
            }
            for key, meta in conn.entities.items()
        ]

    def is_connected(self, device_id: str) -> bool:
        return device_id in self._connections

    # ── Device commands ─────────────────────────────────────────────────────

    def switch_command(self, device_id: str, key: int, state: bool) -> None:
        client = self._get_client(device_id)
        client.switch_command(key=key, state=state)

    def light_command(
        self,
        device_id:  str,
        key:        int,
        state:      bool,
        brightness: Optional[float] = None,
        red:        Optional[float] = None,
        green:      Optional[float] = None,
        blue:       Optional[float] = None,
        color_temp: Optional[float] = None,
    ) -> None:
        client = self._get_client(device_id)
        kwargs: Dict[str, Any] = {"key": key, "state": state}
        if brightness  is not None: kwargs["brightness"]        = brightness
        if red         is not None: kwargs["red"]               = red
        if green       is not None: kwargs["green"]             = green
        if blue        is not None: kwargs["blue"]              = blue
        if color_temp  is not None: kwargs["color_temperature"] = color_temp
        client.light_command(**kwargs)

    # ── Internal ────────────────────────────────────────────────────────────

    def _get_client(self, device_id: str) -> APIClient:
        conn = self._connections.get(device_id)
        if not conn:
            raise KeyError(f"Device '{device_id}' is not connected")
        return conn.client

    async def _load_entities(self, conn: _Connection) -> None:
        entities, _ = await conn.client.list_entities_services()
        for entity in entities:
            entity_type = _ENTITY_TYPE.get(type(entity), "unknown")
            conn.entities[entity.key] = {
                "name":        entity.name,
                "object_id":   entity.object_id,
                "entity_type": entity_type,
                "unit":        getattr(entity, "unit_of_measurement", None) or None,
            }

    async def _on_state(self, device_id: str, state: Any) -> None:
        conn = self._connections.get(device_id)
        if not conn:
            return

        meta = conn.entities.get(state.key)
        if not meta:
            return

        record = ESPHomeStateRecord(
            device_id=device_id,
            key=state.key,
            entity_name=meta["name"],
            entity_type=meta["entity_type"],
            state=getattr(state, "state", None),
            unit=meta["unit"],
        )
        doc = record.model_dump()

        # Upsert latest state (one document per device+entity)
        await mongo_db.esphome_states.update_one(
            {"device_id": device_id, "key": state.key},
            {"$set": doc},
            upsert=True,
        )

        # Append to time-series log
        await mongo_db.esphome_readings.insert_one(doc)

        logger.debug("ESPHome state: %s / %s = %s", device_id, meta["name"], record.state)


esphome_manager = ESPHomeManager()
