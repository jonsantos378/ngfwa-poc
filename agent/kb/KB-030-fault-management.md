---
doc_id: KB-030
title: Fault management integration for ngFWA
version: 1.4
owner: OSS Integration (fictional)
last_reviewed: 2026-10-19
classification: synthetic
---

# Fault management integration for ngFWA

## 1. Purpose

This document describes how ngFWA alarms reach the carrier's fault management system, how they are mapped and correlated, and when a trouble ticket opens. It follows the ITU-T X.733 alarm model and TM Forum alarm management (TMF642) and trouble ticket (TMF621) patterns.

## 2. Alarm flow

1. The EMS raises an alarm on a base station, sector or CPE.
2. The EMS posts the alarm to the fault management webhook (`POST /alarms`) within 30 seconds.
3. Fault management maps the alarm (section 3), correlates it (section 4), and decides whether to open a ticket (section 5).
4. When the condition clears, the EMS posts a `CLEARED` event with the same alarm ID.

## 3. Severity mapping

| EMS alarm | X.733 severity | Example cause |
|---|---|---|
| `BS_DOWN` | Critical | Base station power or backhaul loss |
| `SECTOR_DOWN` | Critical | Sector radio failure |
| `SECTOR_CONGESTED` | Major | Sector load above 95% for 15 minutes (KB-040) |
| `CPE_LINK_DOWN` | Minor | CPE powered off or lost link |
| `CPE_LINK_DEGRADED` | Warning | Signal or SNR below threshold (KB-040) |
| `CPE_CONFIG_MISMATCH` | Warning | Profile differs from the activated speed tier |

## 4. Correlation rules

Correlation stops one root cause from flooding operations with symptom alarms:

| Rule | Condition | Result |
|---|---|---|
| Parent suppression | A `BS_DOWN` or `SECTOR_DOWN` alarm is active | All CPE alarms on the affected sectors are suppressed and linked to the parent |
| Sector-wide degradation | 30% or more of a sector's CPEs report `CPE_LINK_DEGRADED` within 10 minutes | One `SECTOR_DEGRADED` incident replaces the individual CPE alarms |
| Flapping | The same CPE raises and clears an alarm more than 5 times in 1 hour | Alarm held as `FLAPPING`; RAN Engineering reviews |

The sector-wide rule is the main way to tell an **interference or capacity** problem (many CPEs on one sector) from an **installation** problem (one CPE). See the triage tree in KB-050.

## 5. Ticket rules

| Severity | Ticket | Initial assignee | Response target |
|---|---|---|---|
| Critical | Opened automatically | NOC tier 2 | 15 minutes |
| Major | Opened automatically | NOC tier 1 | 1 hour |
| Minor | Opened if active more than 1 hour | NOC tier 1 | 4 hours |
| Warning | No ticket; tracked in performance management | — | — |

A ticket (TMF621) carries the alarm ID, affected sector and CPE IDs, and the number of customers impacted, taken from service inventory (KB-010).

## 6. Clearing

Tickets close automatically 15 minutes after the alarm clears, if it doesn't recur. A recurrence within 24 hours reopens the same ticket instead of creating a new one.
