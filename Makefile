CODE_DIR=domino_tf_base_schemas
TESTS_DIR=tests

black:
	black --check --diff $(CODE_DIR) $(TESTS_DIR)

black-fix:
	black $(CODE_DIR) $(TESTS_DIR)

ruff:
	ruff check $(CODE_DIR) $(TESTS_DIR)

ruff-fix:
	ruff check --fix $(CODE_DIR) $(TESTS_DIR)

mypy:
	mypy --follow-imports=silent $(CODE_DIR) $(TESTS_DIR)

pytest:
	coverage run --source $(CODE_DIR) -m pytest -v $(TESTS_DIR)
	coverage report -m --fail-under=80

checks: black ruff mypy pytest
