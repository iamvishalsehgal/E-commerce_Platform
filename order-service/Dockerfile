FROM --platform=linux/amd64 python:3.10-slim
WORKDIR /usr/src/myapp
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5004
ENV PORT=5004
CMD ["gunicorn", "--bind", "0.0.0.0:5004", "--workers", "4", "app:app"]