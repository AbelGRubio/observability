# =============================================================================
#                     			Makefile
#                  Author: Abel
#                  Created: 2025-2026
#                  Purpose: Development workflow
# =============================================================================

# ──────────────────────────────────────────────────────────────────────────────
#  Configuration & Variables
# ──────────────────────────────────────────────────────────────────────────────
ifneq (,$(wildcard .env))
    include .env
    export UV_INDEX_USERNAME UV_INDEX_PASSWORD GH_TOKEN VERSION
endif

VENV_DIR        := .venv
ENV_SCRIPT      := activate_env.sh

PROJECT_NAME    := $(notdir $(CURDIR))
CONTAINER_NAME  := $(shell echo "$(PROJECT_NAME)" | tr '[:upper:]' '[:lower:]' | tr -s ' _-' '-' | sed 's/-*$$//; s/^-*//')
REPO_URL        := $(shell git remote get-url origin 2>/dev/null)
REGISTRY_URL    := $(shell echo "$(REPO_URL)" | \
                     sed -e 's|https://gitlab\.agrubio\.dev/|https://registry.agrubio.dev/|' \
                         -e 's|\.git$$||' | tr '[:upper:]' '[:lower:]')
REGISTRY_PATH   := $(shell echo "$(REGISTRY_URL)" | sed 's|https://||')

ifeq ($(strip $(VERSION)),)
VERSION     := $(shell grep '^version[[:space:]]*=' pyproject.toml | head -n 1 | sed 's/version[[:space:]]*=[[:space:]]*"\(.*\)"/\1/')
endif

