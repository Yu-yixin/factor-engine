# Execution Planner V1

## 1. 目标

`execution_planner_v1` 的目标不是引入一个通用 DAG 优化器，而是先把当前已经确认会出问题的链式调用模式正式纳入统一规划层：

- 让执行器先判断“该表达式应该怎么执行”，再决定是否直接编译
- 把“必须先物化中间结果”的链式组合变成显式计划，而不是散落在执行器里的临时判断
- 为后续的 stage 复用、公共子表达式复用和更细粒度 benchmark 打基础

V1 明确是一个保守版本：

- 不改变 DSL 语义
- 不改变 `FactorEngine.parse / validate / evaluate / evaluate_many` 的公开 API
- 不引入通用 DAG/CSE
- 不重写 rolling kernel

## 2. 背景问题

当前引擎里有两类链式调用：

1. Python 层分步链式  
   例：先 `evaluate_many([("rank", "ts_rank(close, 10)")])`，再 `evaluate("demean(rank)")`
2. DSL 内部嵌套链式  
   例：`demean(ts_rank(close, 10))`

这两类调用在语义上应该等价，但之前并不总是如此。问题根因是：

- 内层是 ordered time-series/window 表达式
- 外层是 cross-sectional 或 grouped cross-sectional 聚合
- 如果直接把整棵 AST 递归编成一个后端表达式，就会出现“窗口表达式再套窗口表达式”的执行语义偏差

已经被证实会出问题的典型模式：

- `demean(ts_rank(...))`
- `zscore(ts_rank(...))`
- `rank(ts_rank(...))`
- `group_demean(ts_rank(...), industry)`
- `group_zscore(ts_rank(...), industry)`
- `group_rank(ts_rank(...), industry)`

## 3. V1 的核心概念

### 3.1 Route

V1 不直接做复杂 stage DAG，而是先把根表达式规划到 4 条执行路线之一：

- `compiled`
  - 可以安全直接编译为一个 `pl.Expr`
- `segmented`
  - 依赖 executor-scoped helper columns，保持 AST 路径
- `staged`
  - 必须先物化中间结果，再做外层 cross/grouped 聚合
- `table`
  - 表级结果，例如 `fft(...)`

### 3.2 Staged Cross-Section Plan

对于命中 `staged` 的根表达式，planner 会生成一个结构化计划：

- 外层函数名
- 内层需要先物化的值表达式
- 是否需要 group 列
- `rank/group_rank` 的 `ascending/pct` 选项

V1 当前支持的 staged 外层函数：

- `demean`
- `zscore`
- `rank`
- `group_demean`
- `group_zscore`
- `group_rank`

## 4. 规划规则

### 4.1 直接编译

如果根表达式不含 segmented 窗口，且不命中 staged 规则，则走 `compiled`。

典型例子：

- `close - open`
- `abs(ts_mean(close, 5))`
- `where(volume > 0, close, open)`
- `rank(close, pct=true)`

### 4.2 保持 segmented AST 路径

如果表达式树里出现 segmented window family，则走 `segmented`。

原因：

- 需要 executor-scoped 的 helper columns
- 可能需要按 segment spec 构造和复用 prepared view

### 4.3 强制 staged materialization

如果根表达式属于 cross/grouped cross-sectional family，且其值参数本身需要 ordered time-series 执行，则走 `staged`。

当前判定规则可以概括为：

- 根函数在 `demean/zscore/rank/group_demean/group_zscore/group_rank`
- 其 value argument 的 `ExecutionProfile.needs_time_order == True`

这类表达式不会再被当成单个后端嵌套窗口表达式处理。

## 5. 执行模型

以 `demean(ts_rank(close, 10))` 为例，V1 的执行计划等价于：

### Stage 1

- 在 ordered prepared frame 上计算：
  - `__stage_value = ts_rank(close, 10)`

### Stage 2

- 基于 `__stage_value` 再计算：
  - `result = demean(__stage_value)`

然后恢复原始输入顺序。

`group_rank(ts_rank(close, 10), industry, pct=true)` 也是同样思路：

### Stage 1

- `__stage_value = ts_rank(close, 10)`

### Stage 2

- `result = group_rank(__stage_value, industry, pct=true)`

## 6. 当前代码落点

### 6.1 Planner 模块

V1 规划逻辑收敛在：

- [src/factor_engine/planner.py](../../../src/factor_engine/planner.py)

核心对象：

- `ExecutionPlanner`
- `ExecutionPlan`
- `StagedCrossSectionPlan`

### 6.2 Engine

`FactorEngine` 负责：

- 缓存 AST
- 缓存 `ValidationResult`
- 缓存 `ExecutionPlan`
- 仅对 `compiled` 路线缓存 `pl.Expr`

也就是说：

- `compiled` 表达式可以走 compiled cache
- `segmented` 和 `staged` 表达式只缓存 plan，不缓存编译结果

### 6.3 Executor

`Executor` 负责按 plan 执行：

- `compiled` -> 原有 compiled/no-time-order/ordered path
- `segmented` -> 原有 segmented path
- `staged` -> 新的显式两阶段执行

## 7. V1 保证的事情

V1 明确保证：

- `demean(ts_rank(...))` 与“先物化 `ts_rank` 再 `demean`”一致
- `zscore(ts_rank(...))` 与分步写法一致
- `rank(ts_rank(...))` 与分步写法一致
- grouped 对应版本与分步写法一致
- `evaluate_many()` 在 staged 场景下仍然保持 row-aligned 输出
- 现有 segmented 和 table 语义不变

## 8. V1 不做的事情

V1 明确不做：

- 任意深层表达式自动拆成通用多 stage DAG
- 跨根表达式公共子表达式识别
- 任意层级的 CSE/materialization reuse
- planner 级别的成本模型
- planner 级别的 benchmark 自动归因

## 9. 为什么这版值得先做

V1 的价值不在于“已经是最终优化器”，而在于：

- 把已经验证的链式语义风险从 executor 临时逻辑提升为正式规划层
- 给后续优化留出稳定扩展点
- 把 route 选择从“执行时顺手判断”变成“显式 plan 决策”

这能让后续工作更清晰地分三层推进：

1. planner 决定 route 和 materialization barrier
2. executor 只负责按 plan 执行
3. engine 负责 cache 和公共 API

## 10. 后续演进方向

如果后续要继续做“全面优化链式调用系统”，推荐顺序是：

1. 扩展 planner 的 stage 表达能力，而不是继续往 executor 里堆根函数特判
2. 把 `evaluate_many()` 提升到按 plan 合并 stage，而不是只按 compiled/no-time-order/time-ordered 分桶
3. 在 planner 层引入公共子表达式复用，但前提是 benchmark 能证明收益足够
4. 再考虑更通用的 DAG/CSE，而不是一步到位重写执行器

## 11. 一句话总结

`execution_planner_v1` 的本质是：

> 先把“哪些链式组合必须先物化”变成显式计划，再让执行器按计划执行，从架构上避免已知的嵌套窗口语义问题。
