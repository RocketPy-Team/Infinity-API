FROM python:3.11-slim-bookworm

EXPOSE 3000

USER api

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install --no-cache-dir --upgrade -r /code/requirements.txt && \
    apt-get purge -y --auto-remove && \
    rm -rf /var/lib/apt/lists/*

COPY ./lib /code/lib

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "lib:app", "-b", "0.0.0.0:3000"]
