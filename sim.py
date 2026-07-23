from typing import Any, List
import sys
from drone import Drone
from graph import Graph
from reservation_table import ReservationTable


class Simulator:
    """Manages spatial-temporal drone routing simulations."""

    def __init__(self, graph: Graph, visualizer: Any) -> None:
        """Initializes simulation components and entities."""
        self.graph = graph
        self.reservation = ReservationTable()
        self.turn = 0
        self.drones = self.create_drones()
        self.visualizer = visualizer
        self.visualizer.drones_list = self.drones
        self.visualizer.simulator = self

    def create_drones(self) -> List[Drone]:
            """Calculates collision-free optimal flight paths.

            Returns:
                List[Drone]: A list of scheduled Drone objects.
            """
            drones: List[Drone] = []
            start = self.graph.start_hub
            goal = self.graph.goal_hub

            if not start or not goal:
                print("Error: Start or Goal hub is not defined in the graph.")
                sys.exit(1)

            for i in range(self.graph.drone_count):
                path = self.graph.dijkstra(
                    start,
                    goal,
                    self.reservation
                )

                if not path:
                    if i == 0:
                        print("Error: No static path exists between zones.")
                    else:
                        print(f"Drone {i + 1} blocked at Hub: {start} after 0 turns.")
                    sys.exit(1)

                t_idx = 0
                for idx, name in enumerate(path):
                    if idx > 0:
                        hub = self.graph.hubs[name]
                        prev = path[idx - 1]

                        if prev == name:
                            t_idx += 1
                            if name != start and name != goal:
                                self.reservation.reserve_hub(hub, t_idx)
                            continue

                        edge = self.graph.find_connection(prev, name)
                        cost = 2 if hub.type_zone == "restricted" else 1

                        if edge:
                            self.reservation.reserve_connection(edge.name(), t_idx)
                            if cost == 2:
                                self.reservation.reserve_connection(edge.name(), t_idx + 1)

                        t_idx += cost

                        if name != start and name != goal:
                            self.reservation.reserve_hub(hub, t_idx)

                drone = Drone(drone_id=i + 1, path=path)
                drones.append(drone)

            return drones

    def all_finished(self) -> bool:
        """Checks if simulation completed entirely."""
        return all(d.finished() for d in self.drones)

    def step_turn(self) -> List[str]:
        """Executes one simulation step manually."""
        moves: List[str] = []
        for d in self.drones:
            if d.finished():
                continue
            if d.in_flight:
                d.finish_flight()
                if not d.in_flight:
                    moves.append(f"{d.name}-{d.current_hub_name()}")
                else:
                    nxt = d.next_hub_name()
                    if nxt:
                        edge = self.graph.find_connection(
                            d.current_hub_name(), nxt
                        )
                        p1 = d.current_hub_name()
                        e_name = edge.name() if edge else f"{p1}-{nxt}"
                        moves.append(f"{d.name}-{e_name}")
            else:
                nxt = d.next_hub_name()
                if nxt and nxt == d.current_hub_name():
                    d.pos += 1
                elif nxt:
                    hub = self.graph.hubs[nxt]
                    occupied = 0
                    for other in self.drones:
                        if (
                            not other.in_flight
                            and other.current_hub_name() == nxt
                        ):
                            occupied += 1

                    # If the hub is full, wait
                    if occupied >= hub.max_drones:
                        continue

                    is_res = hub.type_zone == "restricted"
                    d.move(is_res)
                    d.finish_flight()
                    if not d.in_flight:
                        moves.append(f"{d.name}-{d.current_hub_name()}")
                    else:
                        edge = self.graph.find_connection(
                            d.path[d.pos - 1], nxt
                        )
                        p2 = d.path[d.pos - 1]
                        e_name = edge.name() if edge else f"{p2}-{nxt}"
                        moves.append(f"{d.name}-{e_name}")
        return moves

    def run(self) -> None:
        """Delegates lifecycle control to visualizer."""
        while not self.all_finished():
            self.turn += 1
            t_m = self.step_turn()
            if t_m:
                print(" ".join(t_m))
