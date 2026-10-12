# ngFWA Telemetry Pipeline — Stage 1 POC

Synthetic fixed-wireless-access telemetry streamed through Confluent Cloud,
flagged for anomalies, and deployed to a personal k3s cluster via GitOps.
All data is synthetic and runs on personal infrastructure — no employer data,
hardware, or credentials.

Built by architecting and directing an AI-assisted build (Claude Code) under
my own technical direction; see "How this was built" below.

## Architecture

```
synthetic producer -> Confluent Cloud (topic + Schema Registry)
                         |-- managed connector --> S3 or Postgres sink
                         '-- anomaly consumer   --> Postgres + pgvector
k3s (VPS) <- Argo CD <- this Git repo (k8s/)
```

## Status

- [ ] Day 1 — VPS + k3s + repo
- [ ] Day 2 — Confluent Cloud, schema, producer
- [ ] Day 3 — connector, consumer, anomaly detection
- [ ] Days 4–5 — Argo CD / Flux GitOps rollout
- [ ] Days 6–7 — README, diagram, talk track (EN/PT)

## Repo layout

```
producer/        synthetic telemetry producer (Python, confluent-kafka)
consumer/        anomaly-flagging consumer -> Postgres/pgvector
schema/          Avro schema registered in Schema Registry
k8s/             plain Kubernetes manifests Argo CD syncs from
                 (includes Postgres + pgvector and its schema)
aws/             IAM policy for the S3 sink connector's role
templates/       secret template (kept out of k8s/ so Argo CD never applies it)
argocd/          the Argo CD Application pointing at this repo
```

## Configuration

Every credential is an environment variable, injected in the cluster via a
Kubernetes Secret. Copy `templates/secret.example.yaml` to `k8s/secret.yaml`,
fill in real values, and `kubectl apply -f k8s/secret.yaml`. That file is
gitignored, so it never reaches the repo or Argo CD. The template lives
outside `k8s/` because Argo CD applies every manifest in that folder.
Nothing is hardcoded in code or committed manifests.

Local run (outside the cluster) needs the same variables exported in your
shell: see `producer/producer.py` and `consumer/consumer.py` for the full
list.

## Running locally

```bash
export KAFKA_TOPIC=ngfwa-telemetry
export KAFKA_BOOTSTRAP_SERVERS=...
export KAFKA_API_KEY=...
export KAFKA_API_SECRET=...
export SCHEMA_REGISTRY_URL=...
export SCHEMA_REGISTRY_API_KEY=...
export SCHEMA_REGISTRY_API_SECRET=...
export DATABASE_URL=postgresql://ngfwa:<password>@localhost:15432/ngfwa_poc

python -m venv .venv && source .venv/bin/activate
pip install -r producer/requirements.txt -r consumer/requirements.txt

python producer/producer.py   # terminal 1
python consumer/consumer.py   # terminal 2
```

Postgres runs in k3s and creates its schema on first start
(`k8s/postgres-init.yaml`). To reach it from a laptop, tunnel through the
VPS (terminal 3):

```bash
ssh -L 15432:127.0.0.1:15432 root@<vps-ip> \
  'kubectl -n ngfwa-poc port-forward svc/postgres 15432:5432'
```

## Building container images

Build from the repo root so the Dockerfiles can reach `schema/`:

```bash
docker build -f producer/Dockerfile -t ghcr.io/<you>/ngfwa-producer:latest .
docker build -f consumer/Dockerfile -t ghcr.io/<you>/ngfwa-consumer:latest .
```

Push to a registry the cluster can pull from, then update the `image:` field
in `k8s/producer-deployment.yaml` and `k8s/consumer-deployment.yaml`.

## Deploying with Argo CD

```bash
kubectl apply -f argocd/application.yaml
```

Argo CD watches `k8s/` on `main` and reconciles the cluster to match. A
commit that changes a manifest rolls out automatically (`prune: true`,
`selfHeal: true`).

## How this was built

I architected this pipeline (schema design, anomaly thresholds, GitOps
topology) and directed Claude Code through the implementation. I do not
claim hands-on Python, Java, or prior production Confluent/GitOps
experience — this project is where that hands-on experience is being built.

## Talk track (2 minutes)

_To fill in once the pipeline is live end to end — English and Portuguese._

## License / scope

Personal project. Synthetic data only. Not affiliated with, and contains
no data or code from, any current or former employer.
