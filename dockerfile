FROM python:3.10 as builder
RUN apt-get update
WORKDIR /app
RUN python3 -m venv venv
COPY requirements.txt /app/requirements.txt
RUN /app/venv/bin/pip install -r requirements.txt

FROM python:3.10-slim

WORKDIR /app
COPY --from=builder /app/venv /app/venv
COPY src /app


CMD ["venv/bin/python3", "app.py"]