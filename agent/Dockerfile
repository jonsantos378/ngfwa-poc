FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 \
    MODEL_CACHE=/models
WORKDIR /app
COPY agent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download, smoke-test and fingerprint the embedding model at build time,
# then forbid runtime downloads so the image always uses these exact weights.
COPY agent/embeddings.py .
RUN python embeddings.py
ENV HF_HUB_OFFLINE=1

COPY agent/ingest.py agent/search.py ./
COPY agent/kb ./kb
RUN useradd --system --uid 10001 app && chown -R 10001 /models
USER 10001
CMD ["python", "ingest.py"]
