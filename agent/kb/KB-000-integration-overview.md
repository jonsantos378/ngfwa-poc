---
doc_id: KB-000
title: ngFWA integration overview
version: 1.2
owner: Network Integration Architecture (fictional)
last_reviewed: 2026-10-19
classification: synthetic
---

# ngFWA integration overview

## 1. Purpose

This document describes how the ngFWA platform connects to the carrier's operations (OSS), business (BSS) and decision-support (DSS) systems. Read it first; the other knowledge-base documents go deeper on each integration.

## 2. Platform components

| Component | Role |
|---|---|
| Base station (BS) | Tower-mounted radio serving three sectors (A, B, C), each covering about 120 degrees |
| Customer premises equipment (CPE) | Subscriber radio installed at the customer's home or business |
| Element management system (EMS) | Vendor software that configures base stations and CPEs, collects their alarms and statistics, and exposes a northbound REST API at `https://ems.example.net/api/v1` |
| Telemetry stream | Per-CPE radio readings published every 2 seconds to the Kafka topic `ngfwa-telemetry` |

## 3. Systems the platform integrates with

| Domain | System | Integration | Detail in |
|---|---|---|---|
| BSS | Product and service ordering | Orders for new service, speed changes and disconnects (TMF622, TMF641) | KB-020 |
| BSS | Billing and mediation | Usage records and speed-tier changes (TMF635) | KB-060 |
| OSS | Resource and service inventory | Sites, sectors, BSs and CPEs, plus the services running on them (TMF639, TMF638) | KB-010 |
| OSS | Service activation | Provisioning CPEs and speed tiers on the EMS (TMF640) | KB-020 |
| OSS | Fault management | EMS alarms into the alarm manager; trouble tickets (TMF642, TMF621) | KB-030 |
| OSS | Performance management | KPIs and threshold breaches (TMF628) | KB-040 |
| DSS | Data warehouse and analytics | Telemetry and inventory for capacity planning and churn analysis | KB-040 |

## 4. End-to-end flows

1. **Order to activation:** a customer order flows from BSS ordering, through a serviceability check against inventory and sector capacity, to CPE installation, EMS registration and activation. Inventory is updated at each step. See KB-020.
2. **Assure:** EMS alarms and telemetry threshold breaches reach fault and performance management. Correlated issues open trouble tickets. See KB-030, KB-040 and KB-050.
3. **Bill:** the EMS reports per-CPE usage; mediation rates it against the customer's plan. See KB-060.

## 5. Identifier conventions

All systems use the same identifiers, so records can be joined without translation tables:

| Object | Format | Example |
|---|---|---|
| Site | `SITE-NN` | `SITE-02` |
| Sector | `SITE-NN-X`, X = A, B or C | `SITE-02-A` |
| CPE | `CPE-NNNNN` | `CPE-00009` |

## 6. Ownership

| Area | Owning team (fictional) |
|---|---|
| EMS and radio configuration | RAN Engineering |
| Inventory, activation, assurance integrations | OSS Integration |
| Ordering and billing integrations | BSS Integration |
| Telemetry pipeline and analytics | Data Platform |
| API security and change control | Security Architecture (KB-070) |
