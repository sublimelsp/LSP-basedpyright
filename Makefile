MAKEFLAGS += --silent

.PHONY: all
all:

.PHONY: ci-check
ci-check:
 	# mypy -p plugin
	echo "Check: ruff (lint)"
	ruff check --diff .
	echo "Check: ruff (format)"
	ruff format --diff .

.PHONY: ci-fix
ci-fix:
	echo "Fix: ruff (lint)"
	ruff check --fix .
	echo "Fix: ruff (format)"
	ruff format .

.PHONY: update-schema
update-schema:
	python3 ./scripts/update_schema.py
