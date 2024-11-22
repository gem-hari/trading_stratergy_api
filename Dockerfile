# Use a base image
FROM 851725235990.dkr.ecr.ap-south-1.amazonaws.com/python-slim-11:3.11-slim
# FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy dependency file into the image
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code into the image
COPY . .

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
