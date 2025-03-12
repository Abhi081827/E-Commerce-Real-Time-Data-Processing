# data-simulator/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy the shared requirements file from the project root
COPY ../requirements.txt /app/requirements.txt

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Copy the Data Simulator code into the container
COPY data_simulator.py /app/data_simulator.py

# Run the Data Simulator script
CMD ["python", "data_simulator.py"]
