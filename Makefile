.PHONY: help build run test clean docker-build docker-run k8s-deploy terraform-init terraform-apply sonar trivy

# Variables
APP_NAME = snapverse-ai
DOCKER_IMAGE = h8815/ai-reel-generator
DOCKER_REGISTRY = docker.io
K8S_NAMESPACE = snapverse

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install Python dependencies
	pip install -r requirements.txt

run: ## Run application locally
	python main.py

test: ## Run tests
	pytest tests/ -v

format: ## Format code with black
	black .

lint: ## Lint code
	black --check .

# Docker commands
docker-build: ## Build Docker image
	docker build -t $(DOCKER_IMAGE) .

docker-build-prod: ## Build production Docker image
	docker build -f Dockerfile.prod -t $(DOCKER_IMAGE) .

docker-run: ## Run Docker container
	docker run -p 5000:5000 -v $$(pwd)/static:/app/static $(DOCKER_IMAGE)

docker-push: ## Push Docker image to registry
	docker tag $(DOCKER_IMAGE):latest $(DOCKER_IMAGE):latest
	docker push $(DOCKER_IMAGE):latest

docker-compose-up: ## Start all services with docker-compose
	docker-compose up -d

docker-compose-down: ## Stop all services
	docker-compose down

docker-compose-logs: ## View docker-compose logs
	docker-compose logs -f

# Kubernetes commands
k8s-deploy: ## Deploy to Kubernetes
	kubectl apply -f k8s/

k8s-delete: ## Delete Kubernetes resources
	kubectl delete -f k8s/

k8s-status: ## Check Kubernetes deployment status
	kubectl get all -n $(K8S_NAMESPACE)

k8s-logs: ## View application logs
	kubectl logs -f deployment/$(APP_NAME) -n $(K8S_NAMESPACE)

k8s-scale: ## Scale deployment (usage: make k8s-scale REPLICAS=5)
	kubectl scale deployment/$(APP_NAME) --replicas=$(REPLICAS) -n $(K8S_NAMESPACE)

# Terraform commands
terraform-init: ## Initialize Terraform
	cd terraform && terraform init

terraform-plan: ## Plan Terraform changes
	cd terraform && terraform plan -var-file="terraform.tfvars"

terraform-apply: ## Apply Terraform configuration
	cd terraform && terraform apply -var-file="terraform.tfvars"

terraform-destroy: ## Destroy Terraform infrastructure
	cd terraform && terraform destroy -var-file="terraform.tfvars"

terraform-output: ## Show Terraform outputs
	cd terraform && terraform output

# Security scanning
trivy-fs: ## Run Trivy filesystem scan
	trivy fs --config trivy.yaml .

trivy-image: ## Run Trivy image scan
	trivy image $(DOCKER_IMAGE)

trivy-k8s: ## Run Trivy Kubernetes scan
	trivy config k8s/

# Code quality
sonar: ## Run SonarQube analysis
	sonar-scanner

sonar-start: ## Start SonarQube server
	docker-compose up -d sonarqube sonarqube-db

# Cleanup
clean: ## Clean up generated files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

clean-docker: ## Remove Docker containers and images
	docker-compose down -v
	docker rmi $(DOCKER_IMAGE) || true

# All-in-one commands
dev-setup: install docker-compose-up ## Setup development environment
	@echo "Development environment ready!"
	@echo "App: http://localhost:5000"
	@echo "SonarQube: http://localhost:9000"

ci-local: test trivy-fs sonar ## Run CI checks locally
	@echo "All CI checks passed!"

deploy-all: docker-build docker-push k8s-deploy ## Build, push, and deploy
	@echo "Deployment complete!"
