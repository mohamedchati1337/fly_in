from typing import Dict
from hub import Hub
from connection import Connection
from graph import Graph


class ReservationTable:
    """Manages spatial-temporal resource allocations."""

    def __init__(self) -> None:
        """Initializes internal tracking structures."""
        self.hubs: Dict[tuple[str, int], int] = {}
        self.conns: Dict[tuple[str, int], int] = {}

    def reserve_hub(self, name: str, turn: int) -> None:
        """Reserves hub at turn."""
        key = (name, turn)
        self.hubs[key] = self.hubs.get(key, 0) + 1

    def reserve_connection(self, name: str, turn: int) -> None:
        """Reserves link at turn."""
        key = (name, turn) 
        self.conns[key] = self.conns.get(key, 0) + 1

    def is_hub_reserved(self, hub: Hub, turn: int, start: str, goal: str) -> bool:
        """Checks structural hub reservation status against capacity."""
        if hub.name == start or hub.name == goal:
            return False
        usage = self.hubs.get((hub.name, turn), 0)
        return usage >= hub.max_drones

    def is_conn_reserved(self, conn: Connection, turn: int) -> bool:
        """Checks connection reservation status against capacity."""
        usage = self.conns.get(
                    (conn.name(), turn), 0
                )
        return usage >= conn.max_link_capacity