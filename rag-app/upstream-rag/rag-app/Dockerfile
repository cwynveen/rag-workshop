# Use the Chainguard Python base image (with dev tools)
FROM python:latest

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY main.py .

# Expose FastAPI port
EXPOSE 8000

# Launch via uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
