FROM python:3.9-slim

WORKDIR /app

# Copy the shared requirements file
COPY ../requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Copy dashboard code
COPY dashboard.py /app/dashboard.py

EXPOSE 8501

CMD ["streamlit", "run", "dashboard.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
