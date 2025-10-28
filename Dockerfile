FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir flask grpcio grpcio-tools redis

# Optional: improve reliability for Render
ENV PYTHONUNBUFFERED=1

EXPOSE 8080
EXPOSE 50051

CMD ["python", "server.py"]
