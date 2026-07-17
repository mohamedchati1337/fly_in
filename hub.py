from typing import Tuple


class Hub:
    """Represents a network node location zone."""

    def __init__(
        self,
        name: str,
        coordinates: Tuple[int, int],
        type_zone: str = "normal",
        max_drones: int = 1,
        color: str = "none"
    ) -> None:
        """Initializes structural zone parameters."""
        self.name: str = name
        self.coordinates: Tuple[int, int] = coordinates
        self.type_zone: str = type_zone
        self.max_drones: int = max_drones
        self.color: str = color
