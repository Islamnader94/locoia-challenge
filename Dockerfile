FROM python:3.6-slim

WORKDIR /app

COPY requirements.txt /app/
RUN apt-get update \
    && apt-get install -y gcc libmagic1 \
    && pip install -r requirements.txt \
    && apt-get autoremove --purge -y gcc \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

EXPOSE 8000
CMD [ "python", "gistapi.gistapi:app" ]
