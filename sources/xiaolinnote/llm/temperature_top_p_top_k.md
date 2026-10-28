---
来源站点: xiaolinnote.com
原文链接: https://xiaolinnote.com/ai/llm/temperature_top_p_top_k.html
抓取日期: 2026-10-28
所属知识域: 域6
---

# Temperature / Top-P / Top-K

Temperature：logit 除以 T 再 softmax。T→0 趋近贪心；T<1 分布变尖；T>1 变平。
Top-K：固定留前 K 个，不随分布形状变。
Top-P：按概率累加到 P 截断，确定问题时候选少、开放问题时候选多。

实战：一次主要调一个。精确任务 T=0~0.2；对话 T=0.5~0.7；创意 T=0.8~1.2。不要同时把 T 拉高又把 top_p 压得很低。
