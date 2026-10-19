---
doc_id: KB-040
title: Performance telemetry and thresholds for ngFWA
version: 2.3
owner: Data Platform (fictional)
last_reviewed: 2026-10-19
classification: synthetic
---

# Performance telemetry and thresholds for ngFWA

## 1. Purpose

This document defines the radio KPIs every CPE reports, how they are delivered, and the thresholds that mark a reading as degraded. It is the reference for performance management (TMF628), the anomaly consumer, and the triage runbook (KB-050).

## 2. Telemetry stream

| Property | Value |
|---|---|
| Transport | Kafka topic `ngfwa-telemetry` |
| Format | Avro; schema registered as subject `ngfwa-telemetry-value` |
| Key | CPE ID (keeps each CPE's readings in order) |
| Frequency | One reading per CPE every 2 seconds |
| Retention on the topic | 7 days |
| Long-term storage | Hourly files in object storage for analytics; flagged and raw readings in the operational database |

## 3. KPIs

| Field | Unit | Meaning | Typical healthy range |
|---|---|---|---|
| `signal_strength_dbm` | dBm | Received signal strength at the CPE | −95 to −60 |
| `snr_db` | dB | Signal-to-noise ratio | 12 to 35 |
| `sector_load_pct` | % | Load on the CPE's serving sector at the time of the reading | 5 to 85 |
| `link_state` | enum | `UP`, `DEGRADED` or `DOWN` | `UP` |

## 4. Degradation thresholds

A reading is **flagged** when any condition is true:

| Rule | Threshold | Why |
|---|---|---|
| Link not up | `link_state` is `DEGRADED` or `DOWN` | The radio itself reports a problem |
| Weak signal | `signal_strength_dbm` below −105 | Near the edge of reliable reception; throughput drops sharply |
| Low SNR | `snr_db` below 5 | Too noisy to sustain higher modulation; points to interference |
| Congested sector | `sector_load_pct` above 95 | Sector near capacity; all its customers slow down |

The anomaly consumer records every reason that applies, not just the first. Several reasons on one reading narrow the cause (see KB-050).

## 5. From readings to alarms

A single flagged reading is not an alarm; it may be a moment of rain fade or a passing truck. Performance management raises an alarm (KB-030) only when the condition persists:

| Alarm | Persistence rule |
|---|---|
| `CPE_LINK_DEGRADED` | 60% or more of a CPE's readings flagged over 10 minutes |
| `SECTOR_CONGESTED` | Sector load above 95% for 15 consecutive minutes |
| `SECTOR_DEGRADED` | 30% or more of a sector's CPEs degraded within 10 minutes (KB-030, section 4) |

## 6. Data quality

- Readings with timestamps more than 5 minutes in the future are discarded.
- A CPE that sends no readings for 10 minutes is treated as `DOWN` for alarm purposes.
- Threshold changes are configuration changes and follow change control (KB-070).
