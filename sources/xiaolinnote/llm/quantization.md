---
来源站点: xiaolinnote.com
原文链接: https://xiaolinnote.com/ai/llm/quantization.html
抓取日期: 2026-10-28
所属知识域: 域6
---

# 量化：INT8/INT4 · GPTQ · AWQ · NF4

本质：FP16 经 scale/zero_point 映射到低比特。7B：14GB → INT4 约 3.5GB。

- GPTQ：逐层 + Hessian 误差补偿，极端低位更稳，量化慢，激活仍 FP16
- AWQ：约 1% salient 权重按激活幅度保护，推理 kernel 友好
- QLoRA NF4：按正态非均匀 4bit + 双重量化 + 分页优化器，消费卡可微调
- GGUF 是 llama.cpp 容器格式，不是算法

INT8 通常很接近；INT4 是部署甜蜜点但数学/长代码可能明显掉点。上线前用业务集评测。KV Cache 量化比权重量化更敏感。
