# Use a base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy dependency file into the image
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code into the image
COPY . .

# Expose the application port
EXPOSE 8000

# Command to run the application
CMD ["python", "app.py"]
