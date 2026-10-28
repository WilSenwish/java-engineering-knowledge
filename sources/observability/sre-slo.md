---
来源站点: Google SRE Book
原文链接: https://sre.google/sre-book/service-level-objectives/
抓取日期: 2026-10-28
所属知识域: 域5
---

# SLI / SLO / SLA 与错误预算

- SLI：量化的服务质量（延迟、错误率、吞吐、可用性=成功请求占比）。不要把能采的指标都当 SLI。
- SLO：SLI 的目标区间。例如 99% 的 Get 在 100ms 内。可按用户类拆。
- SLA：带后果的合同。没有明确后果的就是 SLO。SRE 通常不签 SLA，但要避免触发后果。

100% 既不现实也不该追求（Chubby 过稳会养出错误依赖，Google 会人为制造故障把可用性压回目标）。错误预算 = 允许错过 SLO 的比例，用来决定还能不能发版。目标不要按当前表现锁死，避免绝对化。
