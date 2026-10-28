---
来源站点: OpenTelemetry 官方文档
原文链接: https://opentelemetry.io/docs/concepts/signals/ ；https://opentelemetry.io/docs/languages/java/instrumentation/
抓取日期: 2026-10-28
所属知识域: 域5
---

# OpenTelemetry 信号与 Java 埋点

信号：Traces、Metrics、Logs、Baggage；Profiles 仍在发展。

关联靠 trace context：span 用 parent/links；metric 用 exemplar；log 记录同一 trace context。入口 extract，出口 inject，线程间传递 Context。

Java 优先 Java agent（字节码，零代码）。其次 Spring Boot starter。日志桥接 Log4j/Logback，不要用 OTel Logger 替换 SLF4J。两条出日志路：OTLP 直发 Collector，或 stdout/文件再由 Fluent Bit 采集。
