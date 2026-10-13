# CSE20120 — Cloud Computing & DevOps Laboratory
## Experiment 5: CI/CD Pipeline Using Jenkins, Docker and Amazon ECR

---

## 📑 Table of Contents
1. [Overview & Architecture](#1-overview--architecture)
2. [Deliverables: 9 Required Screenshots Checklist](#2-deliverables-9-required-screenshots-checklist)
3. [Step-by-Step Execution Guide](#3-step-by-step-execution-guide)
   - [Phase 1: Local Application & Git Setup (Steps 1–3)](#phase-1-local-application--git-setup)
   - [Phase 2: AWS Setup — EC2, IAM Role & ECR (Steps 4, 7, 8)](#phase-2-aws-setup--ec2-iam-role--ecr)
   - [Phase 3: Jenkins Installation & Configuration (Steps 5, 6, 9)](#phase-3-jenkins-installation--configuration)
   - [Phase 4: Jenkins Pipeline Configuration (Steps 10–12)](#phase-4-jenkins-pipeline-configuration)
   - [Phase 5: Pipeline Run & Image Verification (Steps 13–15)](#phase-5-pipeline-run--image-verification)
   - [Phase 6: Trigger Code Update — Version 2 (Step 16)](#phase-6-trigger-code-update--version-2)
4. [Complete Viva Questions & Model Answers (Q14–Q23)](#4-complete-viva-questions--model-answers)
5. [Troubleshooting & Pro Tips](#5-troubleshooting--pro-tips)

---

## 1. Overview & Architecture

In this experiment, you build an automated end-to-end Continuous Integration / Continuous Deployment (CI/CD) pipeline:

```
Developer (Code Push)
        │
        ▼
GitHub Repository (Prats1729/CICD)
        │
        ▼
Jenkins on AWS EC2
        ├── Stage 1: Checkout SCM
        ├── Stage 2: Build & Test (Python compile/test)
        ├── Stage 3: Docker Build (cloud-image:latest)
        ├── Stage 4: ECR Login (aws ecr get-login-password via IAM Role)
        ├── Stage 5: Docker Tag (tag to ECR registry URI)
        └── Stage 6: Docker Push (push to AWS ECR)
        │
        ▼
Amazon ECR (Private Registry: image-regi)
        │
        ▼
Used by Kubernetes (Experiment 6 Minikube Deployment)
```

---

## 2. Deliverables: 9 Required Screenshots Checklist

Match these exactly against **Page 7** of the Experiment 5 Lab Manual:

| # | Lab Sheet Item | What to Capture | Source / Command / URL |
| :-: | :--- | :--- | :--- |
| **5** | **GitHub Repository** | GitHub repo webpage showing `app.py`, `Dockerfile`, `Jenkinsfile`, and `requirements.txt` | `https://github.com/Prats1729/CICD` |
| **6** | **Flask Application** | VS Code / Editor showing `app.py` code (or browser running at `http://localhost:5000`) | Open `app.py` |
| **7** | **Dockerfile** | VS Code / Editor showing `Dockerfile` content | Open `Dockerfile` |
| **8** | **Jenkins Dashboard** | Browser window showing Jenkins Dashboard with welcome screen or pipeline list | `http://<EC2-PUBLIC-IP>:8080` |
| **9** | **Jenkins Pipeline Configuration** | Jenkins job configuration page showing SCM settings (Git repo URL, credentials ID, branch `*/main`, Script Path `Jenkinsfile`) | Job: `ccd-pipeline` ➔ Configure |
| **10** | **Successful Pipeline Build / Console Output** | Jenkins Stage View with all green boxes + Console output showing `Finished: SUCCESS` | Build #1 ➔ Console Output / Pipeline Overview |
| **11** | **Docker Image** | Terminal on EC2 showing output of `docker images` with `cloud-image` and ECR-tagged image | EC2 Terminal: `docker images` |
| **12** | **Amazon ECR Repository showing image** | AWS Web Console showing the `image-regi` repository with an image tag `latest` and Image URI | AWS Console ➔ ECR ➔ `image-regi` |
| **13** | **Updated GitHub Version & Subsequent Build** | (a) GitHub commit showing "Version 2" AND (b) Jenkins Build #2 Stage View completed successfully | GitHub commit diff + Jenkins Build #2 Console |

---

## 3. Step-by-Step Execution Guide

### Phase 1: Local Application & Git Setup

#### Step 1: Verify the Flask Application
Ensure `app.py` exists in your project root:
```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello from Jenkins CI/CD Pipeline!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```
Ensure `requirements.txt`:
```txt
Flask
```

#### Step 2: Verify the Dockerfile
Ensure `Dockerfile` exists in your project root:
```dockerfile
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
```

#### Step 3: Push to GitHub
Your repository is already initialized to `https://github.com/Prats1729/CICD.git`.
Verify branch and status:
```bash
git status
git add .
git commit -m "Initial application for Experiment 5"
git push origin main
```
> 📸 **Screenshot 5:** Capture your GitHub repository web page showing your files.
> 📸 **Screenshot 6 & 7:** Capture `app.py` and `Dockerfile` in your editor.

---

### Phase 2: AWS Setup — EC2, IAM Role & ECR

#### Step 4: AWS EC2 Instance Launch & Security Group
1. Launch an EC2 instance:
   - **OS**: Amazon Linux 2023 (AL2023) or Amazon Linux 2 (AL2).
   - **Instance Type**: `t2.micro` (100% AWS Free Tier eligible).
2. **Security Group Rules (Inbound)**:
   - **SSH**: Port `22` (Source: My IP or 0.0.0.0/0).
   - **Custom TCP**: Port `8080` (Jenkins web UI, Source: `0.0.0.0/0`).
   - **Custom TCP**: Port `5000` (Flask application test port, Source: `0.0.0.0/0`).

#### Step 7: Create the Amazon ECR Private Repository
1. In AWS Management Console, search for **ECR (Elastic Container Registry)**.
2. Select **Private repositories** ➔ Click **Create repository**.
3. **Repository name**: `image-regi`.
4. **AWS Region**: `ap-south-1` (Asia Pacific - Mumbai).
5. Leave all other settings as default ➔ Click **Create repository**.
6. Note your **AWS Account ID** (e.g. `164607045936`).

#### Step 8: Configure EC2 IAM Role for ECR Access
To allow Jenkins running on EC2 to authenticate with ECR without embedding hardcoded AWS access keys:
1. Open **IAM Console** ➔ **Roles** ➔ **Create role**.
2. **Trusted entity type**: `AWS service` ➔ Use case: `EC2` ➔ Next.
3. Attach Policy: `AmazonEC2ContainerRegistryPowerUser` (or `AmazonEC2ContainerRegistryFullAccess`).
4. **Role name**: `EC2-ECR-Jenkins-Role` ➔ Click **Create role**.
5. Attach the role to your EC2 instance:
   - Go to **EC2 Console** ➔ Select your running instance.
   - Click **Actions** ➔ **Security** ➔ **Modify IAM role**.
   - Select `EC2-ECR-Jenkins-Role` ➔ Click **Update IAM role**.
6. Verify identity inside your EC2 terminal:
   ```bash
   aws sts get-caller-identity
   aws ecr describe-repositories --repository-names image-regi --region ap-south-1
   ```

---

### Phase 3: Jenkins Installation & Configuration

#### Step 5 & 6: Install & Start Jenkins and Docker on EC2
SSH into your EC2 instance (`ssh -i your-key.pem ec2-user@<EC2-PUBLIC-IP>`):

**For Amazon Linux 2023 (AL2023) / Amazon Linux 2 (AL2) on `t2.micro`:**
```bash
# 1. CRITICAL for t2.micro: Create 2GB Swap Memory (Prevents Jenkins/JVM crash/freeze)
sudo dd if=/dev/zero of=/swapfile bs=128M count=16
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile swap swap defaults 0 0' | sudo tee -a /etc/fstab

# 2. Update packages and install Java 17 Corretto, Git, Python3, and Docker
sudo dnf update -y
sudo dnf install -y java-17-amazon-corretto git python3 python3-pip docker wget

# (Note: If using older Amazon Linux 2, use 'sudo yum' instead of 'sudo dnf' and 'sudo amazon-linux-extras install docker java-openjdk11 -y')

# 3. Add Jenkins Official RedHat/Amazon Linux Repository and Install Jenkins
sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key
sudo dnf upgrade -y
sudo dnf install -y jenkins

# 4. Start Docker and Jenkins services
sudo systemctl enable --now docker
sudo systemctl enable --now jenkins

# 5. Give Jenkins user (and ec2-user) permission to use Docker
sudo usermod -aG docker jenkins
sudo usermod -aG docker ec2-user
sudo systemctl restart jenkins

# 6. Verify versions (AWS CLI is already pre-installed on Amazon Linux)
python3 --version
git --version
docker --version
java -version
aws --version
sudo systemctl status jenkins --no-pager
```

*(Note: If you ever use Ubuntu instead, use `sudo apt-get update -y && sudo apt-get install -y openjdk-17-jdk docker.io`)*

#### Step 5 (Continued): Unlock Jenkins
Retrieve the initial administrator password:
```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```
1. In your browser, open: `http://<EC2-PUBLIC-IP>:8080`
2. Paste the password from the terminal.
3. Click **Install suggested plugins**.
4. Create your Admin user (e.g., `admin` / your password).
5. Confirm Jenkins URL ➔ Save and Finish.
> 📸 **Screenshot 8:** Capture the Jenkins Dashboard home page.

#### Step 9: Configure GitHub Credentials in Jenkins
1. Go to **Jenkins Dashboard** ➔ **Manage Jenkins** ➔ **Credentials**.
2. Click **(global)** under System ➔ Click **Add Credentials**.
3. Fill in:
   - **Kind**: `Username with password`
   - **Scope**: `Global`
   - **Username**: Your GitHub username (e.g. `Prats1729`)
   - **Password**: Your GitHub Personal Access Token (PAT) with `repo` permissions
   - **ID**: `github-credentials`
   - **Description**: `GitHub Access Token`
4. Click **Create**.

---

### Phase 4: Jenkins Pipeline Configuration

#### Step 10 & 11: Verify and Push Jenkinsfile
Your `Jenkinsfile` in the repository root:
```groovy
pipeline {
    agent any

    environment {
        AWS_REGION     = 'ap-south-1'
        AWS_ACCOUNT_ID = '164607045936'  // Replace with your 12-digit AWS Account ID
        ECR_REPOSITORY = 'image-regi'
        IMAGE_NAME     = 'cloud-image'
        ECR_REGISTRY   = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        ECR_IMAGE      = "${ECR_REGISTRY}/${ECR_REPOSITORY}:latest"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build and Test') {
            steps {
                sh 'python3 -m pip install --user -r requirements.txt'
                sh 'python3 -m py_compile app.py'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t ${IMAGE_NAME}:latest .'
            }
        }

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

        stage('Push to ECR') {
            steps {
                sh 'docker push ${ECR_IMAGE}'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
```
Commit and push this file:
```bash
git add Jenkinsfile
git commit -m "Add Jenkins pipeline"
git push origin main
```

#### Step 12: Create Pipeline Job in Jenkins
1. Jenkins Dashboard ➔ **New Item**.
2. Enter item name: `ccd-pipeline`.
3. Select **Pipeline** ➔ Click **OK**.
4. Scroll down to the **Pipeline** section:
   - **Definition**: `Pipeline script from SCM`
   - **SCM**: `Git`
   - **Repository URL**: `https://github.com/Prats1729/CICD.git`
   - **Credentials**: Select `github-credentials`
   - **Branch Specifier**: `*/main`
   - **Script Path**: `Jenkinsfile`
5. Click **Save**.
> 📸 **Screenshot 9:** Capture this Jenkins Pipeline Configuration page showing the SCM settings.

---

### Phase 5: Pipeline Run & Image Verification

#### Step 13: Run the Pipeline
1. In the `ccd-pipeline` project page, click **Build Now** on the left menu.
2. Watch Build `#1` execute.
3. Click on `#1` ➔ **Console Output**.
4. Verify all 6 stages finish green:
   - `Checkout` ➔ `Build and Test` ➔ `Docker Build` ➔ `ECR Login` ➔ `Docker Tag` ➔ `Push to ECR`.
   - Bottom shows: `Finished: SUCCESS`.
> 📸 **Screenshot 10:** Capture the Pipeline Stage View (all green stages) and the bottom of Console Output (`Finished: SUCCESS`).

#### Step 14: Verify Docker Image Locally on EC2
On the EC2 terminal, run:
```bash
docker images
```
Look for:
- `cloud-image:latest`
- `164607045936.dkr.ecr.ap-south-1.amazonaws.com/image-regi:latest`
> 📸 **Screenshot 11:** Capture the terminal showing both images in `docker images`.

#### Step 15: Verify Image in Amazon ECR
Run via AWS CLI:
```bash
aws ecr list-images --repository-name image-regi --region ap-south-1
```
Or open the AWS Console:
- Go to **Amazon ECR** ➔ **Private Repositories** ➔ `image-regi`.
- You will see tag `latest` with its Image URI and pushed timestamp.
> 📸 **Screenshot 12:** Capture the AWS ECR Console page showing the pushed image tag `latest`.

---

### Phase 6: Trigger Code Update — Version 2

#### Step 16: Demonstrate a Code Change
1. Modify `app.py`:
   Change the returned string:
   ```python
   @app.route("/")
   def home():
       return "Version 2 - CI/CD Pipeline"
   ```
2. Commit and push the update to GitHub:
   ```bash
   git add app.py
   git commit -m "Version 2"
   git push origin main
   ```
3. In Jenkins, go to `ccd-pipeline` and click **Build Now**.
4. Build `#2` runs, automatically pulling the `Version 2` code, compiling it, rebuilding the Docker container, and pushing the new tag to ECR.
> 📸 **Screenshot 13:** Capture:
> - (a) The GitHub commit page showing the "Version 2" commit diff.
> - (b) The Jenkins Pipeline Dashboard showing Build `#2` completed with `Finished: SUCCESS`.

---

## 4. Complete Viva Questions & Model Answers

These are the exact 10 Viva questions from **Page 8** of the lab manual:

#### 14. What is Continuous Integration (CI)?
> **Answer**: Continuous Integration is a software development DevOps practice where developers frequently merge their code changes into a central shared repository (e.g., GitHub), after which automated builds and tests are immediately triggered to detect integration errors early.

#### 15. What is Continuous Deployment/Delivery (CD)?
> **Answer**:
> - **Continuous Delivery**: Automatically builds, tests, and prepares artifacts (like Docker images pushed to ECR) ready for production deployment at any time with manual approval.
> - **Continuous Deployment**: Every change that passes all stages of the production pipeline is released directly into production without manual intervention.

#### 16. What is Jenkins?
> **Answer**: Jenkins is a leading open-source automation server written in Java. It enables developers to automate the non-human parts of software development, such as building, testing, containerizing, and deploying applications through custom CI/CD pipelines.

#### 17. What is a Jenkinsfile?
> **Answer**: A Jenkinsfile is a text file written using Groovy-based Domain Specific Language (DSL) that defines the entire Jenkins Pipeline as code ("Pipeline as Code"). It is stored in the root of the source control repository alongside application code.

#### 18. What is the role of Docker in a CI/CD pipeline?
> **Answer**: Docker provides consistent, lightweight container packaging. It eliminates the "works on my machine" problem by ensuring that dependencies, system libraries, and runtime configurations are identical across development, test, CI server, and production Kubernetes clusters.

#### 19. Why is Amazon ECR used in this experiment?
> **Answer**: Amazon Elastic Container Registry (ECR) is a fully managed, secure, scalable AWS Docker container registry. It stores, manages, and distributes private Docker container images close to AWS compute services (EC2, ECS, EKS) with IAM access control and encryption.

#### 20. Why is an EC2 IAM role used for ECR access?
> **Answer**: An IAM role uses AWS Security Token Service (STS) to provide short-lived, automatically rotated credentials directly to the EC2 instance metadata. This avoids the severe security risk of hardcoding permanent AWS Access Keys and Secret Keys inside the Jenkinsfile or EC2 filesystem.

#### 21. Why is Docker tag required before pushing an image to ECR?
> **Answer**: Docker CLI determines the target remote registry and repository URL from the image name itself. Tagging the local image (`cloud-image:latest`) with the fully qualified ECR repository URI (`<account_id>.dkr.ecr.<region>.amazonaws.com/image-regi:latest`) tells Docker exactly which registry endpoint and repository to push to.

#### 22. What happens when a Jenkins pipeline fails?
> **Answer**: Execution immediately halts at the failing stage. The pipeline status is marked as `FAILED` (red), notifications (Slack/email) can be triggered via the `post { failure { ... } }` block, and the bad code is prevented from reaching production or being pushed to Amazon ECR.

#### 23. Why is Build Now used after a GitHub push in this experiment?
> **Answer**: Because no GitHub Webhook was configured between GitHub and the EC2 Jenkins instance (which typically requires a publicly accessible webhook URL or public IP without NAT restrictions), the build is triggered manually by clicking "Build Now".

---

## 5. Troubleshooting & Pro Tips

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| **`docker: permission denied`** | Jenkins user is not in the `docker` OS group | Run `sudo usermod -aG docker jenkins` followed by `sudo systemctl restart jenkins`. |
| **`ecr: RepositoryNotFoundException`** | Repository name or region mismatch | Ensure repository name in AWS is exactly `image-regi` and region is `ap-south-1`. |
| **`ECR Login fails / Not authorized`** | EC2 instance does not have IAM role attached | Attach `EC2-ECR-Jenkins-Role` to the EC2 instance via **Actions ➔ Security ➔ Modify IAM Role**. |
| **`Jenkinsfile not found`** | Branch is set to `*/master` instead of `*/main` | In Jenkins Pipeline configuration, change Branch Specifier from `*/master` to `*/main`. |
| **GitHub authentication fails** | Using GitHub password instead of PAT | GitHub requires a **Personal Access Token (classic)** with `repo` scope enabled. |
| **EC2 Out of Memory / Jenkins freezes** | `t2.micro` is too small | Use at least `t2.medium` (2 vCPU, 4GB RAM) for running Jenkins and Docker together. |
