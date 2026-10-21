# ==============================================================================
# CloudOps Pulse - Automated CI/CD Watcher & Kubernetes Deployer
# Automatically detects GitHub commits, builds Docker image, and deploys to K8s
# ==============================================================================

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  🚀 KUBERNETES CI/CD LIVE AUTO-DEPLOYER IS RUNNING" -ForegroundColor Green
Write-Host "  Watching GitHub repository: Prats1729/CICD (branch: main)" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan

# Verify Minikube & Kubectl connection
$k8sStatus = kubectl cluster-info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] Minikube / Kubernetes cluster is not yet reachable." -ForegroundColor Yellow
    Write-Host "Please ensure Docker Desktop is running and run 'minikube start' in another terminal." -ForegroundColor Yellow
} else {
    Write-Host " Kubernetes Cluster Connected!" -ForegroundColor Green
}

$IMAGE_NAME = "971023774760.dkr.ecr.ap-south-1.amazonaws.com/image-regi:latest"

function Deploy-To-Kubernetes {
    param([string]$CommitMsg)

    Write-Host "`n------------------------------------------------------------" -ForegroundColor Cyan
    Write-Host "🔔 [TRIGGER] GitHub Change Detected! Starting CI/CD Pipeline..." -ForegroundColor Yellow
    Write-Host "Commit MMessage: $CommitMsg" -ForegroundColor Gray
    Write-Host "------------------------------------------------------------" -ForegroundColor Cyan

    # Step 1: Run Automated Tests
    Write-Host "▶ Stage 1: Running Automated Tests..." -ForegroundColor Cyan
    python test_app.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Unit tests failed! Deployment aborted." -ForegroundColor Red
        return
    }
    Write-Host " Unit tests passed!" -ForegroundColor Green

    # Step 2: Build Docker Image
    Write-Host "▶ Stage 2: Building Docker Image ($IMAGE_NAME)..." -ForegroundColor Cyan
    docker build -t $IMAGE_NAME -t "studentapp:latest" .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker build failed!" -ForegroundColor Red
        return
    }
    Write-Host " Docker image built successfully!" -ForegroundColor Green

    # Step 3: Load Image into Minikube
    Write-Host "▶ Stage 3: Loading Docker Image into Minikube..." -ForegroundColor Cyan
    minikube image load $IMAGE_NAME
    minikube image load "studentapp:latest"
    Write-Host " Image loaded into Minikube cache!" -ForegroundColor Green

    # Step 4: Deploy & Rolling Update to Kubernetes
    Write-Host "▶ Stage 4: Applying Kubernetes Manifests & Triggering Rollout..." -ForegroundColor Cyan
    kubectl apply -f deployment.yaml
    kubectl apply -f service.yaml
    kubectl rollout restart deployment/studentapp-deployment
    kubectl rollout status deployment/studentapp-deployment --timeout=60s

    Write-Host "`n============================================================" -ForegroundColor Green
    Write-Host "✨ DEPLOYMENT COMPLETE! New version is LIVE on Kubernetes!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    kubectl get pods -l app=studentapp
    Write-Host ""
}

# Main polling loop
$lastCommit = git rev-parse HEAD

Write-Host "`n👀 Polling GitHub every 5 seconds for incoming commits... Press Ctrl+C to stop." -ForegroundColor White

while ($true) {
    try {
        git fetch origin main --quiet
        $remoteCommit = git rev-parse origin/main

        if ($remoteCommit -ne $lastCommit) {
            Write-Host "`n[NEW COMMIT DETECTED ON GITHUB]" -ForegroundColor Magenta
            git pull origin main --quiet
            $commitDetails = git log -1 --pretty=format:"%s (%an)"
            $lastCommit = $remoteCommit
            Deploy-To-Kubernetes -CommitMsg $commitDetails
        }
    } catch {
        # Ignore intermittent network glitches during poll
    }
    Start-Sleep -Seconds 5
}
