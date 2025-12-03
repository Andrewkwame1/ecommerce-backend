# Kubernetes Deployment Setup Guide

Complete guide for setting up and deploying the Django E-commerce application on Kubernetes using Minikube.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Setup with Minikube](#local-setup-with-minikube)
3. [Building Docker Images](#building-docker-images)
4. [Deploying to Kubernetes](#deploying-to-kubernetes)
5. [Scaling and Load Testing](#scaling-and-load-testing)
6. [Zero-Downtime Deployments](#zero-downtime-deployments)
7. [CI/CD Pipeline](#cicd-pipeline)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

1. **Docker Desktop** or Docker Engine
   - Download from: https://docs.docker.com/get-docker/

2. **Minikube**
   - Windows: `choco install minikube` or download from https://minikube.sigs.k8s.io/docs/start/
   - Linux/Mac: See https://minikube.sigs.k8s.io/docs/start/

3. **kubectl** (Kubernetes CLI)
   - Windows: `choco install kubernetes-cli`
   - Linux/Mac: See https://kubernetes.io/docs/tasks/tools/

4. **Git** (for cloning repository)

### Optional Tools

- **wrk** - For load testing (https://github.com/wg/wrk)
- **Docker Hub account** - For pushing images (or use local Minikube)

## Local Setup with Minikube

### Step 1: Start Minikube Cluster

**Windows (PowerShell):**
```powershell
cd scripts
.\kurbeScript.ps1
```

**Linux/Mac:**
```bash
chmod +x scripts/kurbeScript
./scripts/kurbeScript
```

This script will:
- Check prerequisites
- Start Minikube cluster
- Enable Ingress and Metrics Server addons
- Verify cluster status

### Step 2: Verify Cluster

```bash
# Check cluster status
kubectl cluster-info

# Check nodes
kubectl get nodes

# Check system pods
kubectl get pods --all-namespaces
```

## Building Docker Images

### Option 1: Build Locally and Load into Minikube

```bash
# Navigate to e-commerce directory
cd e-commerce

# Build the image
docker build -t ecommerce-api:latest .

# Load into Minikube (if using Minikube)
minikube image load ecommerce-api:latest
```

### Option 2: Build and Push to Registry

```bash
# Build and tag
docker build -t your-username/ecommerce-api:latest ./e-commerce
docker tag your-username/ecommerce-api:latest your-username/ecommerce-api:1.0

# Login to Docker Hub
docker login

# Push images
docker push your-username/ecommerce-api:latest
docker push your-username/ecommerce-api:1.0
```

**Update deployment.yaml** to use your registry:
```yaml
image: your-username/ecommerce-api:latest
imagePullPolicy: Always
```

## Deploying to Kubernetes

### Step 1: Create Namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

### Step 2: Create Configuration

**Important:** Edit `k8s/secrets.yaml` with your actual secrets before applying!

```bash
# Apply ConfigMap
kubectl apply -f k8s/configmap.yaml

# Apply Secrets (update first!)
kubectl apply -f k8s/secrets.yaml
```

### Step 3: Deploy Dependencies

```bash
# Deploy PostgreSQL
kubectl apply -f k8s/postgres-deployment.yaml

# Deploy Redis
kubectl apply -f k8s/redis-deployment.yaml

# Deploy RabbitMQ
kubectl apply -f k8s/rabbitmq-deployment.yaml
```

Wait for dependencies to be ready:
```bash
kubectl wait --for=condition=ready pod -l app=postgres -n ecommerce --timeout=120s
kubectl wait --for=condition=ready pod -l app=redis -n ecommerce --timeout=120s
kubectl wait --for=condition=ready pod -l app=rabbitmq -n ecommerce --timeout=120s
```

### Step 4: Deploy Application

```bash
# Update deployment.yaml with your image name if needed
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### Step 5: Run Database Migrations

```bash
# Run migrations using kubectl exec
kubectl get pods -n ecommerce -l app=ecommerce-api

# Replace <pod-name> with actual pod name
kubectl exec -it <pod-name> -n ecommerce -- python manage.py migrate
```

Or migrations run automatically via initContainer in the deployment.

### Step 6: Deploy Ingress

```bash
kubectl apply -f k8s/ingress.yaml
```

### Step 7: Access the Application

**Get Minikube IP:**
```bash
minikube ip
```

**Add to hosts file:**

Windows: `C:\Windows\System32\drivers\etc\hosts`
Linux/Mac: `/etc/hosts`

Add this line (replace with your Minikube IP):
```
<minikube-ip> ecommerce.local
```

**Access the application:**
- API: http://ecommerce.local/api/
- Admin: http://ecommerce.local/admin/
- Health Check: http://ecommerce.local/healthz/

**Alternative - Port Forward:**
```bash
kubectl port-forward -n ecommerce service/ecommerce-api-service 8000:8000
```
Then access at: http://localhost:8000

## Scaling and Load Testing

### Manual Scaling

```bash
# Scale to 3 replicas
kubectl scale deployment/ecommerce-api --replicas=3 -n ecommerce

# Verify scaling
kubectl get pods -n ecommerce -l app=ecommerce-api
```

### Using Scaling Script

**Windows:**
```powershell
.\scripts\kubctl-0x01.ps1 3
```

**Linux/Mac:**
```bash
chmod +x scripts/kubctl-0x01
./scripts/kubctl-0x01 3
```

The script will:
- Scale the deployment
- Wait for rollout
- Monitor resource usage
- Perform load testing (if wrk is installed)

### Load Testing with wrk

```bash
# Install wrk first
# Then use the scaling script which includes load testing

# Or test manually
wrk -t4 -c50 -d30s http://localhost:8000/api/v1/products/
```

## Zero-Downtime Deployments

### Blue-Green Deployment

1. **Deploy both versions:**
```bash
kubectl apply -f k8s/blue-deployment.yaml
kubectl apply -f k8s/green-deployment.yaml
kubectl apply -f k8s/blue-green-service.yaml
```

2. **Switch traffic:**

**Windows:**
```powershell
# Switch to green deployment
.\scripts\kubctl-0x02.ps1 -Color green

# Switch back to blue
.\scripts\kubctl-0x02.ps1 -Color blue
```

**Linux/Mac:**
```bash
# Switch to green
kubectl patch service ecommerce-api-service -n ecommerce -p '{"spec":{"selector":{"app":"ecommerce-api","color":"green"}}}'

# Switch to blue
kubectl patch service ecommerce-api-service -n ecommerce -p '{"spec":{"selector":{"app":"ecommerce-api","color":"blue"}}}'
```

### Rolling Updates

**Windows:**
```powershell
.\scripts\kubctl-0x03.ps1 -ImageVersion 1.1
```

**Linux/Mac:**
```bash
# Update image
kubectl set image deployment/ecommerce-api ecommerce-api=ecommerce-api:1.1 -n ecommerce

# Monitor rollout
kubectl rollout status deployment/ecommerce-api -n ecommerce

# View rollout history
kubectl rollout history deployment/ecommerce-api -n ecommerce

# Rollback if needed
kubectl rollout undo deployment/ecommerce-api -n ecommerce
```

## CI/CD Pipeline

### GitHub Actions Setup

1. **Set up GitHub Secrets:**

Go to Repository Settings → Secrets and add:
- `DOCKER_USERNAME` - Your Docker Hub username
- `DOCKER_PASSWORD` - Your Docker Hub password/token

2. **Workflows:**

- **CI Workflow** (`.github/workflows/ci.yml`):
  - Runs on every push/PR
  - Tests code
  - Lints code
  - Builds Docker image (on main branch)

- **Deploy Workflow** (`.github/workflows/deploy.yml`):
  - Runs on pushes to main/master
  - Builds and pushes Docker image
  - Tags with version

3. **View Workflow Runs:**

Go to the Actions tab in your GitHub repository to see workflow runs.

### Automated Testing

The CI workflow automatically:
- Runs pytest tests
- Checks code coverage
- Runs flake8 linting
- Builds Docker image
- Tests Docker image health endpoint

### Automated Deployment

The deploy workflow:
- Builds Docker image with multiple tags
- Pushes to Docker Hub
- Can be extended to automatically update Kubernetes deployments

## Monitoring and Management

### View Pods and Status

```bash
# List all pods
kubectl get pods -n ecommerce

# Get detailed pod info
kubectl describe pod <pod-name> -n ecommerce

# View pod logs
kubectl logs -f <pod-name> -n ecommerce

# View logs from all pods
kubectl logs -f -l app=ecommerce-api -n ecommerce
```

### Resource Usage

```bash
# Pod resource usage
kubectl top pods -n ecommerce

# Node resource usage
kubectl top nodes
```

### Health Checks

```bash
# Check health endpoint
curl http://localhost:8000/healthz/

# Check readiness
curl http://localhost:8000/ready/
```

### Events and Debugging

```bash
# View recent events
kubectl get events -n ecommerce --sort-by='.lastTimestamp'

# Describe deployment
kubectl describe deployment/ecommerce-api -n ecommerce

# Describe service
kubectl describe service/ecommerce-api-service -n ecommerce
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n ecommerce

# Check pod events
kubectl describe pod <pod-name> -n ecommerce

# Check logs
kubectl logs <pod-name> -n ecommerce
```

Common issues:
- Image pull errors → Load image into Minikube or check image name
- Database connection → Check postgres pod status
- Resource limits → Check if resources are available

### Database Connection Issues

```bash
# Check postgres pod
kubectl logs -l app=postgres -n ecommerce

# Test connection from app pod
kubectl exec -it <app-pod> -n ecommerce -- python manage.py dbshell
```

### Ingress Not Working

```bash
# Check ingress status
kubectl get ingress -n ecommerce

# Check ingress controller
kubectl get pods -n ingress-nginx

# Get ingress IP
minikube service ingress-nginx-controller -n ingress-nginx --url
```

### Image Pull Errors

```bash
# Load image into Minikube
minikube image load ecommerce-api:latest

# Or use local image pull policy
# Set imagePullPolicy: Never in deployment.yaml
```

## Cleanup

### Remove All Resources

```bash
# Delete all resources in namespace
kubectl delete -f k8s/

# Or delete entire namespace
kubectl delete namespace ecommerce
```

### Stop Minikube

```bash
# Stop cluster
minikube stop

# Delete cluster (optional)
minikube delete
```

## Next Steps

1. **Production Deployment:**
   - Use managed Kubernetes (GKE, EKS, AKS)
   - Set up proper secrets management
   - Configure TLS certificates
   - Set up monitoring (Prometheus, Grafana)

2. **Auto-Scaling:**
   - Configure Horizontal Pod Autoscaler (HPA)
   - Set resource-based scaling

3. **CI/CD Enhancement:**
   - Automatic deployment on image push
   - Integration with ArgoCD or Flux
   - Automated rollback on failures

4. **Monitoring:**
   - Add Prometheus metrics
   - Set up Grafana dashboards
   - Configure alerting

## Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [Docker Documentation](https://docs.docker.com/)