# Colors
NO_COLOR    := \033[0m
ERROR       := \033[0;31m
SUCCESS     := \033[0;32m
WARNING     := \033[0;33m
INFO        := \033[0;36m
UNDERLINE   := \033[4m
BOLD        := \033[1m

OK      := $(SUCCESS)✓$(NO_COLOR)
FAIL    := $(ERROR)✗$(NO_COLOR)
ARROW   := $(INFO)→$(NO_COLOR)

# ──────────────────────────────────────────────────────────────────────────────
#  Main targets
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: all default help
.DEFAULT_GOAL := help

all: qa build  ## Run QA + build (most common workflow)

default: pre-commit  ## Default target (pre-commit only)

help:  ## Show this help message
	@echo "$(BOLD)DAS-DEVICE Development Makefile$(NO_COLOR)"
	@echo "Usage: make $(UNDERLINE)target$(NO_COLOR)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(INFO)%-22s$(NO_COLOR) %s\n", $$1, $$2}'

# ──────────────────────────────────────────────────────────────────────────────
#  Environment & Dependencies
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: check-venv venv update

check-venv:  ## Verify correct virtual environment is active
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "$(FAIL) No virtual environment is active."; \
		echo "   Run: $(INFO)source ./$(ENV_SCRIPT)$(NO_COLOR)"; \
		exit 1; \
	fi
	@if [ "$$VIRTUAL_ENV" != "$(PWD)/$(VENV_DIR)" ]; then \
		echo "$(FAIL) Wrong virtual environment active"; \
		echo "   Current : $$VIRTUAL_ENV"; \
		echo "   Expected: $(PWD)/$(VENV_DIR)"; \
		exit 1; \
	fi
	@uv lock --locked >/dev/null 2>&1 || { \
		echo "$(WARNING)uv lock file is out of date$(NO_COLOR)"; \
		echo "   Run: $(INFO)make update$(NO_COLOR)"; \
	}
	@echo "$(OK) Virtual environment is correct: $(INFO)$$VIRTUAL_ENV$(NO_COLOR)"

venv:  ## Activate virtual environment in current shell
	@echo "$(INFO)Activating virtual environment...$(NO_COLOR)"
	@bash -c "source $(ENV_SCRIPT) && exec bash"

# ──────────────────────────────────────────────────────────────────────────────
#  Quality & Tests
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: pre-commit qa test unused-packages

pre-commit:  ## Run all pre-commit hooks
	@echo "$(ARROW) Running pre-commit hooks on all files..."
	@uv run pre-commit run --all-files || { echo "$(FAIL) Pre-commit failed"; exit 1; }
	@echo "$(OK) Pre-commit checks passed"

qa:  pre-commit  ## Quality Assurance (pre-commit + other checks)
	@echo "$(ARROW) Running full Quality Assurance suite..."
	@echo "$(OK) QA checks completed"

test:  ## Run pytest suite
	@echo "$(ARROW) Running tests..."
	@uv run pytest -v --tb=short --disable-warnings --maxfail=1 || { echo "$(FAIL) Tests failed"; exit 1; }
	@echo "$(OK) All tests passed"

unused-packages:  ## Detect unused dependencies
	@echo "$(ARROW) Checking for unused packages..."
	@uv run deptry src

# ──────────────────────────────────────────────────────────────────────────────
#  Build & Packaging
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: build publish semantic-release

build:  ## Build python package(s)
	@echo "$(ARROW) Building package(s)..."
	@uv build || { echo "$(FAIL) Build failed"; exit 1; }
	@echo "$(OK) Build completed"

semantic-release: ## Calculate next version (dry-run)
	@echo "$(ARROW) Running semantic-release version..."
	@GH_TOKEN=$(GH_TOKEN) uv run semantic-release -vv version
	@echo "$(OK) Semantic release version check completed"

publish:  ## Publish release using semantic-release
	@echo "$(ARROW) Publishing release..."
	@uv run semantic-release publish || { echo "$(FAIL) Publish failed"; exit 1; }
	@echo "$(OK) Release published"

# ──────────────────────────────────────────────────────────────────────────────
#  Docker
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: docker-build docker-push docker-run docker-stop docker-ls docker-logs docker-all

docker-tags:  ## Build multi-platform Docker image (arm64 focused)
	@echo "$(ARROW) Building Docker image for arm64..."
	@echo "   Registry : $(INFO)$(REGISTRY_PATH)$(NO_COLOR)"
	@echo "   Version  : $(INFO)$(VERSION)$(NO_COLOR)"

docker-build: docker-tags ## Build multi-platform Docker image (arm64 focused)
	@docker buildx build -f docker/Dockerfile --platform linux/arm64 \
		--build-arg UV_INDEX_GITLAB_USERNAME=${UV_INDEX_GITLAB_USERNAME} \
		--build-arg UV_INDEX_GITLAB_PASSWORD=${UV_INDEX_GITLAB_PASSWORD} \
		-t $(REGISTRY_PATH):$(VERSION) -t $(REGISTRY_PATH):latest \
		--no-cache --load .
	@echo "$(OK) Docker image built"

docker-push:  ## Push Docker image to registry
	@echo "$(ARROW) Pushing images to registry..."
	@docker push $(REGISTRY_PATH):$(VERSION)
	@docker push $(REGISTRY_PATH):latest
	@echo "$(OK) Images pushed"

docker-run:  ## Run container locally (port 5000)
	@echo "$(ARROW) Starting container $(INFO)$(CONTAINER_NAME)$(NO_COLOR)..."
	@-docker stop $(CONTAINER_NAME) 2>/dev/null || true
	@-docker rm $(CONTAINER_NAME) 2>/dev/null || true
	@docker run -d --name $(CONTAINER_NAME) -p 5000:5000 $(REGISTRY_PATH):$(VERSION)
	@echo "$(OK) Container running → http://localhost:5000"

docker-stop:  ## Stop and remove container
	@echo "$(ARROW) Stopping container $(INFO)$(CONTAINER_NAME)$(NO_COLOR)..."
	@-docker stop $(CONTAINER_NAME) 2>/dev/null || true
	@-#docker rm $(CONTAINER_NAME) 2>/dev/null || true
	@echo "$(OK) Container stopped and removed"

docker-ls:  ## List /usr/local/bin inside container
	@docker run --rm --entrypoint ls $(REGISTRY_PATH):$(VERSION) -l /usr/local/bin

docker-logs:  ## Show container logs
	@echo "$(ARROW) Showing logs for $(INFO)$(CONTAINER_NAME)$(NO_COLOR)..."
	@docker logs -f $(CONTAINER_NAME)

docker-all: docker-build docker-run docker-logs

# ──────────────────────────────────────────────────────────────────────────────
#  Docker compose
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: compose-down compose-logs compose-up

compose-up:
	@cd docker && REGISTRY_PATH=$(REGISTRY_PATH) VERSION=$(VERSION) \
		docker-compose up -d $(filter-out $@,$(MAKECMDGOALS))

compose-down:
	@cd docker && docker-compose down $(filter-out $@,$(MAKECMDGOALS))

compose-logs:
	@cd docker && REGISTRY_PATH=$(REGISTRY_PATH) VERSION=$(VERSION) \
		docker-compose logs -f $(filter-out $@,$(MAKECMDGOALS))

# ──────────────────────────────────────────────────────────────────────────────
#  Documentation
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: rst
rst:  ## Generate RST API documentation
	@echo "$(ARROW) Generating RST API docs..."
	@uv run sphinx-apidoc -f -e -o docs/source/ src/
	@echo "$(OK) RST documentation generated"

.PHONY: docs
docs: rst  ## Build HTML documentation
	@echo "$(ARROW) Building HTML documentation..."
	@PYTHONPATH=src uv run sphinx-build -b html docs/source docs/build/html
	@echo "$(OK) Documentation built → docs/build/html/index.html"

# ──────────────────────────────────────────────────────────────────────────────
#  Cleanup
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: clean clean-dry-run

clean:  ## Remove temporary files, caches and build artifacts
	@echo "$(ARROW) Cleaning project..."
	@find . -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".ruff_cache" \
		-o -name "htmlcov" -o -name "build" -o -name "dist" -o -name "*.egg-info" \) -exec rm -rf {} + 2>/dev/null || true
	@find . -type f \( -name "*.pyc" -o -name ".coverage*" -o -name "coverage.xml" \) -delete 2>/dev/null || true
	@echo "$(OK) Cleanup completed"

clean-dry-run:  ## Show what would be deleted (dry run)
	@echo "$(WARNING)Files and directories that would be removed:$(NO_COLOR)"
	@find . -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".ruff_cache" \
		-o -name "htmlcov" -o -name "build" -o -name "dist" -o -name "*.egg-info" \) -print
	@find . -type f \( -name "*.pyc" -o -name ".coverage*" -o -name "coverage.xml" \) -print


# ──────────────────────────────────────────────────────────────────────────────
#  Profiling
# ──────────────────────────────────────────────────────────────────────────────

profile:
	@echo off & set RABBITMQ_USER=guest & set RABBITMQ_PSSWRD=guest & set DISABLE_SYSLOG=true & \
	uv run python -m cProfile -o profiler_worker.profile src/__main__.py "./data/CHA1" "./result/CHA1" & \
	uv run snakeviz profiler_worker.profile

profile-memory:
	@echo off & set RABBITMQ_USER=guest & set RABBITMQ_PSSWRD=guest & set DISABLE_SYSLOG=true & \
	uv run mprof run --multiprocess src/__main__.py "./data/CHA1" "./result/CHA1"; \
	uv run mprof plot --title "Profiler Real Time DAS"


# ────────────────────────────────────────────────────────────────────────────
# RUN UVICORN
# ────────────────────────────────────────────────────────────────────────────
.PHONY: uvicorn
uvicorn: ## Run uvicorn
	@echo "$(ARROW) Launching uvicorn..."
	@PYTHONPATH=src uv run uvicorn src.__main__:app --host 0.0.0.0 --port 8000
	@echo "Ended uvicorn"


# ────────────────────────────────────────────────────────────────────────────
# UV SYNC
# ────────────────────────────────────────────────────────────────────────────
.PHONY: uv-sync
uv-sync: ## Run uv sync
	@echo "$(ARROW) Running uv sync..."
	@uv sync
	@echo "Ended UV "
