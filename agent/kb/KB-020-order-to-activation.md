---
doc_id: KB-020
title: Order to activation for ngFWA service
version: 3.1
owner: OSS Integration and BSS Integration (fictional)
last_reviewed: 2026-10-19
classification: synthetic
---

# Order to activation for ngFWA service

## 1. Purpose

This document describes how a customer order for ngFWA service becomes an active connection: ordering, serviceability, installation, EMS registration and activation. It follows TM Forum service ordering (TMF641) and service activation (TMF640) patterns.

## 2. Sequence

1. **Product order (BSS).** Customer care or the online store creates a product order (TMF622) with the install address and speed tier (100, 300 or 500 Mbps).
2. **Serviceability check (OSS).** The order is decomposed into a service order (TMF641). The check passes only if all three conditions hold:

   | Check | Rule |
   |---|---|
   | Coverage | The address is inside a serving sector's predicted coverage, with predicted signal strength of −95 dBm or better |
   | Capacity | The sector's sold capacity plus the new tier stays at or below 80% of its licensed capacity (KB-010) |
   | Sector health | The sector has no open critical alarm (KB-030) and its average load over the past 7 days is below 85% (KB-040) |

   If any check fails, the order is held with reason `NOT_SERVICEABLE` and the specific rule that failed.
3. **Installation appointment.** Field Operations schedules the install. The installer mounts the CPE, aims it at the serving sector and records the antenna height and the received signal strength at install.
4. **EMS registration.** The installer's app calls `POST https://ems.example.net/api/v1/cpes` with the CPE serial number and serving sector ID. The EMS returns the CPE ID (`CPE-NNNNN`). OSS creates the CPE record in inventory (KB-010).
5. **Activation (TMF640).** The activation service calls `PUT https://ems.example.net/api/v1/cpes/{cpe_id}/profile` with the speed-tier profile. Activation succeeds when the EMS reports link state `UP` and the first telemetry reading shows signal strength of −95 dBm or better.
6. **Completion.** Service inventory (TMF638) records the active service, billing starts (KB-060), and the order closes.

## 3. Install acceptance criteria

An install is accepted only if the first 5 minutes of telemetry (KB-040) show:
- Signal strength of −95 dBm or better (stronger than the −105 dBm alarm floor, leaving margin for weather and foliage)
- SNR of 15 dB or better
- Link state `UP` for the whole window

An install that misses these criteria stays in `ACTIVATION_PENDING`. The installer re-aims the CPE or raises the antenna before leaving site.

## 4. Error codes

| Code | Meaning | Resolution |
|---|---|---|
| `NOT_SERVICEABLE` | A serviceability rule failed | Offer an alternative sector or a waitlist |
| `SECTOR_NOT_FOUND` | Serving sector not in inventory | Complete site onboarding (KB-010) |
| `CPE_ALREADY_REGISTERED` | Serial number already active | Check for a duplicate order or a moved CPE |
| `ACTIVATION_TIMEOUT` | EMS did not confirm within 10 minutes | Retry once; then open a ticket with RAN Engineering |

## 5. Speed-tier changes

A speed change reuses steps 2 (capacity check only) and 5 (new profile). No field visit is needed. Billing changes on the next cycle (KB-060).
