# Use Python base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app
RUN mkdir -p ./promtail/config
# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy script files
COPY script.py .
COPY config.yml ./promtail/config

# Expose port
EXPOSE 9584
EXPOSE 9080

# Command to run the script
CMD ["python", "script.py"]
