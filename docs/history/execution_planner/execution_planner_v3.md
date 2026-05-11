# Execution Planner V3

## 1. 目标

`execution_planner_v3` 的目标不是直接实现 full DAG/CSE，而是先把系统推进到 **CSE-ready** 状态：

- planner 可以为 staged chain 提供稳定 key
- `evaluate_many()` 可以在 batch 内复用完全相同的 staged source
- `evaluate_many()` 可以在 batch 内复用完全相同的 staged chain 前缀
- batch reuse 不再只是 executor 内部的隐式缓存，而是 planner 的正式输出

V3 仍然保持克制：

- 不做通用 DAG 构建
- 不做跨 route 的激进共享
- 不做成本模型

## 2. 为什么需要 V3

到 `v2` 为止，planner 已经能把深层链式表达式压平成线性的 staged chain，例如：

- `rank(demean(ts_mean(close, 5)), pct=true)`

但在 batch 场景里，如果同时计算：

- `rank(demean(ts_mean(close, 5)), pct=true)`
- `zscore(demean(ts_mean(close, 5)))`

系统虽然语义已经正确，却仍然可能重复做这些工作：

1. 反复计算 `ts_mean(close, 5)`
2. 反复计算 `demean(ts_mean(close, 5))`

V3 的任务就是先把这类“完全相同 source / 完全相同 prefix”的复用正式化，为将来的 DAG/CSE 打下结构基础。

## 3. 新增能力

### 3.1 稳定表达式 key

planner 为 AST 提供稳定 canonical key：

- `expr_key(expr)`

这让相同的 source expression 即使来自不同根表达式，也能被稳定识别。

### 3.2 稳定 staged step key

planner 为 staged step 提供稳定 key：

- `staged_step_key(step)`

key 覆盖：

- `func_name`
- `group_col`
- `ascending`
- `pct`

### 3.3 稳定 staged chain key

planner 为整条 staged chain 提供稳定 key：

- `staged_chain_key(plan)`

当前 batch 复用主要依赖：

- source key
- prefix step key tuple

### 3.4 planner-side batch graph

V3 现在会显式生成 batch 级执行计划，而不只是让 executor 在运行时临时推断。新增结构：

- `BatchPlanningItem`
- `BatchExecutionPlan`
- `BatchStagedSourceNode`
- `BatchStagedPrefixNode`

这些结构把 batch 内的 staged source、staged prefix、依赖关系和消费者输出名都提升成 planner 的正式输出。

## 4. Batch 复用规则

当前只复用最保守、最安全的两类内容。

### 4.1 完全相同 source_expr

如果多个 staged 输出拥有相同 source：

- `ts_mean(close, 5)`

那么 batch 中只计算一次。

### 4.2 完全相同 chain prefix

如果多个 staged 输出共享相同前缀：

- `demean(ts_mean(close, 5))`

那么这个 prefix 只计算一次，后续输出继续基于它展开。

例如：

- `rank(demean(ts_mean(close, 5)), pct=true)`
- `zscore(demean(ts_mean(close, 5)))`

会共享：

1. `ts_mean(close, 5)`
2. `demean(ts_mean(close, 5))`

## 5. 当前实现位置

### planner

- [src/factor_engine/planner.py](../../../src/factor_engine/planner.py)

负责：

- 递归 staged chain 规划
- `expr_key`
- `staged_step_key`
- `staged_chain_key`
- `build_batch_plan()`
- `BatchExecutionPlan / BatchStagedSourceNode / BatchStagedPrefixNode`

### engine

- [src/factor_engine/engine.py](../../../src/factor_engine/engine.py)

负责：

- 在 `evaluate_many()` 中构建 `BatchPlanningItem`
- 先调用 planner 生成 `BatchExecutionPlan`
- 再把 batch plan 交给 executor 执行

### executor

- [src/factor_engine/executor.py](../../../src/factor_engine/executor.py)

负责：

- 按 planner 输出的 batch staged graph 执行
- materialize staged source / prefix
- 只在 batch 内复用完全相同的 staged source / prefix

## 6. 这还不是 full DAG/CSE

V3 明确不等于 DAG/CSE。它只是让系统具备 DAG/CSE 所需的几个前提：

1. 节点/前缀有稳定 identity
2. batch 执行已经可以复用最保守的一类共享前缀
3. planner 已经能显式输出 batch staged graph

它还没有做：

- 任意子图共享
- 跨 route 共享
- 拓扑图执行
- 成本驱动重排

## 7. 当前收益

V3 已经覆盖这类场景：

- 多个输出共享相同 ordered source
- 多个输出共享相同 cross/grouped staged 前缀

这让后续的 batch 深层链式调用不再只是“语义正确”，而是开始具备真实的中间阶段复用能力。

## 8. 什么时候再做 DAG/CSE

最自然的下一步不是立刻 full DAG，而是：

1. 先观察 benchmark 中 batch staged reuse 的收益
2. 再把共享粒度从“完整 source / 完整 prefix”扩展到“更通用的共享子图”
3. 最后才引入真正的 DAG/CSE 执行计划

## 9. 一句话总结

`execution_planner_v3` 的本质是：

> 先把 planner 和 batch executor 变成 CSE-ready，再为未来的 DAG/CSE 做最保守、最稳定的铺路。
