"""Synthetic ngFWA telemetry producer.

Emits one record per simulated device per interval to a Confluent Cloud
topic, Avro-encoded against the schema registered in Schema Registry.
All values are synthetic; nothing here reads from or resembles any
production system. Credentials come from environment variables only.
"""
import os
import random
import time
from datetime import datetime, timezone

from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer

TOPIC = os.environ["KAFKA_TOPIC"]
BOOTSTRAP_SERVERS = os.environ["KAFKA_BOOTSTRAP_SERVERS"]
KAFKA_API_KEY = os.environ["KAFKA_API_KEY"]
KAFKA_API_SECRET = os.environ["KAFKA_API_SECRET"]
SCHEMA_REGISTRY_URL = os.environ["SCHEMA_REGISTRY_URL"]
SCHEMA_REGISTRY_API_KEY = os.environ["SCHEMA_REGISTRY_API_KEY"]
SCHEMA_REGISTRY_API_SECRET = os.environ["SCHEMA_REGISTRY_API_SECRET"]

DEVICE_COUNT = int(os.environ.get("DEVICE_COUNT", "20"))
EMIT_INTERVAL_SECONDS = float(os.environ.get("EMIT_INTERVAL_SECONDS", "2"))
ANOMALY_RATE = float(os.environ.get("ANOMALY_RATE", "0.03"))

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "schema", "telemetry-value.avsc")


def load_schema() -> str:
    with open(SCHEMA_PATH, "r") as f:
        return f.read()


def build_device_fleet(count: int) -> list[dict]:
    sectors = [f"SITE-{n:02d}-{side}" for n in range(1, 6) for side in "ABC"]
    return [
        {"device_id": f"CPE-{n:05d}", "sector_id": random.choice(sectors)}
        for n in range(count)
    ]


def sample_reading(device: dict, force_anomaly: bool) -> dict:
    if force_anomaly:
        signal = random.uniform(-125, -112)
        snr = random.uniform(-2, 3)
        load = random.uniform(95, 140)
        state = random.choice(["DEGRADED", "DOWN"])
    else:
        signal = random.uniform(-95, -60)
        snr = random.uniform(12, 35)
        load = random.uniform(5, 85)
        state = "UP"

    return {
        "device_id": device["device_id"],
        "sector_id": device["sector_id"],
        "event_time": int(datetime.now(timezone.utc).timestamp() * 1000),
        "signal_strength_dbm": round(signal, 1),
        "snr_db": round(snr, 1),
        "sector_load_pct": round(load, 1),
        "link_state": state,
    }


def delivery_report(err, msg):
    if err is not None:
        print(f"delivery failed: {err}")


def main() -> None:
    schema_registry_client = SchemaRegistryClient({
        "url": SCHEMA_REGISTRY_URL,
        "basic.auth.user.info": f"{SCHEMA_REGISTRY_API_KEY}:{SCHEMA_REGISTRY_API_SECRET}",
    })
    avro_serializer = AvroSerializer(schema_registry_client, load_schema())

    producer = SerializingProducer({
        "bootstrap.servers": BOOTSTRAP_SERVERS,
        "security.protocol": "SASL_SSL",
        "sasl.mechanisms": "PLAIN",
        "sasl.username": KAFKA_API_KEY,
        "sasl.password": KAFKA_API_SECRET,
        "key.serializer": StringSerializer("utf_8"),
        "value.serializer": avro_serializer,
    })

    fleet = build_device_fleet(DEVICE_COUNT)
    print(f"producing synthetic telemetry for {len(fleet)} devices to topic '{TOPIC}'")

    try:
        while True:
            for device in fleet:
                force_anomaly = random.random() < ANOMALY_RATE
                reading = sample_reading(device, force_anomaly)
                producer.produce(
                    topic=TOPIC,
                    key=reading["device_id"],
                    value=reading,
                    on_delivery=delivery_report,
                )
            producer.poll(0)
            time.sleep(EMIT_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        pass
    finally:
        remaining = producer.flush(10)
        print(f"stopped; {remaining} messages left undelivered")


if __name__ == "__main__":
    main()
