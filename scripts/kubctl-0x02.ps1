# Blue-Green Deployment Switch Script for Windows PowerShell
# This script switches traffic between blue and green deployments

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("blue", "green")]
    [string]$Color,
    [string]$Namespace = "ecommerce"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Blue-Green Deployment Switch" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Switching traffic to: $Color" -ForegroundColor Yellow

# Get current service configuration
$service = kubectl get service ecommerce-api-service -n $Namespace -o json | ConvertFrom-Json
$currentSelector = $service.spec.selector.color

Write-Host "Current active deployment: $currentSelector" -ForegroundColor Cyan

if ($currentSelector -eq $Color) {
    Write-Host "  Deployment is already set to $Color" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Updating service selector..." -ForegroundColor Yellow

# Patch the service to switch selector
kubectl patch service ecommerce-api-service -n $Namespace -p "{\"spec\":{\"selector\":{\"app\":\"ecommerce-api\",\"color\":\"$Color\"}}}"

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Failed to update service" -ForegroundColor Red
    exit 1
}

Write-Host "  ✓ Service updated successfully" -ForegroundColor Green

Write-Host ""
Write-Host "Verifying deployment status..." -ForegroundColor Yellow

# Wait for pods to be ready
Start-Sleep -Seconds 5

$pods = kubectl get pods -n $Namespace -l "app=ecommerce-api,color=$Color" -o json | ConvertFrom-Json

if ($pods.items.Count -eq 0) {
    Write-Host "  ✗ No pods found for $Color deployment" -ForegroundColor Red
    Write-Host "  Please deploy the $Color deployment first" -ForegroundColor Yellow
    exit 1
}

Write-Host "  Pods for $Color deployment:" -ForegroundColor Cyan
foreach ($pod in $pods.items) {
    $status = $pod.status.phase
    $ready = ""
    if ($pod.status.conditions) {
        $readyCondition = $pod.status.conditions | Where-Object { $_.type -eq "Ready" }
        if ($readyCondition) {
            $ready = $readyCondition.status
        }
    }
    Write-Host "    - $($pod.metadata.name): $status (Ready: $ready)" -ForegroundColor $(if ($status -eq "Running" -and $ready -eq "True") { "Green" } else { "Yellow" })
}

Write-Host ""
Write-Host "Testing endpoint..." -ForegroundColor Yellow

# Setup port-forward for testing
$portForward = Start-Job -ScriptBlock {
    kubectl port-forward -n $using:Namespace service/ecommerce-api-service 8080:8000
}

Start-Sleep -Seconds 3

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/ready/" -Method Get -TimeoutSec 10
    Write-Host "  ✓ Endpoint is responding: $($response.StatusCode)" -ForegroundColor Green
    
    # Try to get version info
    try {
        $healthResponse = Invoke-RestMethod -Uri "http://localhost:8080/healthz/" -Method Get -TimeoutSec 5
        Write-Host "  ✓ Health check passed" -ForegroundColor Green
    } catch {
        Write-Host "  ! Health check endpoint may not be available" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ✗ Endpoint test failed: $_" -ForegroundColor Red
    Write-Host "  The deployment may still be starting up" -ForegroundColor Yellow
}

# Stop port-forward
Stop-Job $portForward
Remove-Job $portForward

Write-Host ""
Write-Host "Current Service Status:" -ForegroundColor Cyan
kubectl get service ecommerce-api-service -n $Namespace

Write-Host ""
Write-Host "Active Pods:" -ForegroundColor Cyan
kubectl get pods -n $Namespace -l "app=ecommerce-api,color=$Color"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Traffic switched to $Color deployment!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

