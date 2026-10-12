FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY producer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY producer/producer.py .
COPY schema/telemetry-value.avsc ../schema/telemetry-value.avsc
RUN useradd --system --uid 10001 app
USER 10001
CMD ["python", "producer.py"]
