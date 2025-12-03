# Minikube Setup Script for Windows PowerShell
# This script sets up and verifies a local Kubernetes cluster using Minikube

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Minikube Kubernetes Cluster Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if command exists
function Test-Command {
    param($CommandName)
    $command = Get-Command $CommandName -ErrorAction SilentlyContinue
    if ($command) {
        return $true
    }
    return $false
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

$prerequisites = @("kubectl", "minikube", "docker")
$missing = @()

foreach ($cmd in $prerequisites) {
    if (Test-Command $cmd) {
        Write-Host "  ✓ $cmd is installed" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $cmd is NOT installed" -ForegroundColor Red
        $missing += $cmd
    }
}

if ($missing.Count -gt 0) {
    Write-Host ""
    Write-Host "Please install the following tools:" -ForegroundColor Red
    foreach ($cmd in $missing) {
        Write-Host "  - $cmd" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Installation links:" -ForegroundColor Yellow
    Write-Host "  - kubectl: https://kubernetes.io/docs/tasks/tools/" -ForegroundColor Yellow
    Write-Host "  - minikube: https://minikube.sigs.k8s.io/docs/start/" -ForegroundColor Yellow
    Write-Host "  - Docker: https://docs.docker.com/get-docker/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Starting Minikube cluster..." -ForegroundColor Yellow

# Check if minikube is already running
$minikubeStatus = minikube status --output json 2>$null | ConvertFrom-Json
if ($minikubeStatus.Host -eq "Running") {
    Write-Host "  Minikube is already running" -ForegroundColor Green
} else {
    Write-Host "  Starting Minikube cluster (this may take a few minutes)..." -ForegroundColor Yellow
    minikube start --driver=docker --memory=4096 --cpus=2 --disk-size=20g
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ✗ Failed to start Minikube" -ForegroundColor Red
        exit 1
    }
    Write-Host "  ✓ Minikube cluster started successfully" -ForegroundColor Green
}

Write-Host ""
Write-Host "Configuring kubectl context..." -ForegroundColor Yellow
minikube kubectl -- config use-context minikube
Write-Host "  ✓ kubectl configured" -ForegroundColor Green

Write-Host ""
Write-Host "Enabling addons..." -ForegroundColor Yellow
minikube addons enable ingress
minikube addons enable metrics-server
Write-Host "  ✓ Ingress addon enabled" -ForegroundColor Green
Write-Host "  ✓ Metrics server enabled" -ForegroundColor Green

Write-Host ""
Write-Host "Verifying cluster status..." -ForegroundColor Yellow

# Get cluster info
Write-Host ""
Write-Host "Cluster Information:" -ForegroundColor Cyan
minikube kubectl -- cluster-info

# Get nodes
Write-Host ""
Write-Host "Nodes:" -ForegroundColor Cyan
minikube kubectl -- get nodes

# Get all pods in kube-system namespace
Write-Host ""
Write-Host "System Pods (kube-system namespace):" -ForegroundColor Cyan
$systemPods = minikube kubectl -- get pods --namespace=kube-system --output=json | ConvertFrom-Json
Write-Host "  Total pods: $($systemPods.items.Count)" -ForegroundColor Green
foreach ($pod in $systemPods.items) {
    $status = $pod.status.phase
    if ($status -eq "Running") {
        Write-Host "    ✓ $($pod.metadata.name) - $status" -ForegroundColor Green
    } else {
        Write-Host "    ✗ $($pod.metadata.name) - $status" -ForegroundColor Yellow
    }
}

# Wait for all system pods to be ready
Write-Host ""
Write-Host "Waiting for all system pods to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
minikube kubectl -- wait --for=condition=ready pod --all --namespace=kube-system --timeout=120s

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To access the cluster:" -ForegroundColor Yellow
Write-Host "  kubectl get pods --all-namespaces" -ForegroundColor White
Write-Host ""
Write-Host "To get Minikube IP:" -ForegroundColor Yellow
Write-Host "  minikube ip" -ForegroundColor White
Write-Host ""
Write-Host "To open dashboard:" -ForegroundColor Yellow
Write-Host "  minikube dashboard" -ForegroundColor White
Write-Host ""


