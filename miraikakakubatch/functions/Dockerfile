FROM python:3.9.18-slim-bullseye

WORKDIR /app

# Use older Debian (Bullseye) to avoid Trixie Python 3.13 conflicts
RUN apt-get update && apt-get install -y \
    gcc=4:10.2.1-1 \
    python3-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Pin exact versions to avoid conflicts
RUN pip3 install --no-cache-dir \
    pymysql==1.0.2 \
    numpy==1.24.3 \
    yfinance==0.2.18 \
    pandas==2.0.3 \
    requests==2.31.0

# Copy actual Python file instead of inline
COPY simple_batch_worker.py /app/
COPY requirements.txt /app/

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

CMD ["python3", "simple_batch_worker.py"]