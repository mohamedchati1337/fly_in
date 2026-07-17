from typing import Any, List


class State:
    """Represents pathfinding search queue state."""

    def __init__(
        self,
        hub: str,
        turn: int,
        cost: int,
        path: List[str],
        priority_score: int = 1
    ) -> None:
        """Initializes route search state values."""
        self.hub: str = hub
        self.turn: int = turn
        self.cost: int = cost
        self.path: List[str] = path
        self.priority_score: int = priority_score

    def __lt__(self, other: Any) -> bool:
        """Compares states based on cost."""
        if not isinstance(other, State):
            return NotImplemented

        if self.cost != other.cost:
            return self.cost < other.cost
        return self.priority_score < other.priority_score
