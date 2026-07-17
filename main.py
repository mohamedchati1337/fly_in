import sys
from typing import Dict, List, Optional
from drone import Drone
from simulator import Simulator


class MockHub:
    """Mock Hub class matching the requirements of the simulation system."""

    def __init__(self, name: str, type_zone: str) -> None:
        """Initializes a hub object."""
        self.name: str = name
        self.type_zone: str = type_zone


class MockConnection:
    """Mock Connection/Edge class matching the simulator layout."""

    def __init__(self, u: str, v: str) -> None:
        """Initializes a simple route connection."""
        self.u: str = u
        self.v: str = v

    def name(self) -> str:
        """Returns the structural name format of the connection route."""
        return f"{self.u}-{self.v}"


class MockGraph:
    """Mock Graph containing deterministic routing responses for validation."""

    def __init__(self) -> None:
        """Sets up default hub metrics and counts."""
        self.drone_count: int = 2
        self.start_hub: str = "roof1"
        self.goal_hub: str = "roof2"
        self.hubs: Dict[str, MockHub] = {
            "roof1": MockHub("roof1", "normal"),
            "corridorA": MockHub("corridorA", "restricted"),
            "roof2": MockHub("roof2", "normal"),
        }

    def dijkstra(
        self, start: str, goal: str, reservation: getattr(sys.modules[__name__], 'Any', None)
    ) -> Optional[List[str]]:
        """Returns pre-calculated spatio-temporal simulation paths."""
        # Drone 1 path (Fastest direct path)
        if not reservation.reserved_hubs and not reservation.reserved_connections:
            return ["roof1", "corridorA", "roof2"]
        
        # Drone 2 path (Includes a wait turn at roof1 because corridorA is occupied)
        return ["roof1", "roof1", "corridorA", "roof2"]

    def find_connection(self, u: str, v: str) -> Optional[MockConnection]:
        """Validates structural link options between points."""
        valid_links = {
            ("roof1", "corridorA"), ("corridorA", "roof2"),
            ("roof1", "roof1")
        }
        if (u, v) in valid_links or (v, u) in valid_links:
            return MockConnection(u, v)
        return None


def main() -> None:
    """Assembles framework modules and executes runtime verification."""
    # Build components
    graph = MockGraph()
    visualizer = None

    print("Initializing Simulation and calculating paths...")
    # Injecting mocks matching type signatures expected by Simulator
    sim = Simulator(graph=graph, visualizer=visualizer)  # type: ignore

    print("\n--- Simulation Started ---")
    sim.run()
    print("--- Simulation Finished ---")


if __name__ == "__main__":
    main()