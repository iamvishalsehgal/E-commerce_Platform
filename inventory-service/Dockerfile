FROM python:3.10.8-slim-buster
RUN apt-get update && apt-get install -y build-essential
WORKDIR /app
COPY . .
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install -r requirements.txt
CMD ["/venv/bin/gunicorn", "--bind", "0.0.0.0:5005", "--workers", "4", "app:app"]