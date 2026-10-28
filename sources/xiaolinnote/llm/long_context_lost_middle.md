---
来源站点: xiaolinnote.com
原文链接: https://xiaolinnote.com/ai/llm/23_long_context_lost_middle.html
抓取日期: 2026-10-28
所属知识域: 域6
---

# Lost in the Middle

三个长度：训练时见过的长度、接口窗口上限、业务有效长度。窗口只回答「装不装得下」。

现象：证据在开头和结尾更容易被用到，放中间正确率掉（U 形）。不只是 RoPE：训练分布、注意力被干扰稀释、跨段推理更难。

代价：稠密注意力约 O(n²)，KV Cache 与 prefill、token 费用一起涨；多塞资料会引入冲突。

做法：先检索重排；必须全局时分层摘要并保留 chunk id；约束与问题不要埋在中间。评测要改长度、证据位置和干扰量，不能只做大海捞针。
