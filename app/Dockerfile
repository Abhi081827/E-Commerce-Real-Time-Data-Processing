FROM python:3.9-slim

WORKDIR /app

# Copy the shared requirements file from the project root
COPY ../requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Copy FastAPI app code
COPY app.py /app/app.py

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
