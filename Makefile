.PHONY: help run dev test lint format install clean

help:
	@echo "Antigravity Reader — Development Tasks"
	@echo "-------------------------------------"
	@echo "  make run        Run the web server"
	@echo "  make test       Run test suite"
	@echo "  make dev        Install package in editable mode"
	@echo "  make lint       Check code formatting and linting"
	@echo "  make format     Auto-format code"
	@echo "  make clean      Remove python caches and build artifacts"

run:
	./start.sh

test:
	PYTHONPATH=src python3 -m unittest discover -s tests -p "test_*.py"

dev:
	pip install -e .

lint:
	python3 -m py_compile server.py src/antigravity_reader/*.py tests/*.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build/ dist/ *.egg-info .pytest_cache/
