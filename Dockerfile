# Use the official Python base image from Docker Hub
FROM python:3.9.13-slim

# Set the working directory inside the container
WORKDIR /sax4bpm

# Copy the Python script and requirements file into the container
# Copy the entire sax4bpm directory
COPY ./sax /sax4bpm/sax

# Copy requirements.txt separately
COPY ./requirements.txt /sax4bpm/requirements.txt

# Install required dependencies
RUN pip install --no-cache-dir -r /sax4bpm/requirements.txt
RUN pip uninstall -y psutil

# Expose the port for Flask 
EXPOSE 5000

# Run Streamlit application
CMD ["python", "-m", "sax.api.app"]
