#!/usr/bin/env pwsh
<#
.SYNOPSIS
E-Commerce API Test Script
Tests authentication and cart endpoints with automatic token management
#>

$API_BASE = "https://ecommerce-backend-2-88ro.onrender.com/api/v1"
$TIMESTAMP = Get-Date -Format "yyyyMMddHHmmss"
$EMAIL = "testuser_$TIMESTAMP@example.com"
$PASSWORD = "TestPass123!@"
$FIRST_NAME = "Test"
$LAST_NAME = "User"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "E-Commerce API Test Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Register User
Write-Host "Step 1: Registering new user..." -ForegroundColor Yellow
$registerBody = @{
    email = $EMAIL
    password = $PASSWORD
    password_confirm = $PASSWORD
    first_name = $FIRST_NAME
    last_name = $LAST_NAME
} | ConvertTo-Json

try {
    $registerResp = Invoke-WebRequest -Uri "$API_BASE/auth/register/" `
        -Method POST `
        -ContentType "application/json" `
        -Body $registerBody `
        -SkipCertificateCheck
    
    $registerData = $registerResp.Content | ConvertFrom-Json
    Write-Host "✅ Registration successful!" -ForegroundColor Green
    Write-Host "   Email: $EMAIL" -ForegroundColor Green
    Write-Host "   Password: $PASSWORD" -ForegroundColor Green
    Write-Host "   User ID: $($registerData.user.id)" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ Registration failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 2: Login
Write-Host "Step 2: Logging in..." -ForegroundColor Yellow
$loginBody = @{
    email = $EMAIL
    password = $PASSWORD
} | ConvertTo-Json

try {
    $loginResp = Invoke-WebRequest -Uri "$API_BASE/auth/login/" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginBody `
        -SkipCertificateCheck
    
    $loginData = $loginResp.Content | ConvertFrom-Json
    $ACCESS_TOKEN = $loginData.tokens.access
    $REFRESH_TOKEN = $loginData.tokens.refresh
    
    Write-Host "✅ Login successful!" -ForegroundColor Green
    Write-Host "   Access Token: $($ACCESS_TOKEN.Substring(0, 20))..." -ForegroundColor Green
    Write-Host "   User: $($loginData.user.first_name) $($loginData.user.last_name)" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 3: Test Protected Endpoints
Write-Host "Step 3: Testing protected endpoints..." -ForegroundColor Yellow
$headers = @{ "Authorization" = "Bearer $ACCESS_TOKEN" }

# 3a. Get Cart
Write-Host "`n📦 Testing Cart Endpoint..." -ForegroundColor Cyan
try {
    $cartResp = Invoke-WebRequest -Uri "$API_BASE/cart/" `
        -Method GET `
        -Headers $headers `
        -SkipCertificateCheck
    
    $cartData = $cartResp.Content | ConvertFrom-Json
    Write-Host "✅ Cart endpoint working!" -ForegroundColor Green
    Write-Host "   Items in cart: $($cartData.items.Count)" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Cart error: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 3b. Get Products
Write-Host "`n🛍️ Testing Products Endpoint..." -ForegroundColor Cyan
try {
    $productsResp = Invoke-WebRequest -Uri "$API_BASE/products/" `
        -Method GET `
        -SkipCertificateCheck
    
    $productsData = $productsResp.Content | ConvertFrom-Json
    Write-Host "✅ Products endpoint working!" -ForegroundColor Green
    Write-Host "   Total products: $($productsData.count)" -ForegroundColor Green
    
    if ($productsData.results.Count -gt 0) {
        Write-Host "   Sample product: $($productsData.results[0].name)" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Products error: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 3c. Get User Profile
Write-Host "`n👤 Testing User Profile Endpoint..." -ForegroundColor Cyan
try {
    $userResp = Invoke-WebRequest -Uri "$API_BASE/auth/me/" `
        -Method GET `
        -Headers $headers `
        -SkipCertificateCheck
    
    $userData = $userResp.Content | ConvertFrom-Json
    Write-Host "✅ User profile endpoint working!" -ForegroundColor Green
    Write-Host "   Email: $($userData.email)" -ForegroundColor Green
    Write-Host "   Name: $($userData.first_name) $($userData.last_name)" -ForegroundColor Green
} catch {
    Write-Host "⚠️ User profile error: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TEST COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Credentials for future use:" -ForegroundColor Yellow
Write-Host "  Email: $EMAIL" -ForegroundColor White
Write-Host "  Password: $PASSWORD" -ForegroundColor White
Write-Host ""
Write-Host "Tokens:" -ForegroundColor Yellow
Write-Host "  Access: $($ACCESS_TOKEN.Substring(0, 40))..." -ForegroundColor White
Write-Host "  Refresh: $($REFRESH_TOKEN.Substring(0, 40))..." -ForegroundColor White
Write-Host ""
Write-Host "API Base: $API_BASE" -ForegroundColor Cyan
Write-Host "Docs: https://ecommerce-backend-2-88ro.onrender.com/api/docs/" -ForegroundColor Cyan
