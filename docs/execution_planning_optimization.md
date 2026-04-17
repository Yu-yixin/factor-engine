# 执行规划与批量执行专题

本文档是 Factor Engine 的执行规划专题说明，聚焦当前执行路径、批量执行机制、缓存复用与边界约束。历史方案讨论与阶段性决策演进请参见 [revolution.md](revolution.md)。

## 1. 文档职责

本文档只回答以下问题：

- 当前系统如何推导表达式的执行需求
- executor 如何按需求分流
- `evaluate_many()` 如何共享执行壳
- 当前编译缓存与执行规划如何配合
- 当前这套执行模型的边界在哪里

它不承担：

- 记录所有历史方案版本
- 维护完整项目使用说明
- 维护所有模块的总体设计说明

## 2. 背景

执行规划专题的核心问题是：

> 不同表达式对排序、分组和预处理的需求并不相同，系统不能继续用“单一重壳”执行所有列级表达式。

Factor Engine 当前已经从“所有列级表达式统一走 ordered path”的原型状态，演进到“按 AST 级执行需求分流”的结构。

## 3. 当前执行规划数据来源

### 3.1 FunctionSpec

函数级执行规划元信息由 `registry.py` 中的 `FunctionSpec` 提供。

当前与执行规划直接相关的字段包括：

- `result_kind`
- `backend`
- `execution_kind`
- `needs_code_group`
- `needs_time_group`
- `needs_time_order`

这些字段回答的是：

- 结果是列级还是表级
- 是否需要分发到特殊 backend
- 执行时是否依赖 `code` 分组
- 执行时是否依赖 `time` 分组
- 执行时是否依赖 `time` 排序

### 3.2 ExecutionProfile

`validator.py` 会对整棵 AST 递归推导 `ExecutionProfile`。

`ExecutionProfile` 的核心意义是：

- 表达式最终怎么执行，不只看根节点
- 调度对象是整棵 AST，而不是单个函数名

典型例子：

- `close` 是 pointwise
- `demean(close)` 需要 `time_group`
- `delay(close, 1)` 需要 `code_group + time_order`
- `delay(demean(close), 1)` 同时需要 `time_group + code_group + time_order`
- `where(volume > ts_mean(volume, 20), close, 0)` 虽然根节点是 `where`，但整棵树仍有时序需求

## 4. 当前执行路径

### 4.1 `row_aligned_no_time_order`

适用：

- pointwise 表达式
- cross-sectional 表达式
- 所有不需要 `time_order` 的列级表达式

执行方式：

- 直接在原始 DataFrame 上 `with_columns(...)`

典型表达式：

- `close`
- `open + close`
- `where(close > open, close, open)`
- `demean(close)`
- `rank(close)`
- `group_demean(close, industry)`
- `group_rank(close, industry, pct=true)`

### 4.2 `row_aligned_time_ordered`

适用：

- 需要 `code_group + time_order` 的时序表达式

执行方式：

1. 创建 `row_idx`
2. 构造 `sort([code, time])` 视图
3. 在排序视图上执行 `with_columns(...)`
4. 恢复到原始输入顺序

典型表达式：

- `delay(close, 1)`
- `delta(close, 1)`
- `pct_change(close, 1)`
- `ts_mean(close, 5)`
- `ts_rank(close, 20, pct=true)`
- `corr(close, volume, 5)`

### 4.3 `table`

适用：

- 表级表达式

当前典型表达式：

- `fft(close)`

执行方式：

- validator 先保证它满足 table 边界约束
- executor 再把它路由到对应 backend

## 5. `evaluate_many()` 的当前机制

`evaluate_many()` 的核心不是“列表接口”，而是“按执行画像分桶共享执行壳”。

当前执行过程可以概括为：

1. 对每个表达式 parse
2. validate 并推导 `ExecutionProfile`
3. 对相同表达式复用编译结果
4. 按 `needs_time_order` 分流到不同 bucket
5. 每个 bucket 共用一套执行壳
6. 所有结果列在合并前恢复到原始输入顺序

