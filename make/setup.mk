ENV_FILE := .env

define prompt_and_store
    @if [ -z "$($(1))" ]; then \
        echo "$(ARROW) Enter $(1):"; \
        if [ "$(2)" = "secret" ]; then \
            read -s value; echo ""; \
        else \
            read value; \
        fi; \
        echo "$(1)=$$value" >> $(ENV_FILE); \
        export $(1)="$$value"; \
    fi
endef

.PHONY: setup
setup:  ## Execute project setup
	@echo "$(ARROW) Running interactive setup..."
	@touch $(ENV_FILE)
	$(call prompt_and_store,ARTIFACTORY_USER,plain)
	$(call prompt_and_store,ARTIFACTORY_TOKEN,secret)
	$(call prompt_and_store,BITBUCKET_USER,plain)
	$(call prompt_and_store,BITBUCKET_TOKEN,secret)
	@$(MAKE) configure-artifactory configure-bitbucket
	@echo "✅ Setup completed successfully"