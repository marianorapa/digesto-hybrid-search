# Use the official Debian image as the base
FROM debian:bookworm-slim

# Update package index and install dependencies
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    openjdk-17-jdk \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install Python dependencies with --break-system-packages flag
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copy the entire project into the container
COPY . .

# Set the default command to run main.py
CMD ["python3", "main.py"]
