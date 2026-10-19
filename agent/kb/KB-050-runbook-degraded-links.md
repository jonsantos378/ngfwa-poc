---
doc_id: KB-050
title: "Runbook: triaging degraded ngFWA links"
version: 4.0
owner: NOC Operations (fictional)
last_reviewed: 2026-10-19
classification: synthetic
---

# Runbook: triaging degraded ngFWA links

## 1. When to use this runbook

Use it when a CPE has flagged readings (KB-040), a `CPE_LINK_DEGRADED` alarm is open (KB-030), or a customer reports slow or dropping service.

## 2. Step 1: one CPE or the whole sector?

Look up the CPE's serving sector, then check how many CPEs on that sector are degraded in the last 10 minutes.

| Finding | Likely cause | Go to |
|---|---|---|
| 30% or more of the sector's CPEs degraded | Sector problem: interference, congestion or radio fault | Step 3 |
| Only this CPE (or a few) degraded | Installation or premises problem | Step 2 |
| The sector has an active `SECTOR_DOWN` or `BS_DOWN` alarm | Parent outage | Stop: work the parent ticket (KB-030) |

## 3. Step 2: single-CPE checks

Read the CPE's last 30 minutes of telemetry and match the pattern:

| Pattern | Likely cause | Action |
|---|---|---|
| Signal below −105 dBm, SNR normal | Misalignment, new obstruction (tree growth, new building), or antenna moved | Dispatch a technician to re-aim or raise the antenna; compare with the install reading (KB-020, section 3) |
| SNR below 5 dB, signal normal | Local interference at the premises | Ask the customer about new equipment near the CPE; check whether neighboring CPEs show the same pattern |
| Link `DOWN`, all values missing | Power or cabling at the premises | Customer care confirms power to the CPE before dispatch |
| Readings swing between healthy and degraded every few minutes | Intermittent connector, or weather | If it lasts more than 24 hours, dispatch to check the cabling |

## 4. Step 3: sector-level checks

| Pattern | Likely cause | Action |
|---|---|---|
| Sector load above 95% on most readings | Congestion | Raise a capacity ticket for RAN Engineering; pause new sales on the sector (serviceability rule in KB-020) |
| SNR low across many CPEs, load normal | External interference | RAN Engineering runs a spectrum scan; consider a channel change (change control, KB-070) |
| Signal low across many CPEs | Base station radio or antenna fault | Escalate to RAN Engineering as Critical |

## 5. Escalation

| Condition | Escalate to | Severity |
|---|---|---|
| Single CPE unresolved after one technician visit | RAN Engineering | Minor |
| Sector-wide degradation lasting more than 30 minutes | RAN Engineering on-call | Major |
| Any sector or base station outage | NOC tier 2 and RAN Engineering on-call | Critical |

## 6. Closing

Record the cause and fix in the ticket (TMF621). If a technician re-aimed or moved a CPE, confirm that inventory shows the correct serving sector and antenna height (KB-010).
