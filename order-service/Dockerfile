FROM python:3.10.7-slim
WORKDIR /usr/src/myapp
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5004
ENV DB_URL=sqlite:///order.db
CMD ["python3", "app.py"]