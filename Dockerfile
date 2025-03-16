FROM python:3.12.5-slim-bookworm

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

COPY ./src /app/src

CMD ["gunicorn", "-c", "src/settings/gunicorn.py", "-w", "1", "--threads=2", "-k", "src.settings.gunicorn.UvloopUvicornWorker", "src.api:app", "--log-level", "Debug", "-b", "0.0.0.0:3000", "--timeout", "60"]
