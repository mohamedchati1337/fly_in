"""Main entry point for the Fly In drone fleet simulator."""

import sys
from typing import Optional

from graph import Graph
from parser import MapParser
from sim import Simulator
from visualizer import Visualizer


def main() -> None:
    """Parses input map, initializes simulation, and launches visualizer."""
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <map_file>")
        sys.exit(1)
    map_file: str = sys.argv[1]
    parser: MapParser = MapParser()
    try:
        parser.parse_file(map_file)
    except Exception as e:
        print(f"Error parsing map file '{map_file}': {e}", file=sys.stderr)
        sys.exit(1)

    graph: Graph = Graph()
    graph.load_from_parser(parser)
    visualizer: Optional[Visualizer] = None
    try:
        visualizer = Visualizer(graph)
    except Exception as e:
        print(
            f"Warning: Could not initialize visualizer ({e}). "
            "Falling back to headless execution.",
            file=sys.stderr,
        )
    simulator: Simulator = Simulator(graph, visualizer)
    if visualizer:
        visualizer.simulator = simulator
        if hasattr(simulator, "drones"):
            visualizer.drones_list = simulator.drones
        try:
            while True:
                visualizer.update()
        except (KeyboardInterrupt, SystemExit):
            print("\nSimulation terminated cleanly.")
            sys.exit(0)
    else:
        print("Running simulation in headless mode...")
        turn: int = 1
        while not simulator.all_finished():
            moves = simulator.step_turn()
            if moves:
                print(f"Turn {turn}: " + " ".join(moves))
            turn += 1
        print("Simulation complete.")


if __name__ == "__main__":
    main()
