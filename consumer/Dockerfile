FROM python:3.9-slim

WORKDIR /app

# Copy the shared requirements file
COPY ../requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Copy consumer code
COPY consumer.py /app/consumer.py

CMD ["python", "consumer.py"]
