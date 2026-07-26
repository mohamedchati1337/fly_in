*This project has been created as part of the 42 curriculum by [mchati].*

# Fly In

## Description

Fly In is a drone traffic simulation project developed as part of the 42 curriculum.

The goal is to move multiple drones from a starting hub to a goal hub while respecting the limitations of the network.

The project uses a graph made of hubs and connections. Hubs can have capacity limits, connections can have link capacity limits, and some zones can require more than one turn to cross.

The main challenge is to find efficient paths for multiple drones while avoiding conflicts and minimizing the number of simulation turns.

---

## Features

* Graph-based map representation.
* Multiple drone management.
* Dijkstra pathfinding.
* Space-time pathfinding using hub and turn.
* Hub capacity management.
* Connection capacity management.
* Waiting when movement is not possible.
* Restricted zones with different movement costs.
* Reservation system for scheduled drones.
* Turn-based simulation.
* Pygame visualization.

---

## Algorithm

### Dijkstra

The project uses Dijkstra's algorithm to find efficient paths between the start and goal hubs.

A priority queue is used to process the states with the lowest cost first.

The algorithm considers movement costs and checks whether a movement is possible before adding a new state.

### Space-Time Pathfinding

Because several drones use the same network, the current position alone is not enough.

The algorithm considers:

```text
Hub + Turn
```

This allows the system to know when a hub or connection is available.

### State

The pathfinding algorithm uses a `State` object containing information about:

* Current hub.
* Current turn.
* Path cost.
* Path.
* Priority.

### Waiting

When a drone cannot move because of a capacity or reservation conflict, the algorithm can consider waiting at its current hub.

### Avoiding Conflicts

The algorithm checks existing reservations before allowing a drone to use a hub or connection.

This helps prevent capacity violations and conflicts between drones.

---

## Reservation System

The reservation system keeps track of resource usage over time.

It manages:

* Hub reservations.
* Connection reservations.
* Hub capacity.
* Connection capacity.
* Turn-based resource usage.

When planning a new drone, existing reservations are considered so that drones can share the network safely.

---

## Simulation

The simulation manages the drones after their paths have been calculated.

It is responsible for:

* Creating drones.
* Assigning paths.
* Managing turns.
* Moving drones.
* Detecting when drones reach the goal.

The pathfinding and reservation logic are kept separate from the visual representation.

---

## Visual Representation

The project includes a Pygame visualizer.

It displays:

* Hubs.
* Connections.
* Drones.
* Drone movement.
* Hub and connection information.

The visualizer makes the simulation easier to understand and helps with debugging the pathfinding and scheduling logic.

---

## Project Structure

The project is divided into several components:

```text
graph.py              Graph and pathfinding
hub.py                Hub representation
connection.py         Connection representation
state.py              Pathfinding state
reservation_table.py  Resource reservations
drone.py              Drone representation
simulation.py         Simulation logic
visualizer.py         Pygame visualization
main.py               Program entry point
```

---

## Installation

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## Instructions

Run the project with:

```bash
python3 main.py
```

If a map file is required:

```bash
python3 main.py <map_file>
```

The exact command depends on the arguments implemented by the final version of the project.

---

## Testing

The project should be tested with different situations, including:

* One drone.
* Multiple drones.
* Full hubs.
* Full connections.
* Restricted zones.
* Waiting situations.
* Multiple possible paths.
* Maps where no valid path exists.

These tests help verify that the pathfinding and reservation systems work correctly.

---

## Technical Choices

### Python

Python was chosen because it provides clear syntax, useful data structures, type hints, and good support for rapid development.

### Dijkstra

Dijkstra is suitable because the project contains different movement costs.

### Priority Queue

Python's `heapq` is used to efficiently select the state with the lowest cost.

### Space-Time Search

The project uses hub and turn together because resource availability can change during the simulation.

---

## Resources

The following resources were used during development:

* Python Documentation — https://docs.python.org/3/
* Python `heapq` Documentation — https://docs.python.org/3/library/heapq.html
* Dijkstra's Algorithm — https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
* Pygame Documentation — https://www.pygame.org/docs/

These resources were used to understand Python features, priority queues, graph algorithms, and graphical programming.

### AI Usage

AI was used as a development and learning assistant for:

* Understanding Dijkstra and space-time pathfinding.
* Discussing reservation and capacity logic.
* Debugging code and errors.
* Reviewing code structure.
* Improving project documentation and English.

The code was tested, modified, and integrated according to the project's requirements.

---

## Implementation Strategy

The project was developed in separate stages:

```text
Map Parsing
     ↓
Graph
     ↓
Pathfinding
     ↓
Reservation System
     ↓
Drone Scheduling
     ↓
Simulation
     ↓
Visualization
```

This structure keeps the different responsibilities separated and makes the project easier to develop and debug.

---

## Future Improvements

Possible improvements include:

* Better path optimization.
* Improved scheduling for large numbers of drones.
* Better deadlock handling.
* More advanced visualization.
* Performance improvements.

---

## Conclusion

Fly In combines graph algorithms, pathfinding, resource management, simulation, and visualization.

The project demonstrates how Dijkstra can be adapted to handle multiple drones, time, capacities, and conflicts in a shared network.
