---
来源站点: Thanos 设计文档
原文链接: https://thanos.io/tip/thanos/design.md
抓取日期: 2026-10-28
所属知识域: 域5
---

# Thanos：Prometheus 长期存储

组件解耦，统一 Store API（gRPC）：

- Sidecar：挂在 Prometheus 旁，上传 TSDB block（ULID 目录：chunks/index/meta.json，meta 带 external labels）到对象存储
- Store：按时间范围和标签过滤 block，只缓存 index，chunk 按需从对象存储读
- Querier：无状态，对 Store API 做 PromQL，可水平扩展
- Compactor：单例，合并 block、降采样、保留策略；不进查询集群
- Rule：在存储引擎上跑记录/告警规则

不在组件内做通用分片；容量靠对象存储。本地 Prometheus 保留可从数周缩到数小时。
