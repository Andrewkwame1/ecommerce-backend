# Kubernetes Quick Start Guide

Get your Django E-commerce application running on Kubernetes in minutes!

## Prerequisites Check

```bash
# Check if tools are installed
docker --version
kubectl version --client
minikube version
```

If any are missing, install them first (see KUBERNETES_SETUP.md for links).

## Quick Deployment (5 Steps)

### 1. Start Minikube

**Windows:**
```powershell
.\scripts\kurbeScript.ps1
```

**Linux/Mac:**
```bash
chmod +x scripts/kurbeScript
./scripts/kurbeScript
```

### 2. Build Docker Image

```bash
cd e-commerce
docker build -t ecommerce-api:latest .
minikube image load ecommerce-api:latest
cd ..
```

### 3. Update Secrets

**IMPORTANT:** Edit `k8s/secrets.yaml` and change at least:
- `DJANGO_SECRET_KEY` - Use a secure random key
- `DB_PASSWORD` - Change from default

### 4. Deploy Everything

```bash
# Create namespace and config
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml

# Deploy dependencies
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/rabbitmq-deployment.yaml

# Wait for dependencies (about 30 seconds)
kubectl wait --for=condition=ready pod -l app=postgres -n ecommerce --timeout=120s
kubectl wait --for=condition=ready pod -l app=redis -n ecommerce --timeout=120s

# Deploy application
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

### 5. Access the Application

**Option A: Port Forward (Easiest)**
```bash
kubectl port-forward -n ecommerce service/ecommerce-api-service 8000:8000
```
Then open: http://localhost:8000

**Option B: Via Ingress**

1. Get Minikube IP:
   ```bash
   minikube ip
   ```

2. Add to hosts file:
   ```
   <minikube-ip> ecommerce.local
   ```

3. Open: http://ecommerce.local

## Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n ecommerce

# Check services
kubectl get svc -n ecommerce

# Test health endpoint
curl http://localhost:8000/healthz/
```

## Common Operations

### View Logs
```bash
kubectl logs -f -l app=ecommerce-api -n ecommerce
```

### Scale Deployment
```bash
kubectl scale deployment/ecommerce-api --replicas=3 -n ecommerce
```

### Update Deployment
```bash
# Update image version
kubectl set image deployment/ecommerce-api ecommerce-api=ecommerce-api:1.1 -n ecommerce

# Monitor rollout
kubectl rollout status deployment/ecommerce-api -n ecommerce
```

### Run Database Migrations
```bash
# Get pod name
kubectl get pods -n ecommerce -l app=ecommerce-api

# Run migrations
kubectl exec -it <pod-name> -n ecommerce -- python manage.py migrate
```

## Troubleshooting

### Pods Not Starting
```bash
kubectl describe pod <pod-name> -n ecommerce
kubectl logs <pod-name> -n ecommerce
```

### Image Pull Errors
```bash
minikube image load ecommerce-api:latest
```

### Can't Access Application
```bash
# Check service
kubectl get svc -n ecommerce

# Use port-forward instead
kubectl port-forward -n ecommerce service/ecommerce-api-service 8000:8000
```

## Cleanup

```bash
# Delete all resources
kubectl delete -f k8s/

# Stop Minikube
minikube stop
```

## Next Steps

- See `KUBERNETES_SETUP.md` for detailed documentation
- See `k8s/README.md` for advanced operations
- See `DEPLOYMENT_CHECKLIST.md` for production readiness

## Getting Help

Check the logs first:
```bash
kubectl logs -l app=ecommerce-api -n ecommerce
kubectl get events -n ecommerce --sort-by='.lastTimestamp'
```

For more help, see the troubleshooting section in `KUBERNETES_SETUP.md`.

