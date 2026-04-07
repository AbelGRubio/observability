# ──────────────────────────────────────────────────────────────────────────────
#  Docker compose
# ──────────────────────────────────────────────────────────────────────────────

.PHONY: compose-down compose-logs compose-up

compose-up: ## Execute docker-compose up in docker folder
	@cd docker && REGISTRY_PATH=$(REGISTRY_PATH) VERSION=$(VERSION) \
		docker-compose up -d

compose-down: ## Execute docker-compose down in docker folder
	@cd docker && docker-compose down

compose-logs: ## Execute docker-compose logs in docker folder
	@cd docker && REGISTRY_PATH=$(REGISTRY_PATH) VERSION=$(VERSION) \
		docker-compose logs -f

.PHONY: compose-all
compose-all: compose-build compose-up compose-logs  ## Execute build, up and log.
