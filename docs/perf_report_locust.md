
# Week04 Performance Minimal Loop (Locust)

Goal: Build a minimal performance loop with **Locust** and produce a report:
- baseline test (A)
- higher load test (B)
- compare throughput + latency percentiles
- keep artifacts (HTML + CSV)

---

## Target
- Host: https://postman-echo.com
- Endpoints:
  - GET /get
  - POST /post

---

## Commands

### Group A (baseline)
```bash
locust -f perf/locustfile.py --headless -u 10 -r 2 -t 60s \
  --host https://postman-echo.com \
  --csv reports/locust \
  --html reports/locust.html

Group B (higher load)

locust -f perf/locustfile.py --headless -u 20 -r 4 -t 60s \
  --host https://postman-echo.com \
  --csv reports/locust_B \
  --html reports/locust_B.html

Artifacts:
	•	HTML:
	•	reports/locust.html
	•	reports/locust_B.html
	•	CSV:
	•	reports/locust_stats.csv / reports/locust_stats_history.csv (Group A)
	•	reports/locust_B_stats.csv / reports/locust_B_stats_history.csv (Group B)

⸻

Results Summary

Group	Users (-u)	Spawn (-r)	Duration	Total Req	Fail	RPS (agg)	Avg (ms)	P95 (ms)	P99 (ms)	Max (ms)
A	10	2	60s	279	0	4.69	1441	4200	6600	16000
B	20	4	59s	572	0	9.62	1365	3500	8000	18000

Notes:
	•	P95 = 95th percentile (95% of requests finish within this time).
	•	P99 = tail latency indicator (very sensitive to spikes).

⸻

Observations
	1.	Throughput scales up:

	•	RPS nearly doubled from 4.69 → 9.62 when users increased 10 → 20.

	2.	Average latency slightly improved:

	•	Avg 1441ms → 1365ms (this can happen due to sampling/network variance; not over-interpreted).

	3.	Tail latency becomes sharper at higher load:

	•	P95 improved (4200ms → 3500ms),
	•	but P99 got worse (6600ms → 8000ms) and Max increased (16s → 18s).
This suggests the system is stable for most requests but has occasional long-tail spikes (common on public internet services).

	4.	0 failures in both groups:

	•	Failure rate stayed 0, indicating no immediate error-rate regression under the tested load.

⸻

Endpoint-level Notes (Group B)
	•	GET /get:
	•	P95 3400ms, P99 7900ms, Max 18000ms
	•	POST /post:
	•	P95 3600ms, P99 11000ms, Max 16000ms

POST shows heavier tail latency, likely due to larger payload/processing path or network sensitivity (expected for public echo services).

⸻

Interview-ready Summary (60s)

Built a minimal performance test loop using Locust:
	•	defined baseline (u=10) and higher-load run (u=20)
	•	collected HTML/CSV artifacts for reproducibility
	•	compared RPS + P95/P99 to evaluate throughput and tail latency
Result:
	•	throughput scaled ~2x with 0 failures
	•	tail latency (P99/Max) increased under higher load, highlighting long-tail risk and the need for stable environments / longer runs for production-level evaluation.

⸻

Next Improvement (Optional)
	•	Add a unified entry in scripts/run.ps1 (Mode=perf) to standardize local runs.
	•	Define a simple SLA threshold (example): P95 < 5s and error rate < 1%.
