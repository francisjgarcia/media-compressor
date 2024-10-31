# Variables
REPO_NAME := $(shell basename `git rev-parse --show-toplevel`)
IMAGE_NAME := $(REPO_NAME):local
TRIVY_OUTPUT := trivy-results.sarif

# Rutas
DOCKERFILE_LOCAL := ../docker/Dockerfile.local
DOCKER_COMPOSE := ../docker/docker-compose.yml

# Comandos
.PHONY: all build trivy-scan clean

# El objetivo principal: compilar la imagen y escanearla
all: build trivy-scan

# Construye la imagen Docker usando el Dockerfile.local
build:
	@echo "Building Docker image: $(IMAGE_NAME)"
	docker build -f $(DOCKERFILE_LOCAL) -t $(IMAGE_NAME) ..

# Ejecuta Trivy para escanear la imagen y guardar los resultados
trivy-scan:
	@echo "Running Trivy scan on image: $(IMAGE_NAME)"
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
		-v $(shell pwd):/output aquasec/trivy image \
		--vuln-type os,library \
		--severity CRITICAL,HIGH \
		--ignore-unfixed=true \
		--format sarif \
		--output /output/$(TRIVY_OUTPUT) \
		$(IMAGE_NAME)
	@echo "Trivy scan complete. Results saved to $(TRIVY_OUTPUT)."

# Limpia los archivos generados por Trivy
clean:
	@echo "Cleaning up..."
	rm -f $(TRIVY_OUTPUT)
