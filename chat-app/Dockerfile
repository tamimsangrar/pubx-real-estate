FROM python:3.10-slim-buster

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY chat.py .

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "chat:app", "--host", "0.0.0.0", "--port", "8080"] 