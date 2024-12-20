# Use the official Debian image as the base
FROM ubuntu:24.04

# Update package index and install dependencies
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    openjdk-21-jdk \
    python-is-python3 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the entire project into the container
COPY . .

# Install Poetry
RUN pip install poetry --break-system-packages

RUN poetry install

# Set the default command to run main.py
CMD ["poetry", "run", "python3", "main.py"]
