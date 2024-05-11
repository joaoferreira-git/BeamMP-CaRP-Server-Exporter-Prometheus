# Use Python base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /var/log/beammp


# Copy script files
COPY script.py .

# Expose port
EXPOSE 9584

# Command to run the script
CMD ["python", "script.py"]
