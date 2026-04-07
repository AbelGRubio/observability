# ─────────────────────────────────────────────────────────────────────────────
# Quality Assurance & Checks
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: ci
ci: check test   ## Run full QA pipeline
	@echo "✨ QA pipeline completed successfully"

.PHONY: check
check: qa test ## Run pre-commit checks
	@echo "$(ARROW) Running pre-commit hooks on all files..."
	@uv run pre-commit run --all-files || { echo "$(FAIL) Pre-commit failed"; exit 1; }
	@echo "$(OK) Pre-commit checks passed"

.PHONY: qa
qa:  pre-commit  ## Quality Assurance (pre-commit + other checks)
	@echo "$(ARROW) Running full Quality Assurance suite..."
	@echo "$(OK) QA checks completed"

# ─────────────────────────────────────────────────────────────────────────────
# Formatting & Fixing
# ─────────────────────────────────────────────────────────────────────────────
.PHONY: fix
fix: format lint ## Format and auto-fix code
	@echo "Code formatted and fixed $(OK)"

.PHONY: format
format:  ## Format code with ruff
	@echo "$(ARROW) Formatting code (ruff)..."
	@uv run ruff format

.PHONY: lint
lint:  ## Auto-fix lint issues with ruff
	@echo "$(ARROW) Auto-fixing lint issues (ruff)..."
	@uv run ruff check --fix

# ─────────────────────────────────────────────────────────────────────────────
# Testing
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: test
test: ## Run all tests
	@echo "$(ARROW) Running tests..."
	@uv run pytest -v --tb=short --disable-warnings --maxfail=1 || { echo "$(FAIL) Tests failed"; exit 1; }
	@echo "$(OK) All tests passed"
