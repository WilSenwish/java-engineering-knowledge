---
来源站点: xiaolinnote.com
原文链接: https://xiaolinnote.com/ai/llm/lora.html
抓取日期: 2026-10-28
所属知识域: 域6
板块: LoRA
---

# LoRA：除了省参数还有什么

旁路 ΔW ≈ α·(B@A)，W 冻结。r=8~16。7B 可训参数可降到 ~0.3%。

除省参数外五优点：
1. 推理可合并进 W，零额外延迟（优于 Adapter）
2. 一基底多 LoRA 热切换（几十 MB/套）
3. 灾难性遗忘风险更低（仍需回归评测）
4. 训练稳、超参不敏感
5. LoRA Merging 加权融合能力

vs 全量：效果接近、资源远低；vs Adapter：无推理税、可合并。
