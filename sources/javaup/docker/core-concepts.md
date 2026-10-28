---
来源站点: javaup.chat（码力全开）
原文链接: https://javaup.chat/tools/docker/core-concepts/
抓取日期: 2026-10-28
所属知识域: 域4 工程交付与云原生
板块: Docker-核心概念
---

# Docker 容器技术核心概念

## 容器是什么

容器将应用及其运行时依赖封装为独立运行单元：代码+库、独立环境、与宿主及其他容器隔离、可在任意支持容器的平台运行。Docker 基于 Go，利用 Linux **Namespace**（视图隔离）与 **Cgroup**（资源限制）实现进程级隔离。

核心价值：环境一致性、秒级启动与高密度、一次构建到处运行、支撑微服务独立部署。

## 容器 vs 虚拟机

| 维度 | 虚拟机 | 容器 |
|------|--------|------|
| 启动 | 分钟级 | 秒/毫秒级 |
| 磁盘 | GB（完整 OS） | MB（应用+库） |
| 性能损耗 | 5%-15% | 接近原生 |
| 隔离 | OS 级，强 | 进程级，中等 |
| 单机规模 | 几十 | 数百上千 |

VM 适合强隔离/不同 OS；容器适合微服务、CI/CD、快速扩缩。可协同：VM 上跑容器。

## 三大组件

1. **镜像 Image**：只读模板，Union FS 分层 + Copy-on-Write；Dockerfile 每条指令一层。
2. **容器 Container**：镜像运行实例，只读层上叠加可写容器层；生命周期 run/pause/stop/rm。
3. **仓库 Registry**：Docker Hub / 云厂商 ACR / Harbor；命名 `registry/ns/repo:tag`。

## Namespace 与 Cgroup

| Namespace | 隔离内容 |
|-----------|----------|
| PID | 进程 ID |
| Network | 网络栈 |
| Mount | 挂载点 |
| UTS | 主机名 |
| IPC | 进程间通信 |
| User | 用户/组 |

Cgroup 限制 CPU/内存/磁盘 IO/网络带宽：`--cpus`、`--memory`、`--memory-swap`。

## 多阶段构建（Java）

```dockerfile
FROM maven:3.8-openjdk-17 AS builder
WORKDIR /build
COPY pom.xml . && COPY src ./src
RUN mvn package -DskipTests

FROM openjdk:17-jdk-slim
WORKDIR /app
COPY --from=builder /build/target/*.jar app.jar
RUN useradd -m appuser && USER appuser
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```