当前版本的输入契约：

- `list[tuple[str, str]]`
- 每个元素显式提供：
  - 输出列名
  - 表达式字符串

当前版本的输出契约：

- 只支持列级表达式
- 返回“原表 + 多个结果列”的单个 DataFrame

当前不支持：

- table expr 批量执行
- column expr + table expr 混合 batch
- 非行对齐结果的批量拼接

## 6. PreparedFrame 的当前定位

`PreparedFrame` 是 executor 内部的轻量预处理上下文。

当前只承载：

- 原始 DataFrame
- 带 `row_idx` 的排序视图
- 恢复原始顺序所需的信息
- 同一 executor 内按 segmented spec 复用的 prepared segmented views

当前设计刻意保持克制：

- 不暴露为公共 API
- 不承担通用查询计划系统职责
- 不承担 table backend 复用
- 不承担通用缓存中心职责

## 7. 编译缓存与执行规划的配合

当前 `FactorEngine` 维护实例级编译缓存，用于复用：

- AST
- `ValidationResult`
- compiled expression

缓存命中的收益主要发生在编译层，而不是执行结果层。

当前 cache key 绑定：

- `expression`
- schema fingerprint
- `time_col`
- `code_col`

这意味着：

- 相同表达式在同一 schema / 列上下文下可直接命中
- schema 变化会触发重新 validate / compile
- 当前不会跨数据版本复用执行结果

## 8. 当前已落地的执行规划收益

当前这套机制已经带来几类明确收益：

- pointwise 表达式不再无条件支付 ordered path 的排序成本
- cross-sectional 表达式不再被错误包进 `sort(code, time)` 重壳
- grouped cross-sectional expressions 继续停留在 no-time-order 路径，而不是被误判成时序路径
- `evaluate_many()` 可以共享执行壳与编译结果
- ordered time-series 表达式仍保持正确的顺序语义

## 9. 当前边界与非目标

当前明确保留的边界包括：

- mixed-profile AST 允许走“保守但合法”的路径，不追求每种情况都最优
- table expr 仍不能嵌入 column expr
- `PreparedFrame` 不是公共抽象
- grouped cross-sectional 当前只支持显式 `group_*` family，不回灌旧函数签名
- 当前缓存不做 DAG / CSE
- 当前缓存不做整列结果缓存
- 当前 `evaluate_many()` 不做 table path 批量执行
- 当前批量失败汇总位于 workflow helper 边界，不改变 `evaluate_many()` 的 fail-fast 语义

## 10. 当前热点与后续入口

基于当前实现，后续最值得继续观察的专题包括：

- 真实数据 benchmark 与阶段验收
- 编译缓存的可观测性与 clear cache 能力
- FFT 任意长度输入的高性能化
- `ts_rank` 是否真的成为热点，再决定是否继续优化
- 是否需要引入更进一步的 DAG / CSE

这些内容不应直接并入当前执行规划主模型，而应先通过 benchmark 决定投入顺序。

## 11. 一句话总结

当前执行规划体系的核心不是“做一个复杂优化器”，而是：

> 让系统先知道表达式真正需要什么执行上下文，再用最小必要的执行壳去完成它，并在批量场景下共享重复工作。

## 12. 参考文档

## R13.5 Segmented 规格键

R13.5 保持 segmented 执行继续沿用现有 AST 路径，但把预处理视图的键从单一 count 扩展为规范化的 segmented 规格键：

- 等分切分：`("equal", n)`
- 定长切分：`("length", (l1, l2, ...))`

当前规划规则如下：

- 单个表达式里仍然只能使用一种 segmented 规格
- `evaluate_many()` 可以混用不同 segmented 规格，但每种唯一规格都会拥有自己的预处理视图
- 允许同规格复用
- 这一阶段故意禁用跨规格复用，以便 benchmark 能量出真实的成本边界

这样既保持了当前执行模型稳定，也让第二种 segmented 规格的成本可以被独立观测，而不是隐式共享掉。

