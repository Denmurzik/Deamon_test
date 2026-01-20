FROM python:3.10-slim

WORKDIR /app

COPY src /app/src

RUN pip install --no-cache-dir requests pydantic pyyaml

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Измените последнюю строку в Dockerfile
ENTRYPOINT ["python", "-m", "src.runner"]
