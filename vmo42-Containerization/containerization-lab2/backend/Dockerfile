FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV POSTGRES_HOST="my-site-db"
ENV POSTGRES_DB="mydatabase"
ENV POSTGRES_USER="myuser"
ENV POSTGRES_PASSWORD="mypassword"

COPY app.py .

CMD ["python", "app.py"]
