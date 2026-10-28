---
来源站点: javaup.chat（码力全开）
原文链接: https://javaup.chat/java/design-pattern/factory-pattern/
抓取日期: 2026-10-28
所属知识域: 域1 Java核心与编码工程化
板块: 设计模式-工厂
---

# 工厂模式体系详解

## 工厂模式核心理念

工厂模式的核心目标是**封装对象的创建过程**。对象的实例化由专门的工厂类负责，用工厂方法替代直接使用 `new`。

优势：
- 封装创建细节：客户端无需关心对象如何创建
- 集中管理：对象的生命周期可以统一管控
- 提升扩展性：新增产品类型时对现有代码影响最小
- 降低耦合度：客户端与具体产品类解耦

三种变体：简单工厂、工厂方法、抽象工厂——抽象程度逐步递增。

## 简单工厂模式

也称为静态工厂方法模式。通过一个工厂类的静态方法决定创建哪种具体产品。

```java
public class DocumentParserFactory {
    public static DocumentParser createParser(String type) {
        switch (type.toLowerCase()) {
            case "pdf": return new PdfParser();
            case "word": case "docx": return new WordParser();
            case "excel": case "xlsx": return new ExcelParser();
            case "md": case "markdown": return new MarkdownParser();
            default: throw new UnsupportedOperationException("不支持的文档类型: " + type);
        }
    }
}
```

优点：客户端与具体产品解耦，实现简单。  
缺点：新增产品需修改工厂类（违背 OCP）；工厂职责过重。

## 工厂方法模式

定义创建对象的接口，由子类决定实例化哪个具体类。每种产品对应一个工厂类，完全符合开闭原则。

```java
public interface ParserFactory {
    DocumentParser createParser();
}
public class PdfParserFactory implements ParserFactory {
    @Override public DocumentParser createParser() { return new PdfParser(); }
}
```

新增产品只需新增产品类+工厂类，无需改现有代码。  
缺点：类成对增加，理解成本上升。

## 抽象工厂模式

提供创建一系列相关或相互依赖对象的接口，无需指定具体类。关键概念是**产品族**。

```java
public interface UIFactory {
    Button createButton();
    TextField createTextField();
    Checkbox createCheckbox();
}
public class WindowsUIFactory implements UIFactory { /* 创建 Windows 风格全套组件 */ }
public class MacUIFactory implements UIFactory { /* 创建 macOS 风格全套组件 */ }
```

开闭原则倾斜性：
- 新增产品族：只加具体工厂 → 符合 OCP
- 新增产品等级（如再加 Slider）：需改所有工厂 → 违背 OCP

## 三种工厂对比与选型

| 特性 | 简单工厂 | 工厂方法 | 抽象工厂 |
|------|----------|----------|----------|
| 工厂数量 | 一个 | 多个 | 多个 |
| 产品类型 | 一类产品 | 一类产品 | 多类产品（产品族） |
| 扩展产品 | 修改工厂 | 添加工厂 | 添加工厂（族） |
| 开闭原则 | 不符合 | 符合 | 部分符合 |
| 复杂度 | 低 | 中 | 高 |

最佳实践：
1. 产品类型少且稳定 → 简单工厂
2. 产品类型经常变化 → 工厂方法
3. 存在产品族 → 抽象工厂
4. Spring 场景 → IoC 容器本身即工厂，优先用 Bean 注入而非手写工厂
