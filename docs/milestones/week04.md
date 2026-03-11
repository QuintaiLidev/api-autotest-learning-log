# docs/milestones/week04.md

# Week04 Performance Minimal Loop (Locust)

## Goal
Build a minimal performance loop with Locust and produce reports that are reproducible and explainable:
- baseline test (Group A)
- higher load test (Group B)
- compare throughput and latency percentiles
- keep HTML/CSV artifacts

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
locust -f perf/locustfile.py --headless -u 10 -r 2 -t 60s --host https://postman-echo.com --csv reports/locust --html reports/locust.html

Group B (higher load)

locust -f perf/locustfile.py --headless -u 20 -r 4 -t 60s --host https://postman-echo.com --csv reports/locust_B --html reports/locust_B.html


⸻

Results Summary

Group	Users (-u)	Spawn (-r)	Duration	Total Req	Fail	RPS (agg)	Avg (ms)	P95 (ms)	P99 (ms)	Max (ms)
A	10	2	60s	279	0	4.69	1441	4200	6600	16000
B	20	4	59s	572	0	9.62	1365	3500	8000	18000


⸻

Key Observations
	1.	Throughput scaled up:

	•	RPS increased from 4.69 to 9.62 when users increased from 10 to 20.

	2.	Average latency did not worsen:

	•	Avg changed from 1441ms to 1365ms.

	3.	Tail latency is still the main risk:

	•	Group A aggregated P95/P99: 4200ms / 6600ms
	•	Group B aggregated P95/P99: 3500ms / 8000ms
	•	Max latency increased from 16s to 18s

	4.	Stability is good:

	•	Both groups had 0 failures

⸻

Endpoint-level Notes

Group A
	•	GET /get:
	•	P95: 4600ms
	•	P99: 6600ms
	•	Max: 16000ms
	•	POST /post:
	•	P95: 3100ms
	•	P99: 9200ms
	•	Max: 9200ms

Group B
	•	GET /get:
	•	P95: 3400ms
	•	P99: 7900ms
	•	Max: 18000ms
	•	POST /post:
	•	P95: 3600ms
	•	P99: 11000ms
	•	Max: 16000ms

⸻

Conclusion

This minimal Locust loop shows that:
	•	the system can handle higher load with 0 failures
	•	throughput scales up under higher concurrency
	•	long-tail latency (P99 / max latency) is still visible and should be treated as the main performance risk

For a public echo service, this is acceptable as a demo benchmark, but production-level evaluation would require:
	•	a more stable environment
	•	longer duration tests
	•	threshold-based assertions

⸻

What I learned
	•	how to define a minimal Locust scenario
	•	how to run headless performance tests
	•	how to read RPS / P95 / P99 / max latency
	•	how to compare two load groups (A/B)
	•	how to turn a test run into a report that can be explained in interviews

---
## 3）做一次“掌握检查”
这个是你这次最重要的部分。  
不是再写代码，而是确认你真的掌握了。


1）Locust 在项目里的作用是什么？
Locust 在我的项目里主要用于做接口性能测试，验证在一定并发和持续时间下，接口的吞吐量、响应时间、尾延迟和失败率表现如何。

2）perf/locustfile.py 是干什么的？
它是压测场景定义文件，用来定义要压哪些接口、请求参数、请求体、任务权重，以及怎么判断请求是否成功。

3）为什么要做 A/B 两组，而不是只跑一次？
因为只跑一次只能看到单一负载下的表现，A/B 两组是为了观察负载变化后，吞吐量、延迟和尾延迟是怎么变化的，从而看出趋势。

4）为什么 B 组里 RPS 提高了，但 P99 / Max 还是高？

RPS 提高说明系统在更高并发下仍然能处理更多请求，也就是吞吐量提升了。
但 P99 和 Max 仍然很高，说明虽然大多数请求能正常完成，但仍然有少量请求非常慢，这就是长尾延迟问题。
所以系统整体是可用的，但尾部性能还不够稳定。

5）为什么 0 failures 不等于性能完美？

0 failures 只说明这次测试里请求没有直接失败，不代表性能就完美。
因为即使请求都成功了，响应时间也可能很长，尤其是 P99 和 Max 仍然可能很高。
所以性能不仅看失败率，还要看吞吐量、平均响应时间和尾延迟。

---

