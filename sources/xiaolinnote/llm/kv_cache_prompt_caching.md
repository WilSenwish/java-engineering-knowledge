---
来源站点: xiaolinnote.com
原文链接: https://xiaolinnote.com/ai/llm/kv_cache_prompt_caching.html
抓取日期: 2026-10-28
所属知识域: 域6
板块: KV Cache与Prompt Caching
---

# KV Cache 与 Prompt Caching

## 同一机制两时间尺度

- **KV Cache**：单次推理内。无缓存总计算 O(N³)；有缓存 O(N²)。自回归基本盘。
- **Prompt Caching**：跨请求复用相同前缀的 KV。Claude 显式 cache_control；OpenAI 自动。

## 显存公式

2×B×N×L×H×d_k×2B(FP16)。7B@32K ≈ 17GB 仅 KV。进阶：量化、PagedAttention、GQA。

## 工程陷阱

固定内容在前、动态在后；前缀差一字即 miss；低流量可能因写入溢价不划算。
