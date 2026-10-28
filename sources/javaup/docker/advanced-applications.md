---
来源站点: javaup.chat（码力全开）
原文链接: https://javaup.chat/tools/docker/advanced-applications/
抓取日期: 2026-10-28
所属知识域: 域4 工程交付与云原生
板块: Docker-Dockerfile/Compose/K8s入门
---

# Dockerfile 镜像构建与容器编排

## Dockerfile 关键指令

FROM / LABEL / ENV / WORKDIR / COPY(优于 ADD) / RUN / EXPOSE / CMD+ENTRYPOINT / USER / VOLUME / ARG / HEALTHCHECK

最佳实践：合并 RUN 减层；先 COPY 依赖文件再 COPY 源码以吃缓存；`.dockerignore`；优先 alpine/distroless；非 root USER。

## Docker Compose

`services` + `networks` + `volumes`；`depends_on`、`healthcheck`、`deploy.resources`、前后端分离网络（backend internal）。

常用：`up -d` / `down -v` / `logs -f` / `exec` / `--scale api=3` / `build --no-cache`

## 何时上 Kubernetes

Compose 局限：单机、弱自愈、手动扩缩、负载与服务发现弱。

K8s 最小三件套：
- **Pod**：最小调度单元
- **Deployment**：副本与滚动更新（resources requests/limits）
- **Service**：稳定访问入口（ClusterIP/LoadBalancer）

| | Compose | K8s |
|--|---------|-----|
| 规模 | 单机/小 | 大规模 |
| 自愈 | 弱 | 强 |
| 伸缩 | 手动 | HPA |
| 滚动更新 | 脚本 | 原生 |
| 场景 | 开发/小型 | 生产微服务 |
