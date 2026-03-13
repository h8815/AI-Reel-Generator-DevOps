# ✅ DevOps Setup Checklist

Use this checklist to ensure proper setup of the DevOps infrastructure.

---

## 📋 Pre-Deployment Checklist

### 1. Prerequisites Installation
- [ ] Docker installed and running
- [ ] kubectl installed
- [ ] Terraform installed (v1.6+)
- [ ] AWS CLI installed and configured
- [ ] Python 3.12+ installed
- [ ] Git installed
- [ ] Make installed (optional but recommended)

### 2. Repository Setup
- [ ] Repository cloned locally
- [ ] All DevOps files present (check DEVOPS_FILES_SUMMARY.md)
- [ ] `.gitignore` updated to exclude sensitive files
- [ ] README.md reviewed

---

## 🔐 Security Configuration

### 3. GitHub Secrets Configuration
Navigate to: Repository Settings → Secrets and variables → Actions

- [ ] `AWS_ACCESS_KEY_ID` - AWS access key
- [ ] `AWS_SECRET_ACCESS_KEY` - AWS secret key
- [ ] `SONAR_TOKEN` - SonarQube authentication token
- [ ] `SONAR_HOST_URL` - SonarQube server URL
- [ ] `KUBE_CONFIG` - Kubernetes config (base64 encoded)
- [ ] `DB_PASSWORD` - Database password (if using RDS)

**Generate base64 kubeconfig**:
```bash
cat ~/.kube/config | base64 -w 0
```

### 4. AWS Configuration
- [ ] AWS account created
- [ ] IAM user created with appropriate permissions
- [ ] AWS CLI configured: `aws configure`
- [ ] S3 bucket created for Terraform state
- [ ] DynamoDB table created for state locking

**Required IAM Permissions**:
- EC2, VPC, EKS, ECR, S3, RDS, CloudWatch, IAM

---

## 🏗️ Infrastructure Setup

### 5. Terraform Configuration
- [ ] Copy `terraform/terraform.tfvars.example` to `terraform/terraform.tfvars`
- [ ] Update variables in `terraform.tfvars`:
  - [ ] `aws_region`
  - [ ] `environment`
  - [ ] `project_name`
  - [ ] `vpc_cidr`
  - [ ] `availability_zones`
  - [ ] `db_username` (if using RDS)
- [ ] Review `terraform/main.tf` for customizations
- [ ] Initialize Terraform: `make terraform-init`
- [ ] Plan infrastructure: `make terraform-plan`
- [ ] Review plan output carefully
- [ ] Apply infrastructure: `make terraform-apply`
- [ ] Save Terraform outputs: `terraform output > outputs.txt`

### 6. Kubernetes Cluster Setup
- [ ] EKS cluster created (via Terraform or manually)
- [ ] kubectl configured: `aws eks update-kubeconfig --name <cluster-name>`
- [ ] Verify connection: `kubectl cluster-info`
- [ ] Install NGINX Ingress Controller:
  ```bash
  kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/aws/deploy.yaml
  ```
- [ ] Install cert-manager for SSL:
  ```bash
  kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
  ```

### 7. Kubernetes Resources
- [ ] Update `k8s/deployment.yaml` with correct image URL
- [ ] Update `k8s/ingress.yaml` with your domain
- [ ] Review resource limits in `k8s/deployment.yaml`
- [ ] Apply namespace: `kubectl apply -f k8s/namespace.yaml`
- [ ] Apply configmap: `kubectl apply -f k8s/configmap.yaml`
- [ ] Apply deployment: `kubectl apply -f k8s/deployment.yaml`
- [ ] Apply service: `kubectl apply -f k8s/service.yaml`
- [ ] Apply ingress: `kubectl apply -f k8s/ingress.yaml`
- [ ] Apply HPA: `kubectl apply -f k8s/hpa.yaml`
- [ ] Verify deployment: `kubectl get all -n snapverse`

---

## 🐳 Docker Configuration

### 8. Container Registry
- [ ] GitHub Container Registry (GHCR) enabled
- [ ] Docker logged in to GHCR:
  ```bash
  echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
  ```
- [ ] Update image URLs in workflows and K8s manifests
- [ ] Test local Docker build: `make docker-build`
- [ ] Test local Docker run: `make docker-run`

### 9. Docker Compose (Local Development)
- [ ] Review `docker-compose.yml`
- [ ] Start services: `make docker-compose-up`
- [ ] Verify app: http://localhost:5000
- [ ] Verify SonarQube: http://localhost:9000
- [ ] Configure SonarQube (first time):
  - [ ] Login with admin/admin
  - [ ] Change password
  - [ ] Generate token
  - [ ] Add token to GitHub Secrets

---

## 🔍 Security & Quality Tools

### 10. SonarQube Setup
- [ ] SonarQube server running (via docker-compose)
- [ ] SonarQube project created
- [ ] Quality gate configured
- [ ] Token generated and added to GitHub Secrets
- [ ] Test local scan: `make sonar`

### 11. Trivy Setup
- [ ] Trivy installed locally (optional):
  ```bash
  # macOS
  brew install aquasecurity/trivy/trivy
  
  # Linux
  wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
  echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
  sudo apt-get update
  sudo apt-get install trivy
  ```
- [ ] Review `trivy.yaml` configuration
- [ ] Test filesystem scan: `make trivy-fs`
- [ ] Test image scan: `make trivy-image`

---

## 🔄 CI/CD Pipeline

### 12. GitHub Actions
- [ ] Review `.github/workflows/ci-cd.yml`
- [ ] Review `.github/workflows/terraform.yml`
- [ ] Review `.github/workflows/security.yml`
- [ ] All required secrets configured
- [ ] Test workflow by pushing to develop branch
- [ ] Verify all jobs pass
- [ ] Check GitHub Security tab for scan results

