from typing import List, Optional


class Drone:
    """Tracks active drone simulation states."""

    def __init__(self, drone_id: int, path: List[str]) -> None:
        """Initializes individual drone properties."""
        self.id: int = drone_id
        self.name: str = f"D{drone_id}"
        self.path: List[str] = path
        self.pos: int = 0
        self.turns_left: int = 0

    @property
    def in_flight(self) -> bool:
        """Checks if drone is traveling."""
        return self.turns_left > 0

    def current_hub_name(self) -> str:
        """Gets the name of the current active hub."""
        return self.path[self.pos]

    def next_hub_name(self) -> Optional[str]:
        """Gets the name of the next target destination hub."""
        if self.pos + 1 >= len(self.path):
            return None
        return self.path[self.pos + 1]

    def finished(self) -> bool:
        """Checks if destination is reached."""
        return self.pos == len(self.path) - 1

    def move(self, is_restricted: bool) -> None:
        """Initiates movement toward target."""
        self.turns_left = 2 if is_restricted else 1

    def finish_flight(self) -> bool:
        """Decrements flight time remaining and advances position when arrived."""
        if self.turns_left > 0:
            self.turns_left -= 1
            if self.turns_left == 0:
                self.pos += 1
                return True
        return False