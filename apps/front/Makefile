.PHONY: front  install

## Run the Next.js frontend (http://localhost:3000)
front:
	pnpm run dev-frontend


## Install all dependencies (frontend + agent)
install:
	pnpm install


.PHONY: docker-build
docker-build: ## Build Docker image
	@docker build --platform linux/amd64 -f Dockerfile \
		-t observe_front:v0.1.0 --no-cache --load . \
		&& echo "$(ARROW) Building image... done"
	@$(MAKE) uv-local
