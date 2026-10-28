---
来源站点: xiaolincoding.com（小林coding）
原文链接: https://xiaolincoding.com/interview/docker.html
抓取日期: 2026-10-28
所属知识域: 域4 工程交付与云原生
板块: Docker面试题
---

# Docker 面试题精要

## 隔离机制

- Namespace：PID/网络/挂载/IPC 等视图隔离
- cgroups：CPU/内存/IO 配额；v2 统一层次 + PSI 等增强

## 镜像分层

UnionFS/overlay2；指令一层；容器可写层 + CoW；共享底层、构建缓存、增量 pull。最佳实践：不变层（依赖）放可变层（源码）之前。

## 核心组件

镜像=类，容器=对象，仓库=分发中心。

## Dockerfile 高频指令

FROM/WORKDIR/COPY/RUN/ENV/ARG/EXPOSE/VOLUME/CMD/ENTRYPOINT/USER；Java 示例用 slim + jar。

## 与 VM

VM 虚拟化 OS；Docker 虚拟化进程（共享内核）。
