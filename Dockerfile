# Use a Python base image
FROM python:3.9

# Copy the run.sh file to the Docker container
COPY run.sh /app/run.sh

# Set the working directory
WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Make the run.sh file executable
RUN chmod +x run.sh

# Execute the run.sh script when the container starts
CMD ["/bin/bash", "run.sh"]
