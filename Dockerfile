# Stage 1: The Build Stage
# We'll use a full Python image to install dependencies
FROM python:3.12 AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# ----------------------------------------------

# Stage 2: The Final (Runtime) Stage
# We use a slim base image for a smaller final image size
FROM python:3.12-slim

WORKDIR /app

# Install FFmpeg and its dependencies
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 && \
    rm -rf /var/lib/apt/lists/*

# Copy the installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12

# Copy the application code from the local machine into the container
COPY . .

EXPOSE 5000

ENTRYPOINT ["python"]

CMD ["main.py"]