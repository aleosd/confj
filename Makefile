default: help

SRC_DIR := ./confj
TESTS_DIR := ./tests

ALL_CODE := $(SRC_DIR) $(TESTS_DIR)

.PHONY: fmt
fmt:  # sort imports and format the projects' source
	ruff check --select I --fix $(ALL_CODE)
	ruff format $(ALL_CODE)

.PHONY: verify
verify:  # lint (check) the project
	ruff format --check $(ALL_CODE)
	ruff check $(SRC_DIR)
	pyright $(ALL_CODE)

.PHONY: test
test: # run tests with pytest
	coverage run -m pytest $(TESTS_DIR) --showlocals -s -v
	coverage report -m

.PHONY: help
help: # Show help for each of the Makefile recipes.
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done
