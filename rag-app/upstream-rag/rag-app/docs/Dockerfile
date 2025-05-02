FROM python:3.11-slim

WORKDIR /app

# install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# bring in our service code
COPY main.py .
# note: docker_best_practices.md sits one level up in compose

# create persistence dir & mountpoint for user Dockerfiles
RUN mkdir vectordb
VOLUME ["/app/docs"]

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
