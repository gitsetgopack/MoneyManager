# Help function to display available commands
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies in the virtual environment
	pip install --upgrade pip
	pip install -r requirements.txt
	pre-commit install

run: ## Run the FastAPI app using the virtual environment
	python api/app.py

start_database: ## make and run the database
	docker run --name mongo-MM -p 27017:27017 -d mongo:latest
	@sleep 5  # Wait for MongoDB to be ready

stop_database: ## stop the database
	docker stop mongo-MM

clear_database: ## clear the database
	docker stop mongo-MM
	docker rm mongo-MM

test: ## Start MongoDB Docker container, run tests, and clean up
	docker run --name mongo-test -p 27017:27017 -d mongo:latest
	@sleep 5  # Wait for MongoDB to be ready
	pytest --cov=api --cov-report=json:tmp/coverage.json --junitxml=tmp/pytest_output.xml -v || (docker stop mongo-test && docker rm mongo-test && exit 1)
	docker stop mongo-test
	docker rm mongo-test

fix: ## Black format and isort on api dir
	black api/
	isort api/

clean: ## Clean up Python bytecode files and caches
	@docker stop mongo-test || true
	@docker rm mongo-test || true
	(find . -type f \( -name "*.pyc" -o -name ".coverage" -o -name ".python-version" \) -delete && \
	find . -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".mypy_cache" \) -exec rm -rf {} +)

no_verify_push: ## Stage, commit & push with --no-verify
	@read -p "Enter commit message: " msg; \
	git commit -a -m "$$msg" --no-verify
	git push

.PHONY: all help install run test fix clean no_verify_push
