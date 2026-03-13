# 🚀 DevOps Quick Start Guide

## 📋 Prerequisites

Install the following tools:

- **Docker** (20.10+): https://docs.docker.com/get-docker/
- **kubectl** (1.28+): https://kubernetes.io/docs/tasks/tools/
- **Terraform** (1.6+): https://www.terraform.io/downloads
- **AWS CLI** (2.0+): https://aws.amazon.com/cli/
- **Make** (optional): For using Makefile commands

---

## 🏃 Quick Start

### 1. Local Development with Docker Compose

```bash
# Start all services (app, SonarQube, Trivy)
make docker-compose-up

# Or without Make
docker-compose up -d

# Access services
# App: http://localhost:5000
# SonarQube: http://localhost:9000 (admin/admin)
# Trivy: http://localhost:8080
```

### 2. Run Security Scans

```bash
# Trivy filesystem scan
make trivy-fs

# Trivy Docker image scan
make trivy-image

# SonarQube analysis
make sonar
```

### 3. Deploy to Kubernetes

```bash
# Configure kubectl (AWS EKS example)
aws eks update-kubeconfig --name snapverse-ai-cluster --region us-east-1

# Deploy application
make k8s-deploy

# Check status
make k8s-status
```

### 4. Provision Infrastructure with Terraform

```bash
# Initialize Terraform
make terraform-init

# Plan changes
make terraform-plan

# Apply infrastructure
make terraform-apply
```

---

## 📁 File Structure

```
.
├── .github/workflows/       # GitHub Actions CI/CD
│   ├── ci-cd.yml           # Main CI/CD pipeline
│   ├── terraform.yml       # Infrastructure deployment
│   └── security.yml        # Security scanning
├── k8s/                    # Kubernetes manifests
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   └── hpa.yaml
├── terraform/              # Infrastructure as Code
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars.example
├── docker-compose.yml      # Local development stack
├── Dockerfile              # Development Docker image
├── Dockerfile.prod         # Production Docker image
├── Makefile               # Common commands
├── sonar-project.properties # SonarQube config
├── trivy.yaml             # Trivy config
└── DEVOPS.md              # Detailed documentation
```

---

## 🔧 Configuration

### GitHub Secrets

Add these secrets in GitHub Settings → Secrets and variables → Actions:

```
AWS_ACCESS_KEY_ID          # AWS credentials
AWS_SECRET_ACCESS_KEY      # AWS credentials
SONAR_TOKEN               # SonarQube token
SONAR_HOST_URL            # SonarQube server URL
KUBE_CONFIG               # Kubernetes config (base64)
DB_PASSWORD               # Database password
```

### Terraform Variables

Copy and customize:

```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# Edit terraform/terraform.tfvars with your values
```

---

## 🎯 Common Tasks

### Build & Run Locally

```bash
# Build Docker image
make docker-build

# Run container
make docker-run
```

### Test Application

```bash
# Run tests
make test

# Format code
make format
```

### Deploy Updates

```bash
# Build, push, and deploy
make deploy-all
```

### Scale Application

```bash
# Scale to 5 replicas
make k8s-scale REPLICAS=5
```

### View Logs

```bash
# Kubernetes logs
make k8s-logs

# Docker Compose logs
make docker-compose-logs
```

---

## 🛡️ Security Features

- ✅ **Trivy**: Vulnerability scanning (filesystem, images, configs)
- ✅ **SonarQube**: Code quality & security analysis
- ✅ **CodeQL**: Advanced security scanning
- ✅ **Secret Scanning**: Detect exposed credentials
- ✅ **Dependency Check**: Python package vulnerabilities

---

## 📊 CI/CD Pipeline

### Workflow Stages

1. **Test** → Run pytest, format checks
2. **Security** → Trivy, SonarQube scans
3. **Build** → Docker image creation
4. **Push** → Push to container registry
5. **Deploy** → Deploy to Kubernetes

### Triggers

- Push to `main` or `develop` branches
- Pull requests to `main`
- Manual workflow dispatch

---

## 🏗️ Infrastructure Components

### AWS Resources (Terraform)

- **VPC**: Isolated network with public/private subnets
- **EKS**: Managed Kubernetes cluster
- **ECR**: Container registry
- **S3**: Static file storage
- **RDS**: PostgreSQL database (optional)
- **ALB**: Application Load Balancer
- **CloudWatch**: Logging & monitoring

### Kubernetes Resources

- **Namespace**: Isolated environment
- **Deployment**: Application pods (3-10 replicas)
- **Service**: Load balancing
- **Ingress**: External access with SSL
- **HPA**: Auto-scaling based on CPU/memory
- **PVC**: Persistent storage

---

## 🐛 Troubleshooting

### Docker Issues

```bash
# View logs
docker logs snapverse-ai

# Restart container
docker restart snapverse-ai

# Clean up
make clean-docker
```

### Kubernetes Issues

```bash
# Check pod status
kubectl get pods -n snapverse

# Describe pod
kubectl describe pod <pod-name> -n snapverse

# Restart deployment
kubectl rollout restart deployment/snapverse-ai -n snapverse
```

### Terraform Issues

```bash
# Refresh state
terraform refresh

# Show current state
terraform show

# Enable debug logging
export TF_LOG=DEBUG
```

---

## 📚 Documentation

- **[DEVOPS.md](DEVOPS.md)**: Comprehensive DevOps guide
- **[README.md](README.md)**: Application documentation
- **[Makefile](Makefile)**: Available commands

---

## 🤝 Support

For issues:
1. Check [DEVOPS.md](DEVOPS.md) for detailed instructions
2. Review GitHub Actions logs
3. Create an issue with details

---

**Happy Deploying! 🚀**
