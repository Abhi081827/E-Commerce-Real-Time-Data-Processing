# dashboard/Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY ../requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY dashboard.py .
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