## R15 Grouped 与 Workflow 补充

R15 没有引入新的 execution kind，但对当前规划有两点补充：

- grouped cross-sectional：
  - `group_demean / group_zscore / group_rank` 仍归入 `row_aligned_no_time_order`
  - 它们需要的是 `[time, group_col]` 分组，而不是 `code + time_order`
- workflow report path：
  - 结构化失败汇总不在 execution core 内部完成
  - 它放在 `workflow.py` 中按表达式逐条执行并分类异常，从而保留 `evaluate_many()` 作为 strict、fail-fast 的核心接口

- [README.md](../README.md)
- [benchmark.md](benchmark.md)
- [documentation_policy.md](documentation_policy.md)
- [design.md](design.md)
- [revolution.md](revolution.md)

## Current planner state (V6)

The current execution planner is no longer just choosing between:

- compiled column execution
- segmented execution
- staged cross-sectional materialization
- table execution

It now also has a narrow materialized ordered route for one important failure class:

- `corr(...)`
- `cov(...)`

when one or both ordered inputs are themselves cross-sectional or grouped expressions.

### What is now safe

The current planner/executor combination now explicitly protects these composition directions:

- `cross/grouped over ordered`
  - examples:
    - `demean(ts_rank(close, 10))`
    - `rank(demean(ts_mean(close, 5)), pct=true)`
    - `group_rank(ts_rank(close, 10), industry, pct=true)`
- `ordered corr/cov over cross/grouped`
  - examples:
    - `corr(rank(open), rank(volume), 10)`
    - `cov(rank(open), rank(volume), 10)`

The protection mechanism is the same in both directions:

1. detect that direct nested-window compilation is not semantically safe
2. insert a materialization barrier
3. continue execution from real columns instead of from nested window expressions

### What is not yet generalized

V6 does **not** mean the engine now solves arbitrary nested window composition.

The following statement is still too broad:

- "any ordered root can safely consume any cross/grouped child expression"

That is not yet true.

The current protected surface is wider than the original V6 `corr/cov` fix.

Today the planner/executor combination explicitly protects:

- `rolling_single` over cross/grouped inputs:
  - `ts_mean`
  - `ts_std`
  - `ts_sum`
  - `ts_min`
  - `ts_max`
  - `ts_median`
  - `skew`
  - `kurt`
- `pair` over cross/grouped inputs:
  - `corr`
  - `cov`
- `positional` over cross/grouped inputs:
  - `argmax`
  - `argmin`
- `rank` over cross/grouped inputs:
  - `ts_rank`

What is still not true is the broader statement:

- "any ordered root can safely consume any cross/grouped child expression"

That remains too broad because segmented-child cases and future ordered roots still need explicit policy, tests, and route coverage.

### Current rule of thumb

The current system should be understood as:

- not a full DAG/CSE optimizer
- not a fully general nested-window planner
- but a planner that now owns a growing set of **materialization-boundary rules** for cross-domain window composition

This is why correctness work still comes before full graph reuse work:

- first define where direct composition is illegal
- then make those boundaries explicit in the execution plan
- only after that widen reuse and DAG/CSE safely

### Positional rolling implementation note

`argmax` / `argmin` now also have a distinct execution model from ordinary rolling statistics.

They are still ordered roots and still participate in `materialized_ordered` when they consume `cross` or `grouped` children, but their default hot-path kernel is no longer Python callback based and no longer uses phase-1 list-window expansion.

Current default implementation model:

1. sort once into the existing prepared `(code, time)` shell
2. materialize the child value expression once
3. scan each `code` group with a monotonic deque
4. return distance-to-current for the nearest maximum/minimum

This removes the previous `rolling_map(lambda ...)`, `concat_list`, and horizontal shifted-column expansion costs from root `argmax` / `argmin` execution.

The older pure-Polars expression implementations remain available as fallback/reference helpers for composed expression cases and regression checks, but `positional_ordered` and `materialized_ordered(argmax/argmin)` route to the dedicated kernel by default.
