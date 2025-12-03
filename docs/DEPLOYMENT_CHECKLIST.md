# Kubernetes Deployment Checklist

Use this checklist to ensure all components are properly set up for Kubernetes deployment.

## Pre-Deployment Checklist

### Environment Setup
- [ ] Docker installed and running
- [ ] Minikube installed
- [ ] kubectl installed and configured
- [ ] Git repository cloned

### Configuration
- [ ] Update `k8s/secrets.yaml` with secure values:
  - [ ] DJANGO_SECRET_KEY (generate secure random key)
  - [ ] DB_PASSWORD
  - [ ] Email credentials (if using)
  - [ ] Stripe keys (if using)
- [ ] Review `k8s/configmap.yaml` settings
- [ ] Verify Docker image name matches deployment.yaml

### Docker Image
- [ ] Docker image built successfully
- [ ] Image tagged appropriately (e.g., ecommerce-api:latest)
- [ ] Image loaded into Minikube OR pushed to registry

## Deployment Checklist

### Cluster Setup
- [ ] Minikube cluster started
- [ ] Ingress addon enabled
- [ ] Metrics server enabled
- [ ] Cluster verified (kubectl cluster-info)

### Namespace and Config
- [ ] Namespace created
- [ ] ConfigMap applied
- [ ] Secrets applied

### Dependencies
- [ ] PostgreSQL deployed and ready
- [ ] Redis deployed and ready
- [ ] RabbitMQ deployed and ready
- [ ] All dependency pods running

### Application
- [ ] Deployment created
- [ ] Service created
- [ ] Ingress configured
- [ ] All application pods running
- [ ] Health checks passing

### Database
- [ ] Migrations completed
- [ ] Database accessible from application pods
- [ ] Test data loaded (optional)

## Post-Deployment Checklist

### Verification
- [ ] Application accessible via Ingress
- [ ] Health endpoint responding (/healthz/)
- [ ] Readiness endpoint responding (/ready/)
- [ ] API endpoints accessible
- [ ] Admin panel accessible

### Testing
- [ ] Test basic API endpoints
- [ ] Test authentication endpoints
- [ ] Test database connectivity
- [ ] Test cache (Redis) connectivity
- [ ] Test message broker (RabbitMQ) connectivity

### Scaling
- [ ] Successfully scaled to 3 replicas
- [ ] Load testing completed (optional)
- [ ] Resource usage monitored

### Zero-Downtime Deployment
- [ ] Blue-Green deployment tested
- [ ] Rolling update tested
- [ ] Rollback procedure tested

## CI/CD Checklist

### GitHub Actions
- [ ] GitHub Secrets configured:
  - [ ] DOCKER_USERNAME
  - [ ] DOCKER_PASSWORD
- [ ] CI workflow working
- [ ] Tests passing
- [ ] Docker image builds successfully
- [ ] Deploy workflow working

### Automation
- [ ] Tests run on every push/PR
- [ ] Docker images built automatically
- [ ] Images pushed to registry
- [ ] Deployment automation configured (optional)

## Monitoring Checklist

- [ ] Pod logs accessible
- [ ] Resource usage visible (kubectl top)
- [ ] Events monitored
- [ ] Health checks configured and working
- [ ] Alerts configured (optional)

## Security Checklist

- [ ] Secrets stored securely (not in code)
- [ ] Image pull secrets configured (if using private registry)
- [ ] Resource limits set
- [ ] Network policies configured (optional)
- [ ] TLS certificates configured (for production)

## Documentation

- [ ] README.md updated
- [ ] KUBERNETES_SETUP.md reviewed
- [ ] k8s/README.md reviewed
- [ ] Troubleshooting guide available

## Production Readiness (For Production Deployments)

- [ ] Use managed Kubernetes service (GKE/EKS/AKS)
- [ ] Configure proper storage classes
- [ ] Set up backup strategy
- [ ] Configure monitoring and alerting
- [ ] Set up log aggregation
- [ ] Configure auto-scaling
- [ ] Set up disaster recovery plan
- [ ] Security audit completed
- [ ] Performance testing completed
- [ ] Load testing completed

## Quick Verification Commands

```bash
# Check all pods are running
kubectl get pods -n ecommerce

# Check services
kubectl get svc -n ecommerce

# Check ingress
kubectl get ingress -n ecommerce

# Test health endpoint
curl http://localhost:8000/healthz/

# Check logs
kubectl logs -l app=ecommerce-api -n ecommerce

# Check resource usage
kubectl top pods -n ecommerce
```

## Rollback Plan

If something goes wrong:

1. **Quick Rollback:**
   ```bash
   kubectl rollout undo deployment/ecommerce-api -n ecommerce
   ```

2. **Switch Blue-Green:**
   ```bash
   kubectl patch service ecommerce-api-service -n ecommerce -p '{"spec":{"selector":{"color":"blue"}}}'
   ```

3. **Delete and Recreate:**
   ```bash
   kubectl delete -f k8s/deployment.yaml
   kubectl apply -f k8s/deployment.yaml
   ```

4. **Complete Cleanup:**
   ```bash
   kubectl delete namespace ecommerce
   ```

---

**Last Updated:** $(date)
**Status:** Ready for deployment

