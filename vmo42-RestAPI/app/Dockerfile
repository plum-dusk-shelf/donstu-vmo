FROM python:3.11.2-slim

COPY * .

RUN python -m pip install --no-cache-dir -r requirements.txt

ENV POSTGRES_HOST="restapi-db"
ENV POSTGRES_DB="restapi-database"
ENV POSTGRES_USER="restapi-admin-user"
ENV POSTGRES_PASSWORD="IoRKXjgL"

EXPOSE 4000/tcp

CMD ["uvicorn", "--host 0.0.0.0", "--port 4000", "main:app", "--reload"]
