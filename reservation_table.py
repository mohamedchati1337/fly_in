from typing import Dict, Tuple
from hub import Hub
from connection import Connection


class ReservationTable:
    """Manages spatial-temporal resource allocations."""

    def __init__(self) -> None:
        """Initializes internal tracking structures."""
        self.hubs: Dict[Tuple[str, int], int] = {}
        self.conns: Dict[Tuple[str, int], int] = {}

    def reserve_hub(self, hub: Hub, turn: int) -> None:
        """Reserves hub at turn."""
        key = (hub.name, turn)
        self.hubs[key] = self.hubs.get(key, 0) + 1

    def reserve_connection(self, name: str, turn: int) -> None:
        """Reserves link at turn."""
        key = (name, turn)
        self.conns[key] = self.conns.get(key, 0) + 1

    def is_hub_reserved(
        self,
        hub: Hub,
        turn: int,
        start: str,
        goal: str
    ) -> bool:
        """Checks structural hub reservation status against capacity."""
        if hub.name == start or hub.name == goal:
            return False
        usage = self.hubs.get((hub.name, turn), 0)
        return usage >= hub.max_drones

    def is_conn_reserved(
        self,
        conn: Connection,
        turn: int
    ) -> bool:
        """Checks connection reservation status against capacity."""
        usage = self.conns.get(
            (conn.name(), turn), 0
        )
        return usage >= conn.max_link_capacity
