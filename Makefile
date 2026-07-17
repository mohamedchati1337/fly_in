# Variables
PYTHON   = python3
APP      = app.py
SRC      = app.py sim.py visualizer.py graph.py drone.py parser.py connection.py hub.py reservation_table.py

.PHONY: all install run lint clean

all: install lint run

install:
	pip3 install pygame mypy flake8

run:
	$(PYTHON) $(APP)

lint:
	mypy --strict $(SRC)
	flake8 $(SRC)

clean:
	rm -rf __pycache__ .mypy_cache