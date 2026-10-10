"""Anomaly-flagging consumer for synthetic ngFWA telemetry.

Reads Avro-encoded telemetry from Confluent Cloud, applies simple
threshold rules, and writes every record to Postgres. The embedding
column is a placeholder vector built from the three numeric readings
(signal, SNR, load) so the pgvector column and index exist end to end;
Stage 2 replaces it with a real semantic embedding without changing the
table shape.
"""
import os

import psycopg
from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import StringDeserializer

TOPIC = os.environ["KAFKA_TOPIC"]
BOOTSTRAP_SERVERS = os.environ["KAFKA_BOOTSTRAP_SERVERS"]
KAFKA_API_KEY = os.environ["KAFKA_API_KEY"]
KAFKA_API_SECRET = os.environ["KAFKA_API_SECRET"]
SCHEMA_REGISTRY_URL = os.environ["SCHEMA_REGISTRY_URL"]
SCHEMA_REGISTRY_API_KEY = os.environ["SCHEMA_REGISTRY_API_KEY"]
SCHEMA_REGISTRY_API_SECRET = os.environ["SCHEMA_REGISTRY_API_SECRET"]
CONSUMER_GROUP = os.environ.get("KAFKA_CONSUMER_GROUP", "ngfwa-anomaly-consumer")

DATABASE_URL = os.environ["DATABASE_URL"]  # postgresql://user:pass@host:5432/dbname

SIGNAL_FLOOR_DBM = float(os.environ.get("SIGNAL_FLOOR_DBM", "-105"))
SNR_FLOOR_DB = float(os.environ.get("SNR_FLOOR_DB", "5"))
LOAD_CEILING_PCT = float(os.environ.get("LOAD_CEILING_PCT", "95"))


def classify(reading: dict) -> tuple[bool, str | None]:
    reasons = []
    if reading["link_state"] != "UP":
        reasons.append(f"link_state={reading['link_state']}")
    if reading["signal_strength_dbm"] < SIGNAL_FLOOR_DBM:
        reasons.append(f"signal {reading['signal_strength_dbm']} dBm below floor")
    if reading["snr_db"] < SNR_FLOOR_DB:
        reasons.append(f"SNR {reading['snr_db']} dB below floor")
    if reading["sector_load_pct"] > LOAD_CEILING_PCT:
        reasons.append(f"sector load {reading['sector_load_pct']}% over ceiling")
    return (len(reasons) > 0, "; ".join(reasons) if reasons else None)


def placeholder_embedding(reading: dict) -> list[float]:
    return [
        reading["signal_strength_dbm"],
        reading["snr_db"],
        reading["sector_load_pct"],
    ]


INSERT_SQL = """
    INSERT INTO telemetry_events
        (device_id, sector_id, event_time, signal_strength_dbm, snr_db,
         sector_load_pct, link_state, is_anomaly, anomaly_reason, embedding)
    VALUES (%s, %s, to_timestamp(%s / 1000.0), %s, %s, %s, %s, %s, %s, %s)
"""


def main() -> None:
    schema_registry_client = SchemaRegistryClient({
        "url": SCHEMA_REGISTRY_URL,
        "basic.auth.user.info": f"{SCHEMA_REGISTRY_API_KEY}:{SCHEMA_REGISTRY_API_SECRET}",
    })
    avro_deserializer = AvroDeserializer(schema_registry_client)

    consumer = DeserializingConsumer({
        "bootstrap.servers": BOOTSTRAP_SERVERS,
        "security.protocol": "SASL_SSL",
        "sasl.mechanisms": "PLAIN",
        "sasl.username": KAFKA_API_KEY,
        "sasl.password": KAFKA_API_SECRET,
        "key.deserializer": StringDeserializer("utf_8"),
        "value.deserializer": avro_deserializer,
        "group.id": CONSUMER_GROUP,
        "auto.offset.reset": "earliest",
    })
    consumer.subscribe([TOPIC])

    print(f"consuming from topic '{TOPIC}', writing to Postgres")

    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"consumer error: {msg.error()}")
                continue

            reading = msg.value()
            is_anomaly, reason = classify(reading)
            if is_anomaly:
                print(f"anomaly: {reading['device_id']} — {reason}")

            with conn.cursor() as cur:
                cur.execute(
                    INSERT_SQL,
                    (
                        reading["device_id"],
                        reading["sector_id"],
                        reading["event_time"],
                        reading["signal_strength_dbm"],
                        reading["snr_db"],
                        reading["sector_load_pct"],
                        reading["link_state"],
                        is_anomaly,
                        reason,
                        placeholder_embedding(reading),
                    ),
                )


if __name__ == "__main__":
    main()
