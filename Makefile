# Oneshell means one can run multiple lines in a recipe in the same shell, so one doesn't have to
# chain commands together with semicolon
.ONESHELL:
SHELL=/bin/bash
ROOT_DIR=fastapi-template
PACKAGE=app
DOC_DIR=./docs
TEST_DIR=./tests
TEST_MARKER=placeholder
TEST_OUTPUT_DIR=tests_outputs
PRECOMMIT_FILE_PATHS=./app/__init__.py
PROFILE_FILE_PATH=./app/__init__.py
DOCKER_IMAGE=fastapi-template
DOCKER_TARGET=development


.PHONY: help install test publish pre-commit format lint profile
.DEFAULT_GOAL=help

help:
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) |\
		 awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m\
		 %s\n", $$1, $$2}'

# If .env file exists, include it and export its variables
ifeq ($(shell test -f .env && echo 1),1)
    include .env
    export
endif

install-uv: ## Install uv
	! command -v uv &> /dev/null && curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="$$HOME/.local/bin" sh

update-uv: ## Update uv to the latest version
	uv self update

install-base: ## Installs only package dependencies
	uv sync --frozen --no-dev --no-install-project

install: ## Installs the development version of the package
	$(MAKE) install-uv
	$(MAKE) update-uv
	uv sync --frozen
	$(MAKE) install-precommit

install-no-cache: ## Installs the development version of the package without cache
	$(MAKE) install-uv
	$(MAKE) update-uv
	uv sync --frozen --no-cache
	$(MAKE) install-precommit

install-test: ## Install only test version of the package
	uv sync --frozen --only-group test

install-precommit: ## Install pre-commit hooks
	uv run pre-commit install

python-version: ## Checks the python version used in the environment
	uv lock --locked
	uv run python --version

update-dependencies: ## Updates the lockfiles and installs dependencies. Dependencies are updated if necessary
	uv sync

upgrade-dependencies: ## Updates the lockfiles and installs the latest version of the dependencies
	uv sync -U

test-one: ## Run specific tests with TEST_MARKER=<test_name>, default marker is `placeholder`
	uv lock --locked
	uv run --module pytest -m ${TEST_MARKER}

test-one-parallel: ## Run specific tests with TEST_MARKER=<test_name> in parallel, default marker is `placeholder`
	uv lock --locked
	uv run --module pytest -n auto -m ${TEST_MARKER}

test-all: ## Run all tests
	uv lock --locked
	uv run --module pytest

test-all-parallel: ## Run all tests with parallelization
	uv lock --locked
	uv run --module pytest -n auto

test-coverage: ## Run all tests with coverage
	uv lock --locked
	uv run --module pytest --cov=${PACKAGE} --cov-report=html:coverage

test-coverage-parallel:
	uv lock --locked
	uv run --module pytest -n auto --cov=${PACKAGE} --cov-report=html:coverage

test: clean-test test-all ## Cleans and runs all tests
test-parallel: clean-test test-all-parallel ## Cleans and runs all tests with parallelization

clean-test: ## Clean test related files left after test
	# rm -rf ./htmlcov
	# rm -rf ./coverage.xml
	find . -type f -regex '\.\/\.*coverage[^rc].*' -delete
	rm -rf ${TEST_OUTPUT_DIR}
	find ${TEST_DIR} -type f -regex '\.\/\.*coverage[^rc].*' -delete
	find ${TEST_DIR} -type d -name 'htmlcov' -exec rm -r {} +
	find . -type d -name '.pytest_cache' -prune -exec rm -rf {} \;

pre-commit-one: ## Run pre-commit with specific files
	uv lock --locked
	uv run pre-commit run --files ${PRECOMMIT_FILE_PATHS}

pre-commit: ## Run pre-commit for all package files
	uv lock --locked
	uv run pre-commit run --all-files

pre-commit-clean: ## Clean pre-commit cache
	uv run pre-commit clean

lint: ## Lint code with ruff
	uv lock --locked
	uv run --module ruff format ${PACKAGE} --check --diff
	uv run --module ruff check ${PACKAGE}

lint-report: ## Lint report for gitlab
	uv lock --locked
	uv run --module ruff format ${PACKAGE} --check --diff
	uv run --module ruff check ${PACKAGE} --format gitlab > gl-code-quality-report.json

format: ## Run ruff for all package files. CHANGES CODE
	uv lock --locked
	uv run --module ruff format ${PACKAGE}
	uv run --module ruff check ${PACKAGE} --fix --show-fixes

format-unsafe: ## Run ruff for all package files. CHANGES CODE
	uv lock --locked
	uv run --module ruff format ${PACKAGE}
	uv run --module ruff check ${PACKAGE} --fix --unsafe-fixes --show-fixes

# profile: ## Profile the file with scalene and shows the report in the terminal
# 	uv lock --locked
# 	uv run --module scalene --cli --reduced-profile ${PROFILE_FILE_PATH}

# profile-gui: ## Profile the file with scalene and shows the report in the browser
# 	uv lock --locked
# 	uv run --module scalene ${PROFILE_FILE_PATH}

profile-builtin: ## Profile the file with cProfile and shows the report in the terminal
	uv lock --locked
	uv run --module cProfile -s tottime ${PROFILE_FILE_PATH}

docker-build: ## Build docker image
	docker build --tag ${DOCKER_IMAGE} --file docker/Dockerfile --target ${DOCKER_TARGET} .

run-dev: ## Run the app in the dev mode
	# uv run --module uvicorn app.main:app --port 8000
	uv run --module app.__main__

run-migration: ## Run migrations
	uv run --module alembic upgrade head

create-migrations: ## Create migrations
	uv run --module alembic revision --autogenerate -m "Migration" -o ${PACKAGE}/db/migrations

reset-all-migrations: ## Reset all migrations
	uv run --module alembic downgrade base

run-docker-services: # Run required docker services
	docker compose up -d fastapi-template-app api-workers-general api-workers-ml

##### EXTERNAL MAKEFILE CALLS #####

run-ui: ## Run the fasthtml UI server using the ui Makefile
	$(MAKE) -C ui run-ui

workers-python-version: ## Checks the python version used in the worker environment
	$(MAKE) -C api-workers-general python-version

run-workers-general: ## Run Hatchet general worker using the worker Makefile
	$(MAKE) -C api-workers-general run-worker

run-workers-ml: ## Run Hatchet ML worker using the ML worker Makefile
	$(MAKE) -C api-workers-ml run-worker

test-hatchet-api: ## Run Hatchet API/status mapping tests
	$(MAKE) -C api-shared test

test-workers-general: ## Run general worker Hatchet task-logic tests
	$(MAKE) -C api-workers-general test-task-logic

test-workers-ml: ## Run ML worker Hatchet task-logic tests
	$(MAKE) -C api-workers-ml test-task-logic

test-hatchet-all: ## Run all Hatchet-focused tests (api + workers)
	$(MAKE) test-hatchet-api
	$(MAKE) test-workers-general
	$(MAKE) test-workers-ml
