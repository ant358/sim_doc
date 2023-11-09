FROM python:3.11-slim-bullseye

# Set working directory
WORKDIR /app

# Copy source code 
COPY . /app

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt
