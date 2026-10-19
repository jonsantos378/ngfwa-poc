# Knowledge base: ngFWA OSS/BSS integration (synthetic)

**Everything in this folder is fictional.** These documents were written for this proof of concept. They describe a generic, vendor-neutral next-generation fixed wireless access (ngFWA) platform and how a carrier might integrate it with its OSS, BSS and DSS systems. They are not vendor documentation and contain no data from any real operator or vendor. Hostnames use the reserved `example.net` domain. Standards references (TM Forum Open APIs, ITU-T X.733) point to public specifications.

The AI agent retrieves from these documents and cites them by `doc_id` and section. Each document's front matter carries the metadata the audit trail records with every answer.

| doc_id | Title | Covers |
|---|---|---|
| KB-000 | Integration overview | System map, data flows, ownership |
| KB-010 | Inventory onboarding | Sites, sectors, base stations, CPEs; identifiers; reconciliation |
| KB-020 | Order to activation | Service ordering, serviceability check, CPE registration, activation |
| KB-030 | Fault management integration | Alarm flow, severity mapping, correlation, trouble tickets |
| KB-040 | Performance telemetry and thresholds | KPIs, streaming pipeline, threshold definitions |
| KB-050 | Runbook: degraded links | Triage decision tree, checks, escalation |
| KB-060 | Usage and billing mediation | Usage records, speed tiers, reconciliation |
| KB-070 | API security and change control | Authentication, least privilege, audit, change windows |
