---
来源站点: xiaolinnote.com
原文链接: https://xiaolinnote.com/ai/llm/position_encoding.html
抓取日期: 2026-10-28
所属知识域: 域6
---

# 位置编码：sin/cos · RoPE · ALiBi

Attention 位置盲。「我打你」与「你打我」分数可相同。不能用裸序号（数值炸、无法外推）。

| | sin/cos | RoPE | ALiBi |
|--|---------|------|-------|
| 类型 | 绝对 | 相对（旋转 Q/K） | 相对（分数加距离惩罚） |
| 注入 | 加到 embedding | 旋转 Q/K，点积只依赖 m-n | softmax 前 -m\|i-j\| |
| 外推 | 差，超训练长度断崖 | 强，配合 NTK/YaRN 仍需评测 | 线性外推好，表达力弱 |
| 采用 | 原版 Transformer | Llama/Qwen/DeepSeek | MPT/BLOOM |

RoPE 赢在相对位置 + 可扩展 + 兼容 KV Cache/Flash/GQA。外推：PI / NTK / YaRN，不是无成本无限加长。
