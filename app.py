import socket
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    host = socket.gethostname()
    return f"This is Home Page - CCD Lab Experiment 6 version 2 | Running on Pod: {host}"

@app.route("/about")
def about():
    return "This is for CCD Lab (CSE20120): Containerization & Orchestration using Kubernetes."

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "pod": socket.gethostname()}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
