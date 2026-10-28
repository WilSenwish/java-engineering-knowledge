---
来源站点: javaup.chat（码力全开）
原文链接: https://javaup.chat/architecture/microservice/deploy-strategy/
抓取日期: 2026-10-28
所属知识域: 域4 工程交付与云原生
板块: 微服务发布策略
---

# 微服务发布与部署策略

## 目标

降风险、用户无感、秒级回滚、自动化。三大策略：蓝绿、金丝雀/灰度、滚动。

## 蓝绿

双环境；闲置环境部署验证后切 Service selector（K8s `kubectl patch service`）。回滚秒级；代价双倍资源；DB schema 需双版本兼容。

## 金丝雀 / 灰度

小流量验证再放量。维度：机器比例、地域、用户等级、userId 取模。Istio VirtualService weight + DestinationRule subset。监控错误率超阈自动回滚。

应用层灰度示例：白名单/黑名单 + `userId % 100 < grayPercentage` 路由 v1/v2。

## 滚动（K8s 默认）

`RollingUpdate`：`maxSurge` / `maxUnavailable`；配合 readiness/liveness Probe。资源省；回滚相对慢（整集群逆向）。

## 基线与回滚

发布前记录：Git Commit、镜像 tag、配置快照、依赖版本 → 一键 `kubectl set image` + rollout status + 就绪副本校验。

## 选型

| 策略 | 资源 | 回滚 | 风险控制 | 场景 |
|------|------|------|----------|------|
| 蓝绿 | 高 | 秒级 | 高 | 核心交易 |
| 金丝雀 | 低~中 | 分钟 | 高 | 通用/C端 |
| 滚动 | 低 | 较慢 | 中 | 内部服务 |
| A/B | 中 | 快 | 高 | 需数据验证 |
