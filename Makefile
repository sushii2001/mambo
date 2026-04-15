.DEFAULT_GOAL := help

local: ## build locally
	python3 -m src

build: ## build and start containers
	docker-compose up --build -d

test: ## run unittests
	pytest tests/ -v

clean: ## stop and remove containers
	docker-compose down --rmi local --volumes --remove-orphans

help: ## show available commands
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS=":.*?## "}; {printf "  %-10s %s\n", $$1, $$2}'