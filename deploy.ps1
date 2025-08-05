# PowerShell deployment script
Write-Host "Starting deployment to Vercel..." -ForegroundColor Green

# Change to zuoshihuice directory
Set-Location zuoshihuice
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow

# Build the project
Write-Host "Building project..." -ForegroundColor Blue
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host "Build successful, starting deployment..." -ForegroundColor Green

# Deploy to Vercel
npx vercel --prod

Write-Host "Deployment completed!" -ForegroundColor Green
Read-Host "Press Enter to continue"