# Rolling Update Script for Windows PowerShell
# This script performs a rolling update of the deployment

param(
    [Parameter(Mandatory=$true)]
    [string]$ImageVersion,
    [string]$Namespace = "ecommerce",
    [string]$DeploymentName = "ecommerce-api",
    [string]$ImageName = "ecommerce-api"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Rolling Update Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$fullImageName = "$ImageName`:$ImageVersion"

Write-Host "Updating deployment image to: $fullImageName" -ForegroundColor Yellow

# Get current deployment info
Write-Host ""
Write-Host "Current Deployment Status:" -ForegroundColor Cyan
kubectl get deployment/$DeploymentName -n $Namespace

# Perform rolling update
Write-Host ""
Write-Host "Starting rolling update..." -ForegroundColor Yellow
kubectl set image deployment/$DeploymentName $DeploymentName=$fullImageName -n $Namespace

if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ Failed to update deployment" -ForegroundColor Red
    exit 1
}

Write-Host "  ✓ Image updated successfully" -ForegroundColor Green

Write-Host ""
Write-Host "Monitoring rollout status..." -ForegroundColor Yellow

# Monitor rollout
kubectl rollout status deployment/$DeploymentName -n $Namespace --timeout=300s

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "  ✗ Rollout failed or timed out" -ForegroundColor Red
    Write-Host "  Use 'kubectl rollout undo deployment/$DeploymentName -n $Namespace' to rollback" -ForegroundColor Yellow
    exit 1
}

Write-Host "  ✓ Rollout completed successfully" -ForegroundColor Green

Write-Host ""
Write-Host "Verifying deployment..." -ForegroundColor Yellow

# Check pod status
$pods = kubectl get pods -n $Namespace -l app=$DeploymentName -o json | ConvertFrom-Json
$runningPods = ($pods.items | Where-Object { $_.status.phase -eq "Running" }).Count
$totalPods = $pods.items.Count

Write-Host "  Running pods: $runningPods/$totalPods" -ForegroundColor $(if ($runningPods -eq $totalPods) { "Green" } else { "Yellow" })

# Test endpoint
Write-Host ""
Write-Host "Testing endpoint..." -ForegroundColor Yellow

$portForward = Start-Job -ScriptBlock {
    kubectl port-forward -n $using:Namespace service/ecommerce-api-service 8080:8000
}

Start-Sleep -Seconds 3

$testCount = 0
$maxTests = 10

while ($testCount -lt $maxTests) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080/ready/" -Method Get -TimeoutSec 5 -ErrorAction Stop
        Write-Host "  ✓ Endpoint is responding: $($response.StatusCode)" -ForegroundColor Green
        break
    } catch {
        $testCount++
        if ($testCount -lt $maxTests) {
            Write-Host "  Waiting for endpoint... (attempt $testCount/$maxTests)" -ForegroundColor Yellow
            Start-Sleep -Seconds 5
        } else {
            Write-Host "  ✗ Endpoint test failed after $maxTests attempts" -ForegroundColor Red
        }
    }
}

# Stop port-forward
Stop-Job $portForward
Remove-Job $portForward

Write-Host ""
Write-Host "Final Deployment Status:" -ForegroundColor Cyan
kubectl get deployment/$DeploymentName -n $Namespace

Write-Host ""
Write-Host "Pod Status:" -ForegroundColor Cyan
kubectl get pods -n $Namespace -l app=$DeploymentName

Write-Host ""
Write-Host "Rollout History:" -ForegroundColor Cyan
kubectl rollout history deployment/$DeploymentName -n $Namespace

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Rolling update completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Current image version: $fullImageName" -ForegroundColor White
Write-Host ""