### 13. Workflow Customization
- [ ] Update Docker registry URLs
- [ ] Update Kubernetes cluster name
- [ ] Adjust resource limits if needed
- [ ] Configure notification settings
- [ ] Set up branch protection rules

---

## 📊 Monitoring & Logging

### 14. CloudWatch Setup
- [ ] CloudWatch log group created
- [ ] Log retention configured
- [ ] Alarms configured for:
  - [ ] High CPU usage
  - [ ] High memory usage
  - [ ] Error rate
  - [ ] Response time
- [ ] Dashboard created

### 15. Kubernetes Monitoring
- [ ] Metrics server installed:
  ```bash
  kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
  ```
- [ ] Test metrics: `kubectl top nodes`
- [ ] Test pod metrics: `kubectl top pods -n snapverse`

---

## 🌐 Domain & SSL

### 16. Domain Configuration
- [ ] Domain registered
- [ ] DNS configured to point to Load Balancer
- [ ] Update `k8s/ingress.yaml` with domain
- [ ] cert-manager ClusterIssuer created:
  ```yaml
  apiVersion: cert-manager.io/v1
  kind: ClusterIssuer
  metadata:
    name: letsencrypt-prod
  spec:
    acme:
      server: https://acme-v02.api.letsencrypt.org/directory
      email: your-email@example.com
      privateKeySecretRef:
        name: letsencrypt-prod
      solvers:
      - http01:
          ingress:
            class: nginx
  ```
- [ ] SSL certificate issued
- [ ] HTTPS working

---

## 🧪 Testing

### 17. Application Testing
- [ ] Unit tests pass: `make test`
- [ ] Code formatting check: `make format`
- [ ] Local app runs: `make run`
- [ ] Docker container runs: `make docker-run`
- [ ] All endpoints accessible

### 18. Integration Testing
- [ ] Test file upload
- [ ] Test reel creation
- [ ] Test gallery view
- [ ] Test file deletion
- [ ] Test with different file sizes
- [ ] Test with different aspect ratios

### 19. Load Testing
- [ ] Install load testing tool (e.g., Apache Bench, k6)
- [ ] Run load tests
- [ ] Verify auto-scaling works
- [ ] Check resource usage under load
- [ ] Verify no errors under load

---

## 📝 Documentation

### 20. Documentation Review
- [ ] README.md updated with correct URLs
- [ ] DEVOPS.md reviewed
- [ ] DEVOPS_QUICKSTART.md reviewed
- [ ] DEVOPS_FILES_SUMMARY.md reviewed
- [ ] Team trained on deployment process
- [ ] Runbooks created for common issues

---

## 🚀 Deployment

### 21. Initial Deployment
- [ ] All previous steps completed
- [ ] Code pushed to main branch
- [ ] CI/CD pipeline runs successfully
- [ ] Application deployed to Kubernetes
- [ ] Health checks passing
- [ ] Application accessible via domain
- [ ] SSL certificate valid

### 22. Post-Deployment Verification
- [ ] All pods running: `kubectl get pods -n snapverse`
- [ ] Services accessible: `kubectl get svc -n snapverse`
- [ ] Ingress configured: `kubectl get ingress -n snapverse`
- [ ] Logs clean: `kubectl logs -f deployment/snapverse-ai -n snapverse`
- [ ] No security vulnerabilities (check GitHub Security tab)
- [ ] SonarQube quality gate passed

---

## 🔧 Maintenance

### 23. Regular Maintenance Tasks
- [ ] Weekly security scans scheduled
- [ ] Dependency updates scheduled
- [ ] Backup strategy implemented
- [ ] Disaster recovery plan documented
- [ ] Incident response plan created
- [ ] On-call rotation established

### 24. Cost Optimization
- [ ] Review AWS costs
- [ ] Right-size instances if needed
- [ ] Configure auto-scaling policies
- [ ] Set up cost alerts
- [ ] Review unused resources

---

## 📞 Support & Escalation

### 25. Support Setup
- [ ] Support channels established (Slack, email, etc.)
- [ ] Escalation path defined
- [ ] Contact list created
- [ ] Documentation accessible to team
- [ ] Training sessions scheduled

---

## ✅ Final Verification

### 26. Production Readiness
- [ ] All checklist items completed
- [ ] Security audit passed
- [ ] Performance testing completed
- [ ] Backup and restore tested
- [ ] Monitoring and alerting working
- [ ] Documentation complete
- [ ] Team trained
- [ ] Go-live approval obtained

---

## 🎉 Go Live!

Once all items are checked:
1. Schedule go-live date
2. Notify stakeholders
3. Monitor closely for first 24-48 hours
4. Collect feedback
5. Iterate and improve

---

## 📋 Quick Commands Reference

```bash
# Setup
make dev-setup              # Complete local setup
./setup-devops.sh          # Interactive setup

# Development
make run                   # Run locally
make test                  # Run tests
make format                # Format code

# Docker
make docker-build          # Build image
make docker-run            # Run container
make docker-compose-up     # Start all services

# Kubernetes
make k8s-deploy           # Deploy to K8s
make k8s-status           # Check status
make k8s-logs             # View logs

# Terraform
make terraform-init       # Initialize
make terraform-plan       # Plan changes
make terraform-apply      # Apply changes

# Security
make trivy-fs             # Scan filesystem
make trivy-image          # Scan image
make sonar                # Run SonarQube

# Cleanup
make clean                # Clean local files
make clean-docker         # Remove containers
```

---

**Last Updated**: 2024
**Version**: 1.0

**Notes**: 
- Check items as you complete them
- Document any deviations or issues
- Update this checklist based on your experience
- Share feedback with the team
