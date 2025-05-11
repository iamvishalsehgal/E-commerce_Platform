FROM python:3.10.7-slim
WORKDIR /usr/src/myapp
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5005
ENV DB_URL=sqlite:///inventory.db
ENV PORT=5005
CMD ["gunicorn", "--bind", "0.0.0.0:5005", "--workers", "4", "app:app"]