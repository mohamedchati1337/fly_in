import sys
from parser import MapParser
from graph import Graph
from sim import Simulator
from visualizer import Visualizer


def main() -> None:
    """Executes main application startup sequence."""
    if len(sys.argv) < 2:
        print("Usage: python3 app.py <map_file>")
        sys.exit(1)

    map_file = sys.argv[1]

    parser = MapParser()
    parser.parse_file(map_file)

    graph = Graph()
    graph.load_from_parser(parser)

    visualizer = Visualizer(graph)

    simulator = Simulator(graph, visualizer)
    simulator.run()


if __name__ == "__main__":
    main()