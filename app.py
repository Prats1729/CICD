import os
import sys
import socket
import platform
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Start timestamp for tracking uptime
START_TIME = datetime.now(timezone.utc)
REQUEST_COUNT = 0

# In-memory storage for interactive demo tasks
TASKS = [
    {"id": 1, "title": "Initialize Flask Application", "completed": True},
    {"id": 2, "title": "Build Docker Container Image", "completed": True},
    {"id": 3, "title": "Deploy on Kubernetes Cluster (Minikube)", "completed": False},
    {"id": 4, "title": "Scale Deployment to 4 Pod Replicas", "completed": False},
]

def get_system_info():
    """Retrieve runtime and pod/container environment details."""
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    # In Kubernetes, socket.gethostname() returns the Pod's name!
    hostname = socket.gethostname()
    
    try:
        host_ip = socket.gethostbyname(hostname)
    except Exception:
        host_ip = "127.0.0.1"

    uptime_delta = datetime.now(timezone.utc) - START_TIME
    uptime_str = f"{int(uptime_delta.total_seconds() // 60)}m {int(uptime_delta.total_seconds() % 60)}s"

    return {
        "hostname": hostname,
        "host_ip": host_ip,
        "os_name": f"{platform.system()} {platform.release()}",
        "python_version": platform.python_version(),
        "uptime": uptime_str,
        "current_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_count": REQUEST_COUNT,
        "app_version": os.getenv("APP_VERSION", "v1.0.0"),
        "environment": os.getenv("APP_ENV", "Kubernetes Production")
    }

@app.route("/")
def index():
    """Render the modern CloudOps Pulse monitoring dashboard."""
    info = get_system_info()
    return render_template("index.html", info=info, tasks=TASKS)

@app.route("/api/health")
def health_check():
    """Kubernetes liveness and readiness probe endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "CloudOps Pulse",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pod_name": socket.gethostname(),
        "uptime": str(datetime.now(timezone.utc) - START_TIME)
    }), 200

@app.route("/api/info")
def api_info():
    """System information JSON API."""
    return jsonify(get_system_info()), 200

@app.route("/api/tasks", methods=["POST"])
def add_task():
    """Add a new task interactively to demonstrate state/interactivity."""
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "Task title is required"}), 400

    new_task = {
        "id": len(TASKS) + 1,
        "title": title,
        "completed": False
    }
    TASKS.append(new_task)
    return jsonify({"success": True, "task": new_task}), 201

@app.route("/api/tasks/<int:task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    """Toggle completion status of a task."""
    for task in TASKS:
        if task["id"] == task_id:
            task["completed"] = not task["completed"]
            return jsonify({"success": True, "task": task})
    return jsonify({"error": "Task not found"}), 404

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    # Exposing on 0.0.0.0 is crucial for Docker & Kubernetes container routing
    app.run(host="0.0.0.0", port=port, debug=False)
