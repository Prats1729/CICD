FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for Docker layer caching
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and templates
COPY . .

# Expose port 5000 for the Flask application
EXPOSE 5000

ENV PYTHONUNBUFFERED=1

CMD ["python", "app.py"]
