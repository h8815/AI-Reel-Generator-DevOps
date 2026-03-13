# 🔧 Configuration Guide - Variables & Secrets

This document lists ALL variables, secrets, and configurations you need to modify before deployment.

---

## 🚨 CRITICAL - Must Change Before Deployment

### 1. GitHub Secrets (Repository Settings → Secrets and variables → Actions)

**Required for CI/CD Pipeline:**

```
AWS_ACCESS_KEY_ID          # Your AWS access key
AWS_SECRET_ACCESS_KEY      # Your AWS secret key
SONAR_TOKEN               # SonarQube authentication token
SONAR_HOST_URL            # Your SonarQube server URL (e.g., http://your-server:9000)
KUBE_CONFIG               # Base64 encoded Kubernetes config file
DB_PASSWORD               # Database password (if using RDS)
DOCKERHUB_USERNAME        # Your Docker Hub username (h8815)
DOCKERHUB_TOKEN           # Docker Hub access token
```

**How to get base64 kubeconfig:**
```bash
cat ~/.kube/config | base64 -w 0
```

---

### 2. Kubernetes Manifests

#### File: `k8s/deployment.yaml`
**Line 18:** Update Docker image if needed
```yaml
image: h8815/ai-reel-generator:latest  # ✅ Already correct
```

#### File: `k8s/ingress.yaml`
**Line 14 & 15:** Replace with YOUR domain
```yaml
tls:
  - hosts:
    - snapverse.yourdomain.com  # ❌ CHANGE THIS
    secretName: snapverse-tls
rules:
  - host: snapverse.yourdomain.com  # ❌ CHANGE THIS
```

**Example:**
```yaml
tls:
  - hosts:
    - snapverse.example.com  # ✅ Your actual domain
    secretName: snapverse-tls
rules:
  - host: snapverse.example.com  # ✅ Your actual domain
```

---

### 3. Terraform Variables

#### File: `terraform/terraform.tfvars` (Create from example)

**Step 1:** Copy the example file
```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
```

**Step 2:** Edit `terraform/terraform.tfvars` with your values:

```hcl
# AWS Configuration
aws_region   = "us-east-1"  # ❌ Change to your preferred region
environment  = "dev"        # ✅ OK or change to "prod"
project_name = "snapverse-ai"  # ✅ OK

# Network Configuration
vpc_cidr             = "10.0.0.0/16"  # ✅ OK or customize
availability_zones   = ["us-east-1a", "us-east-1b"]  # ❌ Match your region
private_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]  # ✅ OK
public_subnet_cidrs  = ["10.0.101.0/24", "10.0.102.0/24"]  # ✅ OK

# Database Configuration (Optional)
enable_rds         = false  # ✅ Set to true if you need database
db_instance_class  = "db.t3.micro"  # ✅ OK
db_username        = "snapverse_admin"  # ❌ Change for security
# db_password - Set via environment variable: export TF_VAR_db_password="YourSecurePassword"
```

**Step 3:** Set database password as environment variable (if using RDS):
```bash
export TF_VAR_db_password="YourVerySecurePassword123!"
```

#### File: `terraform/main.tf`
**Line 14-16:** Update S3 backend configuration
```hcl
backend "s3" {
  bucket         = "snapverse-terraform-state"  # ❌ CHANGE - Must be globally unique
  key            = "snapverse/terraform.tfstate"  # ✅ OK
  region         = "us-east-1"  # ❌ Match your aws_region
  encrypt        = true  # ✅ OK
  dynamodb_table = "snapverse-terraform-locks"  # ❌ CHANGE if needed
}
```

**Example:**
```hcl
backend "s3" {
  bucket         = "h8815-snapverse-terraform-state"  # ✅ Unique name
  key            = "snapverse/terraform.tfstate"
  region         = "us-east-1"  # ✅ Your region
  encrypt        = true
  dynamodb_table = "h8815-snapverse-terraform-locks"  # ✅ Unique name
}
```

