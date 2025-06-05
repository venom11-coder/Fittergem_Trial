FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy code
COPY . .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (Flask default)
EXPOSE 5000

# Start app
CMD ["python", "deepface_Backend_Integration.py"]
