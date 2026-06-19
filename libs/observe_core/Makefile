# ─────────────────────────────────────────────────────────────────────────────
# Testing
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: test
test: ## Run all tests
	@echo "$(ARROW) Running tests..."
	@uv run pytest -v --tb=short --disable-warnings --maxfail=1 || { echo "$(FAIL) Tests failed"; exit 1; }
	@echo "$(OK) All tests passed"


# ─────────────────────────────────────────────────────────────────────────────
# Dependencies & Environment
# ─────────────────────────────────────────────────────────────────────────────
.PHONY: sync
sync: ## Sync dependencies based on lockfile
	@echo "$(ARROW) Syncing dependencies (uv sync)..."
	@uv sync
	@echo "Sync completed $(OK)"

# ─────────────────────────────────────────────────────────────────────────────
# Quality Assurance & Checks
# ─────────────────────────────────────────────────────────────────────────────

.PHONY: ci
ci: check test   ## Run full QA pipeline
	@echo "✨ QA pipeline completed successfully"

.PHONY: check
check: ## Run pre-commit checks
	@echo "$(ARROW) Running pre-commit checks..."
	@uv run pre-commit run --all-files
