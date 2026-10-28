---
来源站点: xiaolinnote.com
原文链接: https://xiaolinnote.com/ai/llm/mha_mqa_gqa_flash_attention.html
抓取日期: 2026-10-28
所属知识域: 域6
板块: Attention优化
---

# MHA 局限与 MQA/GQA/Flash Attention

## MHA 三痛点

KV Cache 显存随 H×N 涨；Attention 访存受限（HBM）；O(N²) 复杂度。

## 结构层：MQA / GQA

- MQA：全头共享 1 套 K/V，显存 /H，效果降 2-5%
- GQA：H 头分 G 组共享，G=8 效果≈MHA、显存≈1/4（Llama3/Qwen 标配）
- MLA（DeepSeek）：低秩潜在压缩 K/V，另一路线

## 实现层：Flash Attention

分块 + 在线 softmax，中间 N×N 不落 HBM；显存 O(N²)→O(N)，速度×2-4；数学等价。

**叠加不是替代**：主流 = GQA + Flash Attention。
