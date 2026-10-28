---
来源站点: GitHub nageoffer/shortlink（浅克隆 depth=1）
原文链接: https://github.com/nageoffer/shortlink
走读日期: 2026-10-28
所属知识域: 域7
板块: Link 源码级走读
---

# Link SaaS 短链源码走读

规模：约 188 个 Java 文件。模块：project（跳转与创建，98）、admin（83）、gateway（4）、aggregation（3）。

## 创建

`ShortLinkServiceImpl#createShortLink`：
1. 白名单校验 originUrl（演示环境防滥用）
2. `generateSuffix`：originUrl + UUID → MurmurHash32 → Base62；布隆已存在则重试，超过 10 次失败
3. 插入 `ShortLinkDO`（分片键 gid）+ `ShortLinkGotoDO`（按 fullShortUrl 路由，跳转时先查路由表拿 gid）
4. Redis 预热 `GOTO_SHORT_LINK_KEY`，TTL 跟随有效期
5. 布隆 `add(fullShortUrl)`

冲突：`DuplicateKeyException` 时若布隆没有该 key 则补写（布隆与 DB 不一致的修复），再抛重复。

`createShortLinkByLock`：全局 Redisson 锁 + DB 查重，注释明确「布隆远胜分布式锁」才是主路径。

## 跳转 `restoreUrl`

1. Redis 命中 → 异步统计 → `sendRedirect`（302）
2. 布隆不含 → 404，不打 DB
3. 空值缓存 `GOTO_IS_NULL` 命中 → 404
4. 锁内双检 → 查 Goto 表拿 gid → 按 gid+fullShortUrl 查短链 → 过期/禁用写 30 分钟空值缓存
5. 回填 Redis 再跳转

统计：Cookie uv + Redis Set 去重 uip，经 RocketMQ `ShortLinkStatsSaveProducer` 异步落库，跳转线程不等统计。

## 判断

- 跳转分片键不是短码本身：Goto 表把 fullShortUrl 映射到 gid，避免跳转时不知道分组就扫全库。
- 创建用布隆挡重复，跳转用布隆挡穿透，空值缓存挡「布隆误判打到不存在的 key」。
- 布隆不能删：注销/删除短链后注释指向「如何从布隆删除」这一已知限制。
