# Scaling and Load Testing Script for Windows PowerShell
# This script scales the deployment and performs load testing

param(
    [int]$Replicas = 3,
    [string]$Namespace = "ecommerce",
    [string]$DeploymentName = "ecommerce-api"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Scaling and Load Testing" -ForegroundColor Cyan
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

if (-not (Test-Command "kubectl")) {
    Write-Host "  ✗ kubectl is NOT installed" -ForegroundColor Red
    exit 1
}
Write-Host "  ✓ kubectl is installed" -ForegroundColor Green

# Check if wrk is available (optional for load testing)
$hasWrk = Test-Command "wrk"
if ($hasWrk) {
    Write-Host "  ✓ wrk is installed" -ForegroundColor Green
} else {
    Write-Host "  ! wrk is not installed (load testing will be skipped)" -ForegroundColor Yellow
    Write-Host "    Install from: https://github.com/wg/wrk" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Scaling deployment to $Replicas replicas..." -ForegroundColor Yellow
kubectl scale deployment/$DeploymentName --replicas=$Replicas -n $Namespace

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Failed to scale deployment" -ForegroundColor Red
    exit 1
}

Write-Host "  ✓ Deployment scaled successfully" -ForegroundColor Green

Write-Host ""
Write-Host "Waiting for rollout to complete..." -ForegroundColor Yellow
kubectl rollout status deployment/$DeploymentName -n $Namespace --timeout=120s

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Rollout failed" -ForegroundColor Red
    exit 1
}

Write-Host "  ✓ Rollout completed successfully" -ForegroundColor Green

Write-Host ""
Write-Host "Current Pod Status:" -ForegroundColor Cyan
kubectl get pods -n $Namespace -l app=$DeploymentName

Write-Host ""
Write-Host "Resource Usage:" -ForegroundColor Cyan
kubectl top pods -n $Namespace -l app=$DeploymentName 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Metrics server not available or pods not ready yet" -ForegroundColor Yellow
}

# Get service endpoint
Write-Host ""
Write-Host "Getting service endpoint..." -ForegroundColor Yellow
$service = kubectl get service ecommerce-api-service -n $Namespace -o json | ConvertFrom-Json
$servicePort = $service.spec.ports[0].port

# Try to get ingress IP or use port-forward
Write-Host "Setting up port-forward for testing..." -ForegroundColor Yellow
$portForward = Start-Job -ScriptBlock {
    kubectl port-forward -n $using:Namespace service/ecommerce-api-service 8080:$using:servicePort
}

Start-Sleep -Seconds 3

$testUrl = "http://localhost:8080"

# Load testing with wrk
if ($hasWrk) {
    Write-Host ""
    Write-Host "Starting load test..." -ForegroundColor Yellow
    Write-Host "  URL: $testUrl" -ForegroundColor White
    Write-Host "  Threads: 4" -ForegroundColor White
    Write-Host "  Connections: 50" -ForegroundColor White
    Write-Host "  Duration: 30s" -ForegroundColor White
    Write-Host ""
    
    wrk -t4 -c50 -d30s $testUrl/ready/
    
    Write-Host ""
    Write-Host "Load test completed" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Skipping load test (wrk not installed)" -ForegroundColor Yellow
    Write-Host "Testing endpoint manually..." -ForegroundColor Yellow
    
    try {
        $response = Invoke-WebRequest -Uri "$testUrl/ready/" -Method Get -TimeoutSec 5
        Write-Host "  ✓ Endpoint is responding: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Endpoint test failed: $_" -ForegroundColor Red
    }
}

# Stop port-forward job
Stop-Job $portForward
Remove-Job $portForward

Write-Host ""
Write-Host "Final Status:" -ForegroundColor Cyan
kubectl get deployment/$DeploymentName -n $Namespace
Write-Host ""
kubectl get pods -n $Namespace -l app=$DeploymentName

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Scaling and Testing Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""


