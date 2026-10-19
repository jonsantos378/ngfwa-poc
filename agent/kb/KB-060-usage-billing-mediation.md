---
doc_id: KB-060
title: Usage and billing mediation for ngFWA
version: 1.1
owner: BSS Integration (fictional)
last_reviewed: 2026-10-19
classification: synthetic
---

# Usage and billing mediation for ngFWA

## 1. Purpose

This document describes how ngFWA usage becomes billable records, how speed tiers map to plans, and how billing is reconciled against the network. It follows TM Forum usage management (TMF635) patterns.

## 2. Usage records

The EMS produces one usage record per CPE per hour:

| Field | Meaning |
|---|---|
| `cpe_id` | CPE that generated the usage |
| `period_start`, `period_end` | The hour covered (UTC) |
| `bytes_down`, `bytes_up` | Traffic in each direction |
| `profile` | Speed-tier profile active during the hour |

Records are exported every hour to `https://ems.example.net/api/v1/usage?since=<timestamp>`. Mediation pulls them, removes duplicates by (`cpe_id`, `period_start`), and passes them to rating.

## 3. Plans and speed tiers

| Plan | Speed tier | Monthly data allowance |
|---|---|---|
| Home Basic | 100 Mbps | Unlimited |
| Home Plus | 300 Mbps | Unlimited |
| Business 500 | 500 Mbps | Unlimited |

Plans are unlimited, so usage is not charged per byte. It is still mediated, for three reasons: fair-use monitoring, capacity planning (KB-040), and catching CPEs whose active profile doesn't match the plan billed.

## 4. Profile reconciliation

Each night, mediation compares the profile in the usage records with the speed tier in service inventory (KB-010):

| Mismatch | Risk | Action |
|---|---|---|
| Network profile higher than the billed plan | Revenue leakage | Correct the EMS profile to the billed tier through activation (KB-020, section 5) |
| Network profile lower than the billed plan | Customer overbilled; complaint risk | Correct the profile and credit the customer |
| CPE has usage but no active service in inventory | Unbilled service | Open an exception for BSS Integration |

## 5. Timing

- A speed change takes effect on the network immediately and in billing from the next cycle.
- A disconnect stops usage records within 1 hour; billing ends on the disconnect date.
