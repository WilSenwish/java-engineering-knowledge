---
来源站点: xiaolinnote.com
原文链接: https://xiaolinnote.com/ai/llm/moe.html
抓取日期: 2026-10-28
所属知识域: 域6
板块: MoE
---

# MoE 混合专家

FFN → N 专家 + Router Top-K。哲学：**总参数大、激活参数小**（DeepSeek V3：671B / 37B）。

组件：Experts、Router、负载均衡（防专家不平衡；DeepSeek Auxiliary-Loss-Free）。

反直觉：显存按总参数；延迟按激活参数。训练坑：不平衡、Router 不稳、All-to-All；部署坑：全量加载、批量通信、热门专家。

2024 爆发因：训练 know-how + vLLM/SGLang 支持 + DeepSeek 成本证明。Dense 在中小规模/延迟敏感仍常用。
