---
来源站点: xiaolinnote.com
原文链接: https://xiaolinnote.com/ai/llm/evaluation_metrics.html
抓取日期: 2026-10-28
所属知识域: 域6
---

# 评测

- MMLU / MMLU-Pro：综合知识
- HumanEval / SWE-bench：代码
- GSM8K / MATH / GPQA：数学与科学推理
- MT-Bench / Arena：对话与偏好
- 数据污染：公开题可能已在预训练里，榜单虚高

工程闭环：50–200 条业务黄金集（真实请求 + 人工期望）+ 客观自动判 / 主观 LLM-as-Judge（抽查 10–20%）+ 线上满意度、完成率、放弃率。
