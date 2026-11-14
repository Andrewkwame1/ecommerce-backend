# Kubernetes Deployment Guide

This directory contains all Kubernetes manifests for deploying the E-commerce Django application on Kubernetes.

## Prerequisites

1. **Minikube** - Local Kubernetes cluster
2. **kubectl** - Kubernetes command-line tool
3. **Docker** - Container runtime
4. **Docker image** - Build and tag your Docker image

## Quick Start

### 1. Set up Minikube Cluster

**Windows (PowerShell):**
```powershell
.\scripts\kurbeScript.ps1
```

**Linux/Mac:**
```bash
chmod +x scripts/kurbeScript
./scripts/kurbeScript
```

### 2. Build and Load Docker Image

```bash
# Build the Docker image
cd e-commerce
docker build -t ecommerce-api:latest .

# Load image into Minikube
minikube image load ecommerce-api:latest
```

Or use a Docker registry:
```bash
docker tag ecommerce-api:latest your-username/ecommerce-api:latest
docker push your-username/ecommerce-api:latest
```

### 3. Create Namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

### 4. Create ConfigMap and Secrets

**Important:** Update `k8s/secrets.yaml` with your actual secrets before applying!

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
```

### 5. Deploy Dependencies

```bash
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/rabbitmq-deployment.yaml
```

Wait for all services to be ready:
```bash
kubectl wait --for=condition=ready pod -l app=postgres -n ecommerce --timeout=120s
kubectl wait --for=condition=ready pod -l app=redis -n ecommerce --timeout=120s
kubectl wait --for=condition=ready pod -l app=rabbitmq -n ecommerce --timeout=120s
```

### 6. Deploy Application

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### 7. Deploy Ingress

```bash
kubectl apply -f k8s/ingress.yaml
```

### 8. Access the Application

**Get Minikube IP:**
```bash
minikube ip
```

**Add to hosts file:**
```bash
# Windows: C:\Windows\System32\drivers\etc\hosts
# Linux/Mac: /etc/hosts

<minikube-ip> ecommerce.local
```

**Access the application:**
- API: http://ecommerce.local/api/
- Admin: http://ecommerce.local/admin/
- Health: http://ecommerce.local/healthz/

Or use port-forward:
```bash
kubectl port-forward -n ecommerce service/ecommerce-api-service 8000:8000
```

Then access at: http://localhost:8000

## File Structure

```
k8s/
├── namespace.yaml           # Namespace definition
├── configmap.yaml           # Configuration values
├── secrets.yaml             # Secrets (update before use!)
├── postgres-deployment.yaml # PostgreSQL database
├── redis-deployment.yaml    # Redis cache
├── rabbitmq-deployment.yaml # RabbitMQ message broker
├── deployment.yaml          # Main application deployment
├── service.yaml             # ClusterIP service
├── ingress.yaml             # NGINX Ingress
├── blue-deployment.yaml     # Blue deployment for blue-green
├── green-deployment.yaml    # Green deployment for blue-green
└── blue-green-service.yaml  # Service for blue-green switching
```

## Scaling

### Manual Scaling

```bash
kubectl scale deployment/ecommerce-api --replicas=3 -n ecommerce
```

### Using Script

**Windows:**
```powershell
.\scripts\kubctl-0x01.ps1 3
```

**Linux/Mac:**
```bash
./scripts/kubctl-0x01 3
```

## Blue-Green Deployment

### 1. Deploy Both Versions

```bash
kubectl apply -f k8s/blue-deployment.yaml
kubectl apply -f k8s/green-deployment.yaml
kubectl apply -f k8s/blue-green-service.yaml
```

### 2. Switch Traffic

**Windows:**
```powershell
# Switch to green
.\scripts\kubctl-0x02.ps1 -Color green

# Switch to blue
.\scripts\kubctl-0x02.ps1 -Color blue
```

**Linux/Mac:**
```bash
# Switch to green
kubectl patch service ecommerce-api-service -n ecommerce -p '{"spec":{"selector":{"app":"ecommerce-api","color":"green"}}}'

# Switch to blue
kubectl patch service ecommerce-api-service -n ecommerce -p '{"spec":{"selector":{"app":"ecommerce-api","color":"blue"}}}'
```

## Rolling Updates

**Windows:**
```powershell
.\scripts\kubctl-0x03.ps1 -ImageVersion 1.1
```

**Linux/Mac:**
```bash
kubectl set image deployment/ecommerce-api ecommerce-api=ecommerce-api:1.1 -n ecommerce
kubectl rollout status deployment/ecommerce-api -n ecommerce
```

## Monitoring

### View Pods

```bash
kubectl get pods -n ecommerce
kubectl get pods -n ecommerce -l app=ecommerce-api
```

### View Logs

```bash
# All pods
kubectl logs -f -l app=ecommerce-api -n ecommerce

# Specific pod
kubectl logs -f <pod-name> -n ecommerce
```

### View Events

```bash
kubectl get events -n ecommerce --sort-by='.lastTimestamp'
```

### Resource Usage

```bash
kubectl top pods -n ecommerce
kubectl top nodes
```

### Describe Resources

```bash
kubectl describe deployment/ecommerce-api -n ecommerce
kubectl describe service/ecommerce-api-service -n ecommerce
kubectl describe pod/<pod-name> -n ecommerce
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

### Database Connection Issues

```bash
# Check postgres pod
kubectl logs -l app=postgres -n ecommerce

# Test connection
kubectl exec -it <postgres-pod> -n ecommerce -- psql -U postgres -d ecommerce
```

### Image Pull Errors

```bash
# If using Minikube, load image directly
minikube image load ecommerce-api:latest

# Or check image pull secrets
kubectl get secrets -n ecommerce
```

### Ingress Not Working

```bash
# Check ingress status
kubectl get ingress -n ecommerce

# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller
```

## Cleanup

```bash
# Delete all resources
kubectl delete -f k8s/

# Or delete namespace (removes everything)
kubectl delete namespace ecommerce

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

## Production Considerations

Before deploying to production:

1. **Update Secrets:** Change all default secrets in `k8s/secrets.yaml`
2. **Use Image Registry:** Push images to a proper registry (Docker Hub, GCR, ECR, etc.)
3. **Configure Resource Limits:** Adjust based on your workload
4. **Enable TLS:** Configure SSL certificates for Ingress
5. **Set up Monitoring:** Add Prometheus and Grafana
6. **Configure Backups:** Set up database backups
7. **Network Policies:** Add network security policies
8. **Pod Security:** Configure pod security standards
9. **Horizontal Pod Autoscaler:** Enable auto-scaling
10. **Persistent Volumes:** Use proper storage classes for production data

## Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)

