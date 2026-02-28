FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY .env.example .env.example

# Create output directory
RUN mkdir -p reports

# Default command
CMD ["python", "-m", "src.main", "--query", "hospital readmissions heart failure", "--outdir", "reports"]
