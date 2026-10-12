FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY consumer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY consumer/consumer.py .
RUN useradd --system --uid 10001 app
USER 10001
CMD ["python", "consumer.py"]
