FROM cgr.dev/chainguard/python:latest-dev
WORKDIR /app
USER 0

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
RUN mkdir vectordb

EXPOSE 8000

# Because ENTRYPOINT is already /usr/bin/python,
# just hand it the -m uvicorn arguments directly:
CMD ["-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
