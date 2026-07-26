PYTHON   = python3
APP      = main.py
MAP     ?= maps/easy/01_linear_path.txt
SRC      = sim.py visualizer.py graph.py drone.py parser.py connection.py hub.py reservation_table.py main.py

.PHONY: all install run lint clean

all: install lint run

install:
	pip3 install pygame mypy flake8

run:
	$(PYTHON) $(APP) $(MAP)

lint:
	@mypy --strict $(SRC)
	@flake8 $(SRC)

clean:
	rm -rf __pycache__ .mypy_cache