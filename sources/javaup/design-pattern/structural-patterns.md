---
来源站点: javaup.chat（码力全开）
原文链接: https://javaup.chat/java/design-pattern/structural-patterns/
抓取日期: 2026-10-28
所属知识域: 域1 Java核心与编码工程化
板块: 设计模式-结构型
---

# 结构型设计模式应用

## 结构型模式概述

结构型模式关注类和对象的组合方式，使系统结构更清晰、灵活。本文覆盖代理、享元、不可变三种高频结构型模式。

## 代理模式

通过代理对象控制对原始对象的访问，可在访问过程中添加额外逻辑。

应用场景：
- 远程代理：Dubbo RPC，隐藏网络通信细节
- 动态代理：Spring AOP
- 缓存/日志/异常/权限代理

静态代理示例（缓存增强）：

```java
public class CachedUserServiceProxy implements UserService {
    private final UserService userService;
    private final Map<Long, UserInfo> userCache = new ConcurrentHashMap<>();

    public CachedUserServiceProxy(UserService userService) {
        this.userService = userService;
    }

    @Override
    public UserInfo getUserById(Long userId) {
        UserInfo cached = userCache.get(userId);
        if (cached != null) return cached;
        UserInfo user = userService.getUserById(userId);
        if (user != null) userCache.put(userId, user);
        return user;
    }
}
```

Spring AOP + 自定义 `@Cacheable` 注解可实现通用代理切面（Around 拦截 → 查缓存 → 未命中则 proceed → 回填）。

## 享元模式

通过共享技术支持大量细粒度对象复用。状态分两类：
- **内部状态**：可共享的不变状态
- **外部状态**：不可共享的变化状态（如坐标）

典型应用：String 常量池、IntegerCache（-128~127）、连接池、线程池。

```java
public class GraphicElementFactory {
    private static final Map<String, GraphicElement> elements = new HashMap<>();
    public static GraphicElement getTree(String treeType) {
        return elements.computeIfAbsent("tree_" + treeType, k -> createTree(treeType));
    }
}
```

**包装类作锁的陷阱**：`Long.valueOf(1)` 在缓存范围内返回同一对象，看似不同的锁可能互相阻塞。

## 不可变模式

通过禁止对象状态修改解决并发问题。设计规则：
1. 类 `final` 修饰
2. 所有属性 `final`
3. 无 setter
4. 对可变属性做防御性拷贝（入参与出参）

```java
public final class Transaction {
    private final String transactionId;
    private final BigDecimal amount;
    private final List<String> tags;

    public Transaction(..., List<String> tags) {
        this.tags = tags == null
            ? Collections.emptyList()
            : Collections.unmodifiableList(new ArrayList<>(tags));
    }

    public Transaction addTag(String newTag) {
        List<String> newTags = new ArrayList<>(this.tags);
        newTags.add(newTag);
        return new Transaction(..., newTags);  // 返回新对象
    }
}
```

注意：`final` 引用类型属性若指向可变对象，仍可被外部修改——必须深拷贝。

不可变 + 享元：对常用金额等值对象做缓存（`Money.of` + ConcurrentHashMap）。

## 结构型选型指南

| 模式 | 适用场景 | 核心价值 |
|------|----------|----------|
| 代理 | 控制访问、增强功能（缓存/日志/权限） | 解耦、AOP |
| 享元 | 大量相似对象、内存优化 | 对象复用 |
| 不可变 | 多线程值对象 | 天然线程安全 |

组合用法：不可变对象可被享元安全共享；代理可对享元做访问控制。
