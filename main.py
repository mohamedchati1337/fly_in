import sys
from graph import Graph
from parser import MapParser
from sim import Simulator


def load_map_and_run(file_path: str) -> None:
    """Loads the map file using MapParser, initializes structures, and runs simulation."""
    # 1. بنية الـ Parser وقراءة الملف
    map_parser = MapParser()
    map_parser.parse_file(file_path)

    # 2. تحضير الـ Graph وتمرير البيانات ليه من الـ parser
    graph = Graph()
    graph.load_from_parser(map_parser)

    # 3. إعداد الـ Simulator (كنصيفطو ليه الـ graph و None ف الـ visualizer)
    simulator = Simulator(graph=graph, visualizer=None)

    print(f"--- Loading Map: {file_path} ---")
    print(f"Total Drones to schedule: {graph.drone_count}")
    print("Calculating collision-free paths...\n")

    # 4. طباعة المسارات اللي ديجا تحسبات وسط الـ __init__ ديال Simulator
    print("--- Final Scheduled Paths ---")
    for drone in simulator.drones:
        path_str = " -> ".join(drone.path)
        print(f"Drone {drone.id}: {path_str}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <map_file_path>")
        sys.exit(1)

    map_file = sys.argv[1]
    load_map_and_run(map_file)