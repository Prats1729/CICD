# CSE20120 — Cloud Computing & DevOps Laboratory
## Experiment 6: Containerization and Orchestration Using Kubernetes

### Project Name: CloudOps Pulse (Python Flask + Docker + Kubernetes)

---

## 📑 Table of Contents
1. [Project Overview](#1-project-overview)
2. [Files in this Project](#2-files-in-this-project)
3. [Step-by-Step Lab Execution](#3-step-by-step-lab-execution)
4. [Screenshots Checklist (12 Lab Deliverables)](#4-screenshots-checklist-12-deliverables)
5. [Complete Viva Questions & Answers](#5-complete-viva-questions--answers)

---

## 1. Project Overview

Instead of a basic static text string, **CloudOps Pulse** is a purpose-built DevOps & Cloud telemetry dashboard. It demonstrates key container and orchestration concepts:
- **Active Pod Identification**: Displays the hostname dynamically (`socket.gethostname()`). In Kubernetes, this is the exact **Pod ID**, allowing you to demonstrate load balancing and round-robin routing across replicas when refreshing the page!
- **Container Telemetry**: Real-time Pod IP, Uptime, Request Counter, Python Runtime, and OS Platform.
- **Liveness & Health Probe Endpoints**: `/api/health` and `/api/info` used by Kubernetes for automated health monitoring.
- **Interactive Checklist**: A built-in task board to track lab steps interactively.

---

## 2. Files in this Project

| File | Purpose |
| :--- | :--- |
| `app.py` | Flask application server with health probes & telemetry |
| `templates/index.html` | Modern responsive dark-mode DevOps dashboard |
| `requirements.txt` | Python dependencies (`Flask==3.0.3`) |
| `Dockerfile` | Multi-layer container build based on `python:3.11-slim` |
| `deployment.yaml` | Kubernetes Deployment (2 replicas, resource limits, health check) |
| `service.yaml` | Kubernetes NodePort Service exposed on static port `30007` |
| `test_app.py` | Automated unit tests for CI/CD verification |
| `Jenkinsfile` | CI/CD pipeline definition for Amazon ECR (Experiment 5 link) |

---

## 3. Step-by-Step Lab Execution

### Phase 1: Local Application Verification (Optional Pre-check)
Run automated unit tests to verify the application code:
```bash
python test_app.py
```
*(Expected: `Ran 4 tests ... OK`)*

---

### Phase 2: Build & Test with Docker (Steps 4–6 of Lab Sheet)

#### 1. Build the Docker Image
```bash
docker build -t studentapp:v1 .
```
Verify the image was created:
```bash
docker images
```
*(Look for `studentapp` with tag `v1`)*

#### 2. Run the Container Locally
```bash
docker run -d -p 5000:5000 --name student-container studentapp:v1
```
Check running containers:
```bash
docker ps
```

#### 3. Test in Browser / Terminal
- Open browser at: `http://localhost:5000`
- Or curl via terminal:
  ```bash
  curl http://localhost:5000/api/info
  ```

#### 4. Stop and Remove the Local Container (Free port 5000)
```bash
docker stop student-container
docker rm student-container
```

---

### Phase 3: Deploy on Kubernetes with Minikube (Steps 7–9 of Lab Sheet)

#### 1. Start Minikube
```bash
minikube start
```
Verify cluster status:
```bash
minikube status
kubectl cluster-info
```

#### 2. Load the Docker Image into Minikube
Because Minikube has its own isolated Docker daemon, load the locally built image into the cluster:
```bash
minikube image load studentapp:v1
```
*(If your evaluator asks you to use Amazon ECR image from Experiment 5, update the `image:` line in `deployment.yaml` to `164607045936.dkr.ecr.ap-south-1.amazonaws.com/image-regi:latest`)*

#### 3. Deploy the Application (2 Replicas)
Apply the deployment manifest:
```bash
kubectl apply -f deployment.yaml
```
Verify the Deployment and Pods:
```bash
kubectl get deployments
kubectl get pods -o wide
```
*(You will see 2 pods running: `studentapp-deployment-xxxx-xxxx`)*

#### 4. Expose the Application via NodePort Service
Apply the service manifest:
```bash
kubectl apply -f service.yaml
```
Verify the service:
```bash
kubectl get svc studentapp-service
```
*(You will see type `NodePort`, Port `5000:30007/TCP`)*

---

### Phase 4: Access the Application via Kubernetes

In Minikube, access the NodePort service using:
```bash
minikube service studentapp-service
```
*Minikube will automatically open the URL in your default web browser.*

Alternatively, to get the direct URL:
```bash
minikube service studentapp-service --url
```

> **💡 Lab Demonstration Tip**:
> Refresh the page multiple times in your browser. Notice the **Active Pod Identifier** at the top of the dashboard changing between Pod 1 and Pod 2. This proves that the Kubernetes Service is distributing incoming traffic via load balancing!

---

### Phase 5: Scale the Deployment to 4 Replicas (Step 10 of Lab Sheet)

Scale the deployment up to 4 replicas:
```bash
kubectl scale deployment studentapp-deployment --replicas=4
```
Verify the newly created pods:
```bash
kubectl get pods
```
*(You will now see 4 active pods in `Running` state!)*

---

## 4. Screenshots Checklist (12 Deliverables)

Match these exactly to the **Screenshots to Attach** list on Page 6:

| # | Required Screenshot | What to Capture | Command / Screen |
| :--- | :--- | :--- | :--- |
| **1** | Flask Application | Code editor showing `app.py` | Open `app.py` in VS Code/editor |
| **2** | Dockerfile | Code editor showing `Dockerfile` | Open `Dockerfile` |
| **3** | Docker Image Creation | Terminal showing build completion & image list | `docker build -t studentapp:v1 .` and `docker images` |
| **4** | Running Docker Container | Terminal showing active container | `docker ps` |
| **5** | Amazon ECR Repository | AWS Console or terminal showing ECR image | AWS ECR Web Console or `aws ecr list-images` |
| **6** | Minikube Cluster | Terminal showing active cluster status | `minikube status` |
| **7** | Deployment YAML File | Terminal or editor displaying `deployment.yaml` | `cat deployment.yaml` |
| **8** | Service YAML File | Terminal or editor displaying `service.yaml` | `cat service.yaml` |
| **9** | Running Pods | Terminal showing initial 2 running pods | `kubectl get pods` |
| **10** | Running Services | Terminal showing NodePort 30007 service | `kubectl get svc` |
| **11** | Application Output in Browser | Web browser displaying CloudOps Pulse dashboard | `http://<minikube-ip>:30007` or `minikube service` |
| **12** | Scaled Deployment | Terminal showing 4 pods running after scale | `kubectl scale deployment studentapp-deployment --replicas=4` then `kubectl get pods` |

---

## 5. Complete Viva Questions & Answers

These are the exact 17 Viva questions from Page 6 of the lab manual:

#### 1. What is Containerization?
> **Answer**: Containerization is an OS-level virtualization method that packages an application together with its dependencies, configuration, and libraries into a single lightweight executable container, ensuring consistent execution across different computing environments.

#### 2. What is Docker?
> **Answer**: Docker is an open-source platform that enables developers to automate the deployment, scaling, and management of applications inside standardized lightweight software containers.

#### 3. What is a Docker Image?
> **Answer**: A Docker Image is an immutable, read-only template that contains the application source code, runtime, system libraries, and instructions needed to instantiate and run a container.

#### 4. What is a Docker Container?
> **Answer**: A Docker Container is a runnable, isolated instance of a Docker image. It has its own isolated filesystem, network stack, and process space provided by Linux kernel namespaces and cgroups.

#### 5. What is Amazon ECR?
> **Answer**: Amazon Elastic Container Registry (Amazon ECR) is a fully managed AWS container registry service that makes it easy to securely store, manage, share, and deploy Docker container images.

#### 6. What is Kubernetes?
> **Answer**: Kubernetes (K8s) is an open-source container orchestration platform that automates container deployment, scaling, load balancing, networking, and self-healing across clusters of host machines.

#### 7. What is a Kubernetes Pod?
> **Answer**: A Pod is the smallest deployable computing unit in Kubernetes. It represents a single instance of a running process in a cluster, encapsulating one or more tightly coupled containers that share storage, network IP, and port space.

#### 8. What is a Deployment in Kubernetes?
> **Answer**: A Deployment is a higher-level Kubernetes declarative controller that manages the lifecycle of Pods via ReplicaSets. It provides features like declarative pod updates, rolling rollouts, rollbacks, and self-healing.

#### 9. What is a Service in Kubernetes?
> **Answer**: A Service is an abstract Kubernetes resource that defines a logical set of Pods and a policy to access them. It provides a stable IP address and DNS name, decoupling front-end clients from the ephemeral, dynamic IP addresses of individual Pods.

#### 10. What is NodePort?
> **Answer**: NodePort is a type of Kubernetes Service that exposes the service on an open port on every node's IP address (in the default range 30000–32767). It allows external traffic outside the cluster to access internal pods via `<NodeIP>:<NodePort>`. In our experiment, we used NodePort `30007`.

#### 11. What is Minikube?
> **Answer**: Minikube is a lightweight, local Kubernetes implementation that runs a single-node cluster inside a VM or container on a local development machine, allowing developers to test and develop Kubernetes applications locally without cloud infrastructure.

#### 12. Why is Kubernetes used?
> **Answer**: As microservice applications grow, manually managing dozens or hundreds of containers is impossible. Kubernetes automates:
> - High availability and self-healing (restarting crashed containers)
> - Dynamic horizontal autoscaling
> - Automated rollouts and rollbacks
> - Built-in service discovery and load balancing
> - Resource allocation and secret management.

#### 13. What is scaling in Kubernetes?
> **Answer**: Scaling refers to adjusting the number of running instances (Pods) of an application. Horizontal scaling increases or decreases the number of Pod replicas (e.g., using `kubectl scale --replicas=4` or the Horizontal Pod Autoscaler - HPA) to meet changing traffic demands.

#### 14. What is the difference between a Pod and a Container?
> **Answer**: A Container is a single isolated process created from a container image. A Pod is a Kubernetes abstraction that wraps around one or more containers, providing a shared network namespace (shared IP and localhost) and shared storage volumes.

#### 15. What are the advantages of Kubernetes?
> **Answer**:
> 1. Multi-cloud and hybrid portability (no vendor lock-in).
> 2. Automated self-healing (replaces failed containers automatically).
> 3. Zero-downtime rolling deployments and automated rollbacks.
> 4. Efficient compute hardware utilization.
> 5. Built-in ingress, load balancing, and storage orchestration.

#### 16. Why is Amazon ECR used instead of Docker Hub in this experiment?
> **Answer**: Amazon ECR integrates natively with AWS Identity and Access Management (IAM), allowing secure EC2 instance authentication without hardcoding Docker Hub credentials. It also provides lower latency and higher transfer speeds within AWS VPCs.

#### 17. How does Jenkins from Experiment 5 provide the Docker image used by Kubernetes?
> **Answer**: Jenkins automates the CI pipeline: it checks out source code from GitHub, executes automated tests, builds the Docker image, tags it with the ECR repository URI, logs into ECR using AWS IAM credentials, and pushes the image to Amazon ECR. Kubernetes in Experiment 6 then pulls that tagged image (`...amazonaws.com/image-regi:latest`) to run the pods.
