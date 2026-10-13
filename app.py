import os
import socket
from datetime import datetime, timezone
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def home():
    """Home endpoint - displays simple web page with pod details."""
    hostname = socket.gethostname()
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>DevOps Flask App</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f6f9;
            margin: 0;
            padding: 40px;
        }}
        .card {{
            background: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: auto;
            padding: 30px;
        }}
        h1 {{ color: #2c3e50; font-size: 22px; margin-top: 0; }}
        .badge {{
            background: #e1f5fe;
            color: #0288d1;
            padding: 6px 12px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 15px;
            display: inline-block;
        }}
        ul {{ line-height: 1.8; }}
        a {{ color: #0288d1; text-decoration: none; font-weight: bold; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>Cloud & DevOps Lab Application</h1>
        <p><strong>Serving Pod / Host:</strong> <span class="badge">{hostname}</span></p>
        <p>This Flask application is containerized with Docker and running on Kubernetes.</p>
        <hr>
        <h3>Available Endpoints:</h3>
        <ul>
            <li><a href="/health">/health</a> &mdash; Health Check (Liveness Probe)</li>
            <li><a href="/info">/info</a> &mdash; System Information (JSON)</li>
            <li><a href="/api/greet?name=Evaluator">/api/greet?name=Evaluator</a> &mdash; Greeting API</li>
        </ul>
    </div>
</body>
</html>"""

@app.route("/health")
def health():
    """Health check endpoint for Kubernetes liveness probe."""
    return jsonify({
        "status": "healthy",
        "pod_name": socket.gethostname()
    }), 200

@app.route("/info")
def info():
    """System information endpoint returning JSON."""
    return jsonify({
        "hostname": socket.gethostname(),
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    }), 200

@app.route("/api/greet")
def greet():
    """Sample parameter endpoint."""
    name = request.args.get("name", "Student")
    return jsonify({
        "message": f"Hello, {name}!",
        "served_by_pod": socket.gethostname()
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
