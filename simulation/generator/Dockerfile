FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    freetds-dev \
    freetds-bin \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pymssql

COPY generate.py .

CMD ["python", "-u", "generate.py"]
