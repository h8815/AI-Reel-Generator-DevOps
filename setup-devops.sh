#!/bin/bash

# SnapVerse AI - DevOps Setup Script
# This script sets up the complete DevOps environment

set -e

echo "🚀 SnapVerse AI - DevOps Setup"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."
echo ""

MISSING_TOOLS=()

if ! command_exists docker; then
    MISSING_TOOLS+=("docker")
    print_error "Docker is not installed"
else
    print_success "Docker is installed"
fi

if ! command_exists kubectl; then
    MISSING_TOOLS+=("kubectl")
    print_error "kubectl is not installed"
else
    print_success "kubectl is installed"
fi

if ! command_exists terraform; then
    MISSING_TOOLS+=("terraform")
    print_error "Terraform is not installed"
else
    print_success "Terraform is installed"
fi

if ! command_exists aws; then
    MISSING_TOOLS+=("aws-cli")
    print_error "AWS CLI is not installed"
else
    print_success "AWS CLI is installed"
fi

if ! command_exists python3; then
    MISSING_TOOLS+=("python3")
    print_error "Python 3 is not installed"
else
    print_success "Python 3 is installed"
fi

echo ""

if [ ${#MISSING_TOOLS[@]} -ne 0 ]; then
    print_error "Missing tools: ${MISSING_TOOLS[*]}"
    echo ""
    echo "Please install missing tools before continuing:"
    echo "  Docker: https://docs.docker.com/get-docker/"
    echo "  kubectl: https://kubernetes.io/docs/tasks/tools/"
    echo "  Terraform: https://www.terraform.io/downloads"
    echo "  AWS CLI: https://aws.amazon.com/cli/"
    echo "  Python 3: https://www.python.org/downloads/"
    exit 1
fi

# Setup options
echo "Select setup option:"
echo "1) Local Development (Docker Compose)"
echo "2) Kubernetes Deployment"
echo "3) Terraform Infrastructure"
echo "4) Full Setup (All of the above)"
echo "5) Security Scanning Only"
echo ""
read -p "Enter option (1-5): " SETUP_OPTION

case $SETUP_OPTION in
    1)
        echo ""
        print_info "Setting up Local Development environment..."
        
        # Install Python dependencies
        print_info "Installing Python dependencies..."
        pip install -r requirements.txt
        print_success "Python dependencies installed"
        
        # Start Docker Compose
        print_info "Starting Docker Compose services..."
        docker-compose up -d
        print_success "Docker Compose services started"
        
        echo ""
        print_success "Local Development setup complete!"
        echo ""
        echo "Access services at:"
        echo "  App: http://localhost:5000"
        echo "  SonarQube: http://localhost:9000 (admin/admin)"
        echo "  Trivy: http://localhost:8080"
        ;;
        
    2)
        echo ""
        print_info "Setting up Kubernetes deployment..."
        
        # Check if kubectl is configured
        if ! kubectl cluster-info &> /dev/null; then
            print_error "kubectl is not configured. Please configure kubectl first:"
            echo "  aws eks update-kubeconfig --name <cluster-name> --region <region>"
            exit 1
        fi
        
        # Apply Kubernetes manifests
        print_info "Applying Kubernetes manifests..."
        kubectl apply -f k8s/
        print_success "Kubernetes resources created"
        
        # Wait for deployment
        print_info "Waiting for deployment to be ready..."
        kubectl wait --for=condition=available --timeout=300s deployment/snapverse-ai -n snapverse
        print_success "Deployment is ready"
        
        echo ""
        print_success "Kubernetes deployment complete!"
        echo ""
        echo "Check status with:"
        echo "  kubectl get all -n snapverse"
        ;;
        
    3)
        echo ""
        print_info "Setting up Terraform infrastructure..."
        
        # Check AWS credentials
        if ! aws sts get-caller-identity &> /dev/null; then
            print_error "AWS credentials not configured. Please run: aws configure"
            exit 1
        fi
        
        cd terraform
        
        # Check if terraform.tfvars exists
        if [ ! -f terraform.tfvars ]; then
            print_info "Creating terraform.tfvars from example..."
            cp terraform.tfvars.example terraform.tfvars
            print_info "Please edit terraform/terraform.tfvars with your values"
            read -p "Press Enter after editing terraform.tfvars..."
        fi
        
        # Initialize Terraform
        print_info "Initializing Terraform..."
        terraform init
        print_success "Terraform initialized"
        
        # Plan
        print_info "Planning Terraform changes..."
        terraform plan
        
        # Ask for confirmation
        read -p "Apply these changes? (yes/no): " CONFIRM
        if [ "$CONFIRM" = "yes" ]; then
            terraform apply -auto-approve
            print_success "Infrastructure provisioned"
        else
            print_info "Terraform apply cancelled"
        fi
        
        cd ..
        ;;
        
    4)
        echo ""
        print_info "Running full setup..."
        
        # Local Development
        print_info "Step 1/3: Setting up Local Development..."
        pip install -r requirements.txt
        docker-compose up -d
        print_success "Local Development ready"
        
        # Kubernetes (if configured)
        if kubectl cluster-info &> /dev/null; then
            print_info "Step 2/3: Deploying to Kubernetes..."
            kubectl apply -f k8s/
            print_success "Kubernetes deployment complete"
        else
            print_info "Step 2/3: Skipping Kubernetes (not configured)"
        fi
        
        # Terraform (if AWS configured)
        if aws sts get-caller-identity &> /dev/null; then
            print_info "Step 3/3: Terraform setup..."
            cd terraform
            if [ ! -f terraform.tfvars ]; then
                cp terraform.tfvars.example terraform.tfvars
                print_info "Please edit terraform/terraform.tfvars and run: terraform apply"
            else
                terraform init
                print_info "Run 'terraform apply' to provision infrastructure"
            fi
            cd ..
        else
            print_info "Step 3/3: Skipping Terraform (AWS not configured)"
        fi
        
        echo ""
        print_success "Full setup complete!"
        ;;
        
    5)
        echo ""
        print_info "Running security scans..."
        
        # Trivy filesystem scan
        print_info "Running Trivy filesystem scan..."
        if command_exists trivy; then
            trivy fs --config trivy.yaml .
            print_success "Trivy scan complete"
        else
            print_error "Trivy not installed. Install from: https://aquasecurity.github.io/trivy/"
        fi
        
        # SonarQube scan
        print_info "Running SonarQube scan..."
        if command_exists sonar-scanner; then
            sonar-scanner
            print_success "SonarQube scan complete"
        else
            print_info "SonarQube scanner not installed. Skipping..."
        fi
        
        echo ""
        print_success "Security scans complete!"
        ;;
        
    *)
        print_error "Invalid option"
        exit 1
        ;;
esac

echo ""
print_success "Setup completed successfully!"
echo ""
echo "Next steps:"
echo "  - Review DEVOPS_QUICKSTART.md for quick commands"
echo "  - Check DEVOPS.md for detailed documentation"
echo "  - Run 'make help' to see available commands"
echo ""
