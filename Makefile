# Development
format-all:
	@isort . \
		--skip setup.py \
		--skip .venv \
		--skip build \
		--skip dist \
		--skip __pycache__ \
		--skip docs \
		--skip static \
		--skip .conda
	@black . \
		--exclude setup.py \
		--exclude .venv \
		--exclude build \
		--exclude dist \
		--exclude __pycache__ \
		--exclude docs \
		--exclude static \
		--exclude .conda

install-all:
	poetry install -E all --with dev

update-all:
	poetry update
	poetry export --without-hashes -f requirements.txt --output requirements.txt
	poetry export --without-hashes --all-groups --all-extras -f requirements.txt --output requirements-all.txt

# Docs
mkdocs:
	mkdocs serve

# Tests
pytest:
	python -m pytest --cov=inspect_function --cov-config=.coveragerc --cov-report=xml:coverage.xml