**⚠️ IMPORTANT:** Create S3 bucket and DynamoDB table BEFORE running terraform:
```bash
# Create S3 bucket
aws s3 mb s3://h8815-snapverse-terraform-state --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket h8815-snapverse-terraform-state \
  --versioning-configuration Status=Enabled

# Create DynamoDB table
aws dynamodb create-table \
  --table-name h8815-snapverse-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region us-east-1
```

---

### 4. SonarQube Configuration

#### File: `sonar-project.properties`
**Line 2-4:** Update project details
```properties
sonar.projectKey=snapverse-ai  # ❌ Change to match your SonarQube project
sonar.projectName=SnapVerse AI - Reel Generator  # ✅ OK or customize
sonar.projectVersion=1.0  # ✅ OK
```

**After starting SonarQube:**
1. Access: http://localhost:9000
2. Login: admin/admin
3. Change password
4. Create new project with key: `snapverse-ai`
5. Generate token
6. Add token to GitHub Secrets as `SONAR_TOKEN`
7. Add `http://localhost:9000` or your server URL as `SONAR_HOST_URL`

---

### 5. Docker Compose

#### File: `docker-compose.yml`
**Already configured correctly** ✅

If you want to change ports:
```yaml
services:
  snapverse-ai:
    ports:
      - "5000:5000"  # Change left side: "8080:5000" for port 8080
  
  sonarqube:
    ports:
      - "9000:9000"  # Change if port 9000 is in use
```

---

### 6. GitHub Actions Workflows

#### File: `.github/workflows/ci-cd.yml`
**Line 2-6:** Already configured for your repo ✅
```yaml
on:
  push:
    branches: [ main, develop ]  # ✅ OK - triggers on these branches
  pull_request:
    branches: [ main, develop ]  # ✅ OK
```

**Line 8-10:** Docker configuration
```yaml
env:
  DOCKER_IMAGE: h8815/ai-reel-generator  # ✅ Already correct
  DOCKER_REGISTRY: docker.io  # ✅ Already correct
  PYTHON_VERSION: '3.12'  # ✅ OK
```

**Line 103-107:** Update if using different registry
```yaml
- name: Log in to Container Registry
  uses: docker/login-action@v3
  with:
    registry: docker.io  # ✅ OK for Docker Hub
    username: ${{ secrets.DOCKERHUB_USERNAME }}  # ❌ Add this secret
    password: ${{ secrets.DOCKERHUB_TOKEN }}  # ❌ Add this secret
```

#### File: `.github/workflows/terraform.yml`
**Line 8:** Update region if needed
```yaml
env:
  TF_VERSION: '1.6.0'  # ✅ OK
  AWS_REGION: 'us-east-1'  # ❌ Match your terraform region
```

---

### 7. Makefile

#### File: `Makefile`
**Line 2-5:** Already configured correctly ✅
```makefile
APP_NAME = snapverse-ai
DOCKER_IMAGE = h8815/ai-reel-generator  # ✅ Correct
DOCKER_REGISTRY = docker.io  # ✅ Correct
K8S_NAMESPACE = snapverse  # ✅ OK
```

---

## 📝 Step-by-Step Configuration Checklist

### Before Starting:

- [ ] **1. Create GitHub Secrets**
  ```
  Go to: https://github.com/h8815/AI-Reel-Generator-DevOps/settings/secrets/actions
  Add all required secrets listed in section 1
  ```

- [ ] **2. Get Docker Hub Token**
  ```
  1. Login to Docker Hub: https://hub.docker.com
  2. Go to Account Settings → Security
  3. Click "New Access Token"
  4. Name: "GitHub Actions"
  5. Copy token and add to GitHub Secrets as DOCKERHUB_TOKEN
  6. Add your username (h8815) as DOCKERHUB_USERNAME
  ```

