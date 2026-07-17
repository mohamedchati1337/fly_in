class Connection:
    """Represents bidirectional spatial edge paths."""

    def __init__(
        self,
        hub_u: str,
        hub_v: str,
        max_link_capacity: int = 1
    ) -> None:
        """Initializes spatial link capacities."""
        self.hub_u: str = hub_u
        self.hub_v: str = hub_v
        self.max_link_capacity: int = max_link_capacity

    def name(self) -> str:
        """Generates standard tracking path string."""
        if self.hub_u < self.hub_v:
            return f"{self.hub_u}-{self.hub_v}"
        return f"{self.hub_v}-{self.hub_u}"
