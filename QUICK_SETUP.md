# ⚡ QUICK SETUP - What You MUST Change

## 🔴 CRITICAL - Change These First

### 1. GitHub Secrets (Add in Repository Settings)
```
DOCKERHUB_USERNAME = h8815
DOCKERHUB_TOKEN = <your-docker-hub-token>
AWS_ACCESS_KEY_ID = <your-aws-key>
AWS_SECRET_ACCESS_KEY = <your-aws-secret>
SONAR_TOKEN = <generate-after-sonarqube-setup>
SONAR_HOST_URL = http://localhost:9000 (or your server)
KUBE_CONFIG = <base64-encoded-kubeconfig>
DB_PASSWORD = <your-secure-password>
```

### 2. Kubernetes Ingress Domain
**File:** `k8s/ingress.yaml`
**Lines 14-15 & 18:**
```yaml
# CHANGE THIS:
- hosts:
  - snapverse.yourdomain.com  # ← Replace with YOUR domain
  
rules:
  - host: snapverse.yourdomain.com  # ← Replace with YOUR domain
```

### 3. Terraform Backend
**File:** `terraform/main.tf`
**Lines 14-19:**
```hcl
backend "s3" {
  bucket         = "h8815-snapverse-terraform-state"  # ← Make unique
  key            = "snapverse/terraform.tfstate"
  region         = "us-east-1"  # ← Match your region
  encrypt        = true
  dynamodb_table = "h8815-snapverse-terraform-locks"  # ← Make unique
}
```

**Create these AWS resources FIRST:**
```bash
aws s3 mb s3://h8815-snapverse-terraform-state --region us-east-1
aws s3api put-bucket-versioning --bucket h8815-snapverse-terraform-state --versioning-configuration Status=Enabled
aws dynamodb create-table --table-name h8815-snapverse-terraform-locks --attribute-definitions AttributeName=LockID,AttributeType=S --key-schema AttributeName=LockID,KeyType=HASH --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 --region us-east-1
```

### 4. Terraform Variables
**File:** `terraform/terraform.tfvars` (Create from example)
```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
```

**Edit these values:**
```hcl
aws_region   = "us-east-1"  # ← Your AWS region
availability_zones = ["us-east-1a", "us-east-1b"]  # ← Match your region
db_username = "your_admin_username"  # ← Change for security
```

**Set password:**
```bash
export TF_VAR_db_password="YourSecurePassword123!"
```

---

## ✅ Already Configured (No Changes Needed)

- ✅ Docker image: `h8815/ai-reel-generator`
- ✅ GitHub repo: `https://github.com/h8815/AI-Reel-Generator-DevOps.git`
- ✅ Kubernetes deployment image
- ✅ CI/CD workflows
- ✅ Makefile
- ✅ Docker Compose

---

## 📋 Setup Order

1. **Add GitHub Secrets** (5 min)
2. **Create AWS Resources** (S3 + DynamoDB) (5 min)
3. **Update Terraform Files** (main.tf + terraform.tfvars) (5 min)
4. **Update Kubernetes Ingress** (your domain) (2 min)
5. **Start SonarQube & Generate Token** (10 min)
6. **Deploy!** 🚀

---

## 🚀 Quick Deploy Commands

```bash
# 1. Local Development
docker-compose up -d

# 2. Infrastructure
cd terraform
terraform init
terraform apply

# 3. Kubernetes
kubectl apply -f k8s/

# 4. Or use automated script
./setup-devops.sh
```

---

## 📞 Full Details

See [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md) for complete instructions.
