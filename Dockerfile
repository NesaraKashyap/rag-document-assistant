FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY documents/ ./documents/
COPY eval/ ./eval/

EXPOSE 8000

CMD ["sh", "-c", "python -m src.store_embeddings && uvicorn src.api:app --host 0.0.0.0 --port 8000"]