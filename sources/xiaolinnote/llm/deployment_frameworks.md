---
来源站点: xiaolinnote.com
原文链接: https://xiaolinnote.com/ai/llm/deployment_frameworks.html
抓取日期: 2026-10-28
所属知识域: 域6
---

# 部署框架：vLLM · SGLang · TGI · llama.cpp

朴素 transformers 三痛点：KV 预分配碎片、static batch 短等长、共享前缀重复算。

- vLLM：PagedAttention（Block+Block Table，利用率 30%→90%+）+ Continuous Batching
- SGLang：RadixAttention 前缀树，Agent/多轮共享 System Prompt
- TGI：HF 生态与企业接口，极致吞吐通常不优先
- llama.cpp：C++ + GGUF，CPU/Mac/边缘
- TensorRT-LLM：NVIDIA 极致，要编译 engine

选型：高吞吐 API → vLLM；前缀重复 → SGLang；HF 集成 → TGI；无 GPU → llama.cpp。二者互补不替代。