- [ ] **3. Configure AWS**
  ```bash
  # Install AWS CLI
  aws configure
  # Enter your AWS Access Key ID
  # Enter your AWS Secret Access Key
  # Enter region: us-east-1 (or your preferred region)
  ```

- [ ] **4. Create Terraform Backend**
  ```bash
  # Create S3 bucket (use unique name)
  aws s3 mb s3://h8815-snapverse-terraform-state --region us-east-1
  
  # Enable versioning
  aws s3api put-bucket-versioning \
    --bucket h8815-snapverse-terraform-state \
    --versioning-configuration Status=Enabled
  
  # Create DynamoDB table
  aws dynamodb create-table \
    --table-name h8815-snapverse-terraform-locks \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region us-east-1
  ```

- [ ] **5. Update Terraform Files**
  ```bash
  # Copy example file
  cp terraform/terraform.tfvars.example terraform/terraform.tfvars
  
  # Edit with your values
  nano terraform/terraform.tfvars
  
  # Update backend in main.tf (lines 14-16)
  nano terraform/main.tf
  ```

- [ ] **6. Update Kubernetes Ingress**
  ```bash
  # Edit ingress.yaml
  nano k8s/ingress.yaml
  
  # Replace snapverse.yourdomain.com with your actual domain
  ```

- [ ] **7. Start SonarQube & Get Token**
  ```bash
  # Start SonarQube
  docker-compose up -d sonarqube sonarqube-db
  
  # Wait 2-3 minutes, then access http://localhost:9000
  # Login: admin/admin
  # Change password
  # Create project: snapverse-ai
  # Generate token
  # Add to GitHub Secrets
  ```

---

## 🔍 Quick Validation

Run these commands to verify your configuration:

```bash
# 1. Check GitHub secrets (should show names, not values)
gh secret list

# 2. Check AWS configuration
aws sts get-caller-identity

# 3. Check Docker login
docker login docker.io -u h8815

# 4. Validate Terraform
cd terraform
terraform init
terraform validate

# 5. Check Kubernetes config
kubectl cluster-info

# 6. Test local build
make docker-build
```

---

## 🚀 Ready to Deploy?

Once all configurations are set:

```bash
# Option 1: Automated setup
chmod +x setup-devops.sh
./setup-devops.sh

# Option 2: Manual deployment
make dev-setup          # Local development
make terraform-apply    # Provision infrastructure
make k8s-deploy        # Deploy to Kubernetes

# Option 3: Push to GitHub (triggers CI/CD)
git add .
git commit -m "Configure DevOps infrastructure"
git push origin main
```

---

## ⚠️ Common Issues

### Issue 1: Terraform Backend Error
**Error:** "Error loading state: AccessDenied"
**Solution:** Create S3 bucket and DynamoDB table first (see step 4 above)

### Issue 2: Docker Push Failed
**Error:** "denied: requested access to the resource is denied"
**Solution:** 
```bash
docker login docker.io -u h8815
# Enter your Docker Hub password or token
```

### Issue 3: Kubernetes Connection Failed
**Error:** "The connection to the server localhost:8080 was refused"
**Solution:**
```bash
# For AWS EKS
aws eks update-kubeconfig --name snapverse-ai-cluster --region us-east-1
```

### Issue 4: SonarQube Connection Failed
**Error:** "Could not connect to SonarQube server"
**Solution:**
```bash
# Check if SonarQube is running
docker-compose ps

# Restart if needed
docker-compose restart sonarqube
```

---

## 📞 Need Help?

1. Check [DEVOPS_CHECKLIST.md](DEVOPS_CHECKLIST.md) for detailed steps
2. Review [DEVOPS.md](DEVOPS.md) for comprehensive documentation
3. See [DEVOPS_QUICKSTART.md](DEVOPS_QUICKSTART.md) for quick commands

---

**Last Updated:** 2024
**Repository:** https://github.com/h8815/AI-Reel-Generator-DevOps
