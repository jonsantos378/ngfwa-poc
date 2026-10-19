---
doc_id: KB-010
title: Inventory onboarding for ngFWA sites, sectors and CPEs
version: 2.0
owner: OSS Integration (fictional)
last_reviewed: 2026-10-19
classification: synthetic
---

# Inventory onboarding for ngFWA sites, sectors and CPEs

## 1. Purpose

Every ngFWA resource must exist in the resource inventory (TMF639) before it can carry service. This document defines the object model, the onboarding sequence and the daily reconciliation with the EMS.

## 2. Object model

| Inventory object | Parent | Key attributes |
|---|---|---|
| Site | — | Site ID, address, latitude/longitude, tower height (m) |
| Base station | Site | Serial number, software version, commissioning date |
| Sector | Base station | Sector ID, azimuth (degrees), channel, licensed capacity (Mbps) |
| CPE | Sector (serving) | CPE ID, serial number, install address, antenna height (m), assigned speed tier |

A CPE is linked to exactly one **serving sector**. When a CPE is re-pointed to another sector, the inventory link must be updated in the same change (see section 5).

## 3. Onboarding a new site

1. RAN Engineering creates the site and base station in inventory with status `PLANNED`.
2. After installation, the base station registers with the EMS. The EMS assigns sector IDs following the `SITE-NN-X` convention (KB-000, section 5).
3. OSS Integration runs the sector import: `GET https://ems.example.net/api/v1/sectors?site=SITE-NN`. Each returned sector is created in inventory under its base station.
4. RAN Engineering sets the licensed capacity per sector. The serviceability check (KB-020) uses this value; a sector with no capacity value can't be sold.
5. Status changes to `IN_SERVICE` once all three sectors report telemetry (KB-040).

## 4. Onboarding a CPE

CPEs are onboarded during activation, not in bulk. The activation flow (KB-020, step 4) creates the CPE record, links it to its serving sector, and records the antenna height measured by the installer. A CPE that registers on the EMS without a matching inventory record raises a `ROGUE_CPE` reconciliation exception.

## 5. Daily reconciliation

At 02:00 UTC a job compares inventory against the EMS:

| Discrepancy | Automatic action | Human action |
|---|---|---|
| CPE in EMS, not in inventory (`ROGUE_CPE`) | Exception ticket | Field Operations verifies the install record |
| CPE in inventory, not seen by EMS for 7 days | Status set to `SUSPECT` | Customer care contacts the customer |
| CPE serving sector differs between systems | Inventory updated to the EMS value; change logged | RAN Engineering reviews if more than 5 CPEs moved in one sector in a day |
| Base station software version differs | Inventory updated | None |

The EMS is the source of truth for **live radio state** (serving sector, software version). Inventory is the source of truth for **commercial and physical attributes** (address, speed tier, install date).

## 6. Common errors

- **Sector ID typed with lowercase letters** (`site-02-a`): the import rejects it. Identifiers are uppercase.
- **CPE created before its sector exists:** activation fails with `SECTOR_NOT_FOUND`. Complete site onboarding first.
