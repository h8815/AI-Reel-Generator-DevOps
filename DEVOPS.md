# DevOps Documentation

## 📋 Overview

This document provides comprehensive instructions for setting up and using the DevOps infrastructure for SnapVerse AI.

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- kubectl
- Terraform >= 1.0
- AWS CLI (configured)
- GitHub account with Actions enabled

---

## 🐳 Docker

### Local Development
```bash
# Build image
docker build -t snapverse-ai .

# Run container
docker run -p 5000:5000 -v $(pwd)/static:/app/static snapverse-ai
```

### Production Build
```bash
# Build production image
docker build -f Dockerfile.prod -t snapverse-ai:prod .

# Run with Gunicorn
docker run -p 5000:5000 snapverse-ai:prod
```

### Docker Compose (with SonarQube & Trivy)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f snapverse-ai

# Stop services
docker-compose down
```

**Services:**
- App: http://localhost:5000
- SonarQube: http://localhost:9000 (admin/admin)
- Trivy Server: http://localhost:8080

---

## ☸️ Kubernetes

### Setup kubectl
```bash
# Configure kubectl for your cluster
aws eks update-kubeconfig --name snapverse-ai-cluster --region us-east-1
```

### Deploy Application
```bash
# Apply all manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n snapverse
kubectl get services -n snapverse

# View logs
kubectl logs -f deployment/snapverse-ai -n snapverse
```

### Scale Application
```bash
# Manual scaling
kubectl scale deployment snapverse-ai --replicas=5 -n snapverse

# Auto-scaling is configured via HPA (3-10 replicas)
kubectl get hpa -n snapverse
```

### Update Application
```bash
# Update image
kubectl set image deployment/snapverse-ai snapverse-ai=ghcr.io/yourusername/snapverse-ai:v2.0 -n snapverse

# Rollback if needed
kubectl rollout undo deployment/snapverse-ai -n snapverse
```

---

## 🏗️ Terraform

### Initialize Terraform
```bash
cd terraform

# Initialize
terraform init

# Validate configuration
terraform validate

# Plan changes
terraform plan -var-file="terraform.tfvars"
```

### Deploy Infrastructure
```bash
# Apply configuration
terraform apply -var-file="terraform.tfvars"

# View outputs
terraform output
```

### Destroy Infrastructure
```bash
# Destroy all resources (use with caution!)
terraform destroy -var-file="terraform.tfvars"
```

### Infrastructure Components
- **VPC**: Isolated network with public/private subnets
- **EKS**: Managed Kubernetes cluster (1.28)
- **ECR**: Container registry
- **S3**: Static file storage
- **RDS**: PostgreSQL database (optional)
- **ALB**: Application Load Balancer
- **CloudWatch**: Logging and monitoring

---

## 🔍 SonarQube

### Local Setup
```bash
# Start SonarQube via Docker Compose
docker-compose up -d sonarqube sonarqube-db

# Access: http://localhost:9000
# Default credentials: admin/admin
```

### Run Analysis
```bash
# Install SonarScanner
pip install sonar-scanner

# Run scan
sonar-scanner \
  -Dsonar.projectKey=snapverse-ai \
  -Dsonar.sources=. \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=YOUR_TOKEN
```

### CI/CD Integration
SonarQube analysis runs automatically in GitHub Actions on every push/PR.

**Quality Gates:**
- Code Coverage > 80%
- No Critical/Blocker issues
- Security hotspots reviewed
- Code duplication < 3%

---

## 🛡️ Trivy Security Scanning

### Filesystem Scan
```bash
# Scan project files
trivy fs --config trivy.yaml .

# Scan with specific severity
trivy fs --severity CRITICAL,HIGH .
```

### Docker Image Scan
```bash
# Scan Docker image
trivy image snapverse-ai:latest

# Scan with JSON output
trivy image --format json --output results.json snapverse-ai:latest
```

### Kubernetes Manifest Scan
```bash
# Scan K8s configurations
trivy config k8s/

# Scan specific file
trivy config k8s/deployment.yaml
```

### CI/CD Integration
Trivy scans run automatically in GitHub Actions:
- Filesystem scan on every push
- Image scan after Docker build
- Results uploaded to GitHub Security tab

---

## 🔄 GitHub Actions CI/CD

### Workflow Overview
The CI/CD pipeline (`ci-cd.yml`) includes:

1. **Test** - Run pytest, code formatting checks
2. **Security Scan** - Trivy filesystem & config scan
3. **SonarQube** - Code quality analysis
4. **Build & Push** - Docker image to GHCR
5. **Deploy** - Deploy to Kubernetes cluster

### Required Secrets
Configure in GitHub Settings → Secrets:

```
SONAR_TOKEN          # SonarQube authentication token
SONAR_HOST_URL       # SonarQube server URL
KUBE_CONFIG          # Kubernetes config file (base64 encoded)
```

### Trigger Workflow
```bash
# Push to main branch
git push origin main

# Create pull request
gh pr create --base main --head feature-branch
```

### View Workflow Status
- GitHub Actions tab in repository
- Status badges in README
- Email notifications on failure

---

## 📊 Monitoring & Logging

### Kubernetes Logs
```bash
# Application logs
kubectl logs -f deployment/snapverse-ai -n snapverse

# All pods in namespace
kubectl logs -f -l app=snapverse-ai -n snapverse

# Previous container logs
kubectl logs --previous deployment/snapverse-ai -n snapverse
```

### CloudWatch Logs
```bash
# View logs via AWS CLI
aws logs tail /aws/eks/snapverse-ai/cluster --follow
```

### Metrics
```bash
# Pod metrics
kubectl top pods -n snapverse

# Node metrics
kubectl top nodes
```

---

## 🔐 Security Best Practices

### Docker
- ✅ Multi-stage builds
- ✅ Non-root user
- ✅ Minimal base image (slim)
- ✅ No secrets in image
- ✅ Regular vulnerability scanning

### Kubernetes
- ✅ Network policies
- ✅ Resource limits
- ✅ RBAC enabled
- ✅ Secrets management
- ✅ Pod security policies

### Terraform
- ✅ Remote state (S3)
- ✅ State locking (DynamoDB)
- ✅ Encryption at rest
- ✅ IAM least privilege
- ✅ VPC isolation

---

## 🐛 Troubleshooting

### Docker Issues
```bash
# Check container logs
docker logs snapverse-ai

# Inspect container
docker inspect snapverse-ai

# Execute shell in container
docker exec -it snapverse-ai /bin/bash
```

### Kubernetes Issues
```bash
# Describe pod for events
kubectl describe pod <pod-name> -n snapverse

# Check resource usage
kubectl top pods -n snapverse

# Restart deployment
kubectl rollout restart deployment/snapverse-ai -n snapverse
```

### Terraform Issues
```bash
# Enable debug logging
export TF_LOG=DEBUG
terraform apply

# Refresh state
terraform refresh

# Import existing resource
terraform import aws_instance.example i-1234567890abcdef0
```

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [SonarQube Documentation](https://docs.sonarqube.org/)
- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

## 🤝 Support

For issues or questions:
1. Check existing GitHub Issues
2. Review documentation
3. Create new issue with details
4. Contact DevOps team

---

**Last Updated:** 2024
**Maintained By:** DevOps Team
