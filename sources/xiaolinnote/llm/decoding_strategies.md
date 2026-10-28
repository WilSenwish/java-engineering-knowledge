---
来源站点: xiaolinnote.com
原文链接: https://xiaolinnote.com/ai/llm/decoding_strategies.html
抓取日期: 2026-10-28
所属知识域: 域6
---

# 解码：贪心 · Beam Search · 采样

每步从词表概率分布里选下一个 token。

- 贪心：最高概率，可复现，易复读。精确任务（代码/SQL/JSON）适用。
- Beam Search：保留 B 条路径选整句概率最高。翻译时代匹配「单一最优译文」。开放生成没有唯一最优，高概率往往最无聊，且要复制多份 KV Cache。
- 采样：Temperature 缩放 logits；Top-K 固定截断；Top-P 累加到阈值自适应截断。
- 进阶：推测解码（小模型起草、大模型验证）；Self-Consistency（多次采样多数投票）。

Temperature=0 接近贪心，不等于「永远正确」。
