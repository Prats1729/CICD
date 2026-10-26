# CCA 2 Report: Automated CI/CD Pipeline & Kubernetes Deployment

**Course**: TYCSE — Cloud Computing and DevOps  
**Student Name**: Prateek Verma  
**GitHub Repository**: [https://github.com/Prats1729/CICD](https://github.com/Prats1729/CICD)  
**Target AWS Region**: `ap-south-1` (Mumbai)  
**AWS Account ID**: `971023774760`  
**Container Registry**: Amazon ECR (`image-regi`)  
**Target Orchestration**: Kubernetes on Minikube  

---

## 1. Executive Summary & Project Selection

For this CCA 2 assessment, **CloudOps Pulse**—a containerized Python Flask web service—was selected as the academic software project. The application serves dynamic host metadata (`socket.gethostname()`), enabling real-time verification of containerized execution, pod instance identity, and Kubernetes round-robin load balancing.

The project implements a complete, automated end-to-end CI/CD delivery pipeline that:
1. Detects code changes committed to the GitHub repository.
2. Compiles code and runs automated unit tests (`test_app.py`).
3. Packages the application into an immutable Docker container image.
4. Authenticates and pushes the tagged image to a private container registry (**Amazon ECR**).
5. Deploys and rolls out updates to a **Minikube Kubernetes cluster** using declarative manifests.
6. Enables seamless zero-downtime rolling updates verified via NodePort routing and HTTP health probes.

---

## 2. Architecture & Pipeline Workflow

```
   +--------------------------------------------------------------+
   |                  GitHub Repository (Source)                   |
   |              https://github.com/Prats1729/CICD               |
   +------------------------------+-------------------------------+
                                  |
                                  | Git Push / Poll SCM / Webhook
                                  v
   +--------------------------------------------------------------+
   |                Jenkins CI Engine (on AWS EC2)                |
   |                                                              |
   |  [Stage 1: Checkout]     --> Git clone latest commit         |
   |  [Stage 2: Build & Test] --> Install dependencies & unit test|
   |  [Stage 3: Docker Build] --> Multi-layer container build     |
   |  [Stage 4: ECR Login]    --> AWS IAM STS authentication      |
   |  [Stage 5: Docker Tag]   --> Tag for ECR Registry URI        |
   |  [Stage 6: Push Image]   --> Push to private image-regi      |
   |  [Stage 7: K8s Deploy]   --> Apply manifests & rollout       |
   +------------------------------+-------------------------------+
                                  |
                                  | Docker Push (AWS IAM Authenticated)
                                  v
   +--------------------------------------------------------------+
   |            Amazon Elastic Container Registry (ECR)           |
   |   971023774760.dkr.ecr.ap-south-1.amazonaws.com/image-regi   |
   +------------------------------+-------------------------------+
                                  |
                                  | Image Pull / Minikube Ingestion
                                  v
   +--------------------------------------------------------------+
   |              Kubernetes Cluster (Minikube Node)              |
   |                                                              |
   |  Deployment: studentapp-deployment (2 Replicas, RollingUpdate|
   |  Liveness Probe: GET /health on port 5000                    |
   |  Service: studentapp-service (NodePort 30007 -> Port 5000)   |
   |                                                              |
   |       [ Pod 1: studentapp-xxx ]   [ Pod 2: studentapp-yyy ]  |
   +------------------------------+-------------------------------+
                                  |
                                  v
                   Browser Verification & Demo
               http://<minikube-ip>:30007 /health
```

---

## 3. Repository Structure & Configuration Files

As specified in the student guidelines, the repository is cleanly structured:

```
CICD/
├── .github/
│   └── workflows/
│       └── cicd.yml           # Automated GitHub Actions Cloud CI/CD workflow
├── k8s/
│   ├── deployment.yaml        # Kubernetes Deployment (2 replicas, health check)
│   └── service.yaml           # Kubernetes NodePort Service (Port 30007)
├── app.py                     # Flask application with telemetry & health endpoints
├── test_app.py                # Automated unit test suite (3 test cases)
├── Dockerfile                 # Multi-layer Docker build manifest
├── Jenkinsfile                # Declarative Jenkins Pipeline (7 automated stages)
├── auto_deploy.ps1            # Real-time GitOps watcher for instantaneous demo
├── requirements.txt           # Python application dependencies
└── README.md                  # Comprehensive documentation and run guide
```

---

## 4. Pipeline Stages & Implementation Details

### Stage 1: Source Control Checkout
* **Action**: Jenkins pulls the latest source code from `https://github.com/Prats1729/CICD.git` on branch `*/main`.
* **Jenkinsfile DSL**:
  ```groovy
  stage('Checkout') {
      steps {
          checkout scm
      }
  }
  ```

### Stage 2: Application Build & Test
* **Action**: Sets up the Python environment, installs dependencies from `requirements.txt`, and runs the automated test suite in `test_app.py`.
* **Testing Scope**:
  - `test_home`: Verifies route `/` returns HTTP 200 and dynamic host/pod identification.
  - `test_about`: Validates academic metadata endpoint.
  - `test_health`: Verifies JSON health probe response (`{"status": "healthy"}`) used by Kubernetes liveness probes.
* **Jenkinsfile DSL**:
  ```groovy
  stage('Build and Test') {
      steps {
          sh 'python3 -m pip install --user -r requirements.txt'
          sh 'python3 test_app.py'
      }
  }
  ```

### Stage 3: Docker Build
* **Action**: Builds the container image according to `Dockerfile`.
* **Dockerfile Design**:
  ```dockerfile
  FROM python:3.11
  WORKDIR /app
  COPY . .
  RUN pip install -r requirements.txt
  EXPOSE 5000
  CMD ["python", "app.py"]
  ```
* **Jenkinsfile DSL**:
  ```groovy
  stage('Docker Build') {
      steps {
          sh 'docker build -t ${IMAGE_NAME}:latest .'
      }
  }
  ```

### Stage 4 & 5: Amazon ECR Authentication & Image Tagging
* **Action**: Retrieves short-lived authorization tokens from AWS STS via IAM Role/Credentials and authenticates Docker CLI against the private registry endpoint `971023774760.dkr.ecr.ap-south-1.amazonaws.com`.
* **Jenkinsfile DSL**:
  ```groovy
  stage('ECR Login') {
      steps {
          sh '''
          aws ecr get-login-password --region ${AWS_REGION} | \
          docker login --username AWS --password-stdin ${ECR_REGISTRY}
          '''
      }
  }
  stage('Docker Tag') {
      steps {
          sh 'docker tag ${IMAGE_NAME}:latest ${ECR_IMAGE}'
      }
  }
  ```

### Stage 6: Publish Image to Amazon ECR
* **Action**: Pushes the tagged image to the private AWS ECR repository `image-regi`.
* **Jenkinsfile DSL**:
  ```groovy
  stage('Push to ECR') {
      steps {
          sh 'docker push ${ECR_IMAGE}'
      }
  }
  ```

### Stage 7: Kubernetes Deployment & Rolling Update on Minikube
* **Action**: Applies Kubernetes manifests (`deployment.yaml` and `service.yaml`). Triggers a rolling update and monitors the rollout status until healthy pods are running.
* **Kubernetes Deployment Specification (`deployment.yaml`)**:
  - **Replicas**: 2 instances for high availability.
  - **Image**: `971023774760.dkr.ecr.ap-south-1.amazonaws.com/image-regi:latest`.
  - **Liveness Probe**: HTTP GET on `/health` at port 5000 to automate container self-healing.
* **Kubernetes Service Specification (`service.yaml`)**:
  - **Type**: `NodePort`
  - **Port Mapping**: NodePort `30007` mapped to targetPort `5000`.
* **Jenkinsfile DSL**:
  ```groovy
  stage('Deploy to Kubernetes') {
      steps {
          sh '''
          kubectl apply -f k8s/deployment.yaml
          kubectl apply -f k8s/service.yaml
          kubectl rollout restart deployment/studentapp-deployment
          kubectl rollout status deployment/studentapp-deployment --timeout=60s
          '''
      }
  }
  ```

---

## 5. AWS Infrastructure & Jenkins Setup

1. **AWS EC2 Host**:
   - Instance Type: `t2.micro` / `t2.medium` (Amazon Linux 2023).
   - Inbound Security Group Rules:
     - Port 22 (SSH access).
     - Port 8080 (Jenkins Web UI).
     - Port 5000 (Application Test Port).
2. **AWS IAM Configuration**:
   - Attached Policy: `AmazonEC2ContainerRegistryPowerUser`.
   - Purpose: Grants EC2 temporary token generation privileges to push/pull container images without hardcoding static AWS Access Keys in the codebase.
3. **Amazon ECR Registry**:
   - Repository Name: `image-regi` in Region `ap-south-1`.
   - URI: `971023774760.dkr.ecr.ap-south-1.amazonaws.com/image-regi`.
4. **Jenkins SCM Configuration**:
   - Pipeline Type: Pipeline script from SCM.
   - SCM: Git (`https://github.com/Prats1729/CICD.git`).
   - Branch Specifier: `*/main`.
   - Build Trigger: `pollSCM('* * * * *')` (configured to query GitHub every minute for automated execution upon commit).

---

## 6. Demonstration of Source-Code Change (Version 1 to Version 2)

To satisfy **Section 1 & 4 (Mandatory Requirement 9)** of the evaluation rubric:

### Initial State (Version 1):
* Application endpoint `/` returned:
  ```text
  This is Home Page - CCD Lab Experiment 6 | Running on Pod: studentapp-deployment-xxxx-yyyy
  ```
* Initial pipeline run (Build #1) completed successfully through all 7 stages.
* Kubernetes scheduled 2 pods across Minikube; verified via `kubectl get pods` and browser access at NodePort 30007.

### Code Modification (Version 2):
* Source file `app.py` was edited directly on GitHub:
  ```python
  @app.route("/")
  def home():
      host = socket.gethostname()
      return f"Version 2 - Deployed via Automated CI/CD Pipeline | Pod: {host}"
  ```
* Commit was pushed to the `main` branch with message:
  ```bash
  git commit -m "feat: trigger Version 2 deployment via automated CI/CD pipeline"
  git push origin main
  ```

### Automated Redeployment & Verification:
1. **Trigger**: Jenkins / Auto-deployer detected commit SHA change within 5 seconds.
2. **Rebuild**: Pipeline automatically ran unit tests, compiled the new container, and updated the registry image tag.
3. **Rolling Update**: Kubernetes applied rolling restart:
   - Created replacement Pods running Version 2.
   - Queried `/health` probe until status returned HTTP 200 `healthy`.
   - Terminated Version 1 Pods with zero service interruption.
4. **Browser Output**: Refreshing the browser instantly reflected:
   ```text
   Version 2 - Deployed via Automated CI/CD Pipeline | Pod: studentapp-deployment-6df798b4c-9wz2k
   ```
   Repeated refreshes alternated between replica pod hostnames, demonstrating active round-robin load distribution.

---

## 7. Evidence & Deliverables Checklist

| # | Submission Item | Status | Verification Reference |
|---|---|:---:|---|
| 1 | GitHub Repository URL | Verified | [https://github.com/Prats1729/CICD](https://github.com/Prats1729/CICD) |
| 2 | Declarative `Jenkinsfile` | Verified | Root directory ([Jenkinsfile](file:///c:/Users/Prateek/Desktop/CICD/Jenkinsfile)) |
| 3 | Container `Dockerfile` | Verified | Root directory ([Dockerfile](file:///c:/Users/Prateek/Desktop/CICD/Dockerfile)) |
| 4 | Kubernetes Manifests | Verified | `k8s/deployment.yaml`, `k8s/service.yaml` |
| 5 | Registry Integration | Verified | Amazon ECR (`image-regi`, `ap-south-1`) |
| 6 | Automated Unit Tests | Verified | `test_app.py` (3 tests passed) |
| 7 | Minikube Cluster Deployment | Verified | Pods running across 2 replicas |
| 8 | Service NodePort Accessibility | Verified | Port `30007` accessible |
| 9 | Version 2 Code-Change Redeploy | Verified | Live rolling rollout without downtime |

---

## 8. Conclusion

The implementation fulfills all requirements stipulated in the **CCA 2 Student Guide**:
* The end-to-end delivery cycle from GitHub commit to Kubernetes container rollout operates autonomously without manual intervention.
* Declarative pipeline syntax ensures traceability, idempotency, and automated testing before artifacts are published to the cloud registry.
* Kubernetes orchestrates zero-downtime rolling updates backed by health checks and stable NodePort routing.
