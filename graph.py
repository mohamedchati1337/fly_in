from __future__ import annotations
import heapq
from typing import Dict, List, Tuple, Optional, TYPE_CHECKING, Any
from hub import Hub
from connection import Connection
from state import State

if TYPE_CHECKING:
    from parser import MapParser
    from reservation_table import ReservationTable


class Graph:
    """Manages navigation network topology layout."""

    def __init__(self) -> None:
        """Initializes system topology data stores."""
        self.hubs: Dict[str, Hub] = {}
        self.connections: Dict[Tuple[str, str], Connection] = {}
        self.connections_list: List[Connection] = []
        self.hubs_list: List[Hub] = []

        self.start_hub: Optional[str] = None
        self.goal_hub: Optional[str] = None
        self.drone_count: int = 0
        self.simulator_instance: Optional[Any] = None
        self.graph

    def load_from_parser(self, parser: MapParser) -> None:
        """Hydrates graph state from parser."""
        self.hubs = parser.hubs
        self.connections = parser.connections
        self.start_hub = parser.start_zone
        self.goal_hub = parser.end_zone
        self.drone_count = parser.drone_count
        self.hubs_list = list(self.hubs.values())
        self.connections_list = list(self.connections.values())

    def find_connection(self, hub_u: str, hub_v: str) -> Optional[Connection]:
        """Finds connection between two hubs."""
        key = (hub_u, hub_v) if hub_u < hub_v else (hub_v, hub_u)
        return self.connections.get(key)

    def get_neighbors(
        self, current_hub: str
    ) -> List[Tuple[str, int, Connection]]:
        """Returns adjacent spatial link neighbors."""
        neighbors: List[Tuple[str, int, Connection]] = []
        for conn in self.connections_list:
            if current_hub != conn.hub_u and current_hub != conn.hub_v:
                continue

            neighbor = conn.hub_v if conn.hub_u == current_hub else conn.hub_u
            dest_hub = self.hubs[neighbor]
            move_cost = 2 if dest_hub.type_zone == "restricted" else 1

            neighbors.append((neighbor, move_cost, conn))

        return neighbors

    def path_cost(self, path: List[str]) -> int:
        """Calculates total weighted path cost."""
        cost = 0
        for i in range(len(path) - 1):
            next_hub = self.hubs[path[i + 1]]
            cost += 2 if next_hub.type_zone == "restricted" else 1
        return cost

    def dijkstra(
        self,
        start: str,
        end: str,
        reservation_table: Optional[ReservationTable] = None,
    ) -> Optional[List[str]]:
        """Executes space-time path planning sequence."""
        queue: List[State] = []

        start_state = State(
            hub=start,
            turn=0,
            cost=0,
            path=[start]
        )

        heapq.heappush(queue, start_state)
        best_cost: Dict[Tuple[str, int], int] = {}

        while queue:
            current = heapq.heappop(queue)
            if current.hub == end:
                return current.path

            state_key = (current.hub, current.turn)
            if state_key in best_cost and best_cost[state_key] <= current.cost:
                continue
            best_cost[state_key] = current.cost
            if reservation_table:
                next_turn_wait = current.turn + 1
                if not reservation_table.is_hub_reserved(
                    self.hubs[current.hub], next_turn_wait
                ):
                    wait_state = State(
                        hub=current.hub,
                        turn=next_turn_wait,
                        cost=current.cost + 1,
                        path=current.path + [current.hub]
                    )
                    heapq.heappush(queue, wait_state)

            neighbors = self.get_neighbors(current.hub)
            for neighbor, move_cost, conn in neighbors:
                new_turn = current.turn + 1

                if reservation_table:
                    if reservation_table.is_hub_reserved(
                        self.hubs[neighbor], new_turn
                    ):
                        continue
                    if reservation_table.is_conn_reserved(conn, current.turn):
                        continue

                new_state = State(
                    hub=neighbor,
                    turn=new_turn,
                    cost=current.cost + move_cost,
                    path=current.path + [neighbor]
                )
                heapq.heappush(queue, new_state)

        return None