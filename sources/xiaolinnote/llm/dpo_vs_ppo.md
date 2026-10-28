---
来源站点: xiaolinnote.com
原文链接: https://xiaolinnote.com/ai/llm/dpo_vs_ppo.html
抓取日期: 2026-10-28
所属知识域: 域6
---

# DPO vs PPO

PPO/RLHF：偏好排序 → 奖励模型 → PPO 优化 policy。同时在线 4 个模型：policy、reference（KL 防 reward hacking）、reward、value。
DPO：把带 KL 的 RLHF 目标写成 (prompt, chosen, rejected) 上的监督损失，只需 policy + reference。探索弱于在线 RL，但稳定。
GRPO：去掉 value，同一题采样 G 个回答，用组内均值/标准差做优势。可验证任务（数学/代码）奖励可以是 0/1。DeepSeek R1 这条线。
