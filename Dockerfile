FROM python:3.11-slim-bookworm

EXPOSE 3000

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install --no-cache-dir --upgrade -r /app/requirements.txt && \
    apt-get purge -y --auto-remove && \
    rm -rf /var/lib/apt/lists/*

COPY ./lib /app/lib

CMD ["gunicorn", "-w 1", "-k", "uvicorn.workers.UvicornWorker", "lib:app", "--log-level", "Debug", "-b", "0.0.0.0:3000", "--timeout", "120"]
