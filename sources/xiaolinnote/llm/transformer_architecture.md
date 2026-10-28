---
来源站点: xiaolinnote.com（小林面试笔记）
原文链接: https://xiaolinnote.com/ai/llm/transformer_architecture.html
抓取日期: 2026-10-28
所属知识域: 域6
板块: Transformer架构
---

# Transformer 架构基本原理

## RNN 两致命缺陷

1. 顺序计算无法并行；2. 长距离梯度消失。

## Self-Attention

Q/K/V = X @ W_Q/K/V（同一输入三投影）。Attention = softmax(QK^T/√d_k) V。除以 √d_k 防止点积方差爆炸 → softmax one-hot → 梯度消失。

Multi-Head：多子空间捕捉不同关联。位置编码补顺序。FFN 引入非线性并储存事实知识。

## 三架构

| | Encoder-only | Decoder-only | Encoder-Decoder |
|--|--------------|--------------|-----------------|
| 代表 | BERT | GPT/Claude/Qwen | T5/BART |
| 掩码 | 双向 | 因果 | Enc双向+Dec单向+Cross |
| 目标 | MLM | 下一 token | 条件生成 |

**Decoder-only 胜出**：下一 token 目标统一；海量无标注自监督；规模涌现。
