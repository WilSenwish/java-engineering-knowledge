---
来源站点: xiaolinnote.com
原文链接: https://xiaolinnote.com/ai/llm/post_training.html
抓取日期: 2026-10-28
所属知识域: 域6
---

# Post-Training 家族

SFT 之后不是只有 RLHF。五类常组合而不是互相替代：

- RLHF：奖励模型 + PPO + reference KL
- DPO：偏好对监督学习
- GRPO：组内相对优势，砍掉 Value Model
- 拒绝采样：生成多份，筛高分再 SFT（Llama 2 用过）
- RLAIF：用更强模型代替人类打偏好

Llama 2-Chat 公开流程是 SFT + 拒绝采样 + PPO，不是 DPO。
