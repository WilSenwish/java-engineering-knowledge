---
来源站点: GitHub nageoffer/12306（浅克隆 depth=1）
原文链接: https://github.com/nageoffer/12306
走读日期: 2026-10-28
所属知识域: 域7 业务场景与实战案例
板块: 12306 源码级走读
---

# 12306 源码级走读

## 规模与模块

约 **414 个 Java 文件、约 3.0 万行**。双版本：`aggregation-service`（部署）与微服务（学习）。

| 模块 | Java 文件（约） | 职责 |
|------|-----------------|------|
| ticket-service | 135 | 余票、选座、锁座、令牌桶 |
| pay-service | 64 | 支付 |
| user-service | 49 | 注册/登录/乘车人 |
| order-service | 49 | 订单 |
| frameworks | 其余 | 幂等、雪花 ID、分片算法、缓存、责任链 |

包前缀：`org.opengoofy.index12306`。

## 购票主链（v2）

```
TicketServiceImpl#purchaseTicketsV2
 → 责任链 TRAIN_PURCHASE_TICKET_FILTER（非空/参数/重复购票）
 → TicketAvailabilityTokenBucket#takeTokenFromBucket（Lua 原子扣令牌）
 → 本地公平 ReentrantLock + Redisson FairLock（按 trainId+seatType）
 → executePurchaseTickets
   → TrainSeatTypeSelector#select（策略键 = 车型+席别）
     → AbstractTrainPurchaseTicketTemplate#executeResp
       → selectSeats（邻座 → 同车厢不邻座 → 跨车厢）
       → 非 binlog 模式：沿途区间 Hash 余票 -N
     → lockSeat：沿途每段座位状态改为 LOCKED
 → 落 TicketDO（UNPAID）+ 远程建单
```

**v1**：整列车一把 `RLock`，注释写明存在 4 个严重问题，生产路径以 v2 为准。

**幂等**：`@Idempotent` SPEL，key 含 `unique-name + username`，同用户并发下单直接提示「正在执行下单流程」。

## 区间扣减（源码事实）

`TrainStationServiceImpl#listTakeoutTrainStationRoute` 调用 `StationCalculateUtil.takeoutStation`，把「出发→到达」展开成途经的**每一段**（北京南-济南西、济南西-南京南、北京南-南京南…）。

两处同时按段扣：

1. **令牌桶 Lua** `ticket_availability_token_bucket.lua`：先检查各席别余量，不足则 `tokenIsNull` 且**不扣**；够则对 `along` 数组里每段 `HINCRBY -count`。
2. **座位行** `SeatServiceImpl#lockSeat`：对每个选中座位 × 每一段 `startStation/endStation` 把 `seatStatus` 更新为 `LOCKED`。取消走 `unlock` 回 `AVAILABLE`。

余票缓存另有开关 `ticket.availability.cache-update.type=binlog`：为 binlog 时购票路径不直接改 Hash，改由 Canal `TicketAvailabilityCacheUpdateHandler` 回写。

## 选座阶梯（一等座）

`TrainFirstClassPurchaseTicketHandler#selectSeats`（人数 < 5 且未指定座位）：

1. 车厢余票合计 < 人数 → 直接失败；
2. 逐车厢把可用座位铺成 `int[7][4]`（0 空闲）；
3. `SeatSelection.adjacent` 同行连续空位 → 命中即停；
4. 全车厢无邻座 → `SeatSelection.nonAdjacent` 同车厢凑够；
5. 仍不够 → 把多车厢空位拼起来（跨车厢）。

指定座位走 `findMatchSeats`：相对坐标平移匹配（`SEAT_Y_INT` A/C/D/F），匹配失败再降级填空位。策略键由 `TrainSeatTypeSelector#distributeSeats` 拼 `车型名+席别名`，商务/一等/二等各一个 Handler。

## 令牌桶为什么先于锁

`purchaseTicketsV2` 注释：余票缓存限流挡不住「缓存显示有票但锁内才发现没有」的击穿。Lua 在进锁前按**沿途全段**原子预扣；`tokenIsNull` 时单机 `synchronized` + Caffeine（10 分钟）触发一次 `tokenIsNullRefreshToken`，避免击穿时全体打 DB。

锁粒度从 v1「整列车」收到 v2「车次+席别」，且本地公平锁 + 分布式公平锁双层，减少跨实例惊群。

## 用户：读扩散与穿透

登录 `UserLoginServiceImpl#login`：含 `@` 查 `UserMail`，否则先查 `UserPhone`，都落到 **username** 再查 `User`。邮箱/手机是独立映射表，避免「登录维度不是分片键就扫全库」。

用户名是否占用 `hasUsername`：布隆 `userRegisterCachePenetrationBloomFilter` 先挡；命中再查 Redis Set `USER_REGISTER_REUSE_SHARDING + hashShardingIdx(username)`（注销可复用池）。注册成功：`bloom.add` + 从复用 Set 移除；用户名锁 `LOCK_USER_REGISTER`。

分库算法 `CustomDbHashModShardingAlgorithm`：`abs(hashCode) % shardingCount / tableShardingCount` 得到库后缀。

## 工程判断

1. 票不是「OD 一对一行」，座位状态按**区间段**存储，购票必须整段锁定，否则中间站超卖。
2. 缓存扣减与 DB 锁座是两条线：Lua 挡流量，`lockSeat` 才是一致性；binlog 模式把缓存回写从请求线程挪走。
3. 选座是策略 + 模板：席别差异在 Handler，扣缓存在模板 `executeResp`，锁座在 Selector。
4. v2 的公平锁按席别拆，一等座高峰不会堵住二等座。
5. 注册防穿透是「布隆 + 分片 Set」，不是只缓存 null。
