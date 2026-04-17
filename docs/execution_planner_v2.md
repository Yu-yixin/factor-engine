# Execution Planner V2

## 1. 目标

`execution_planner_v2` 在 `v1` 的基础上继续前进一步，但仍然保持克制：

- 不引入通用 DAG/CSE
- 不重写 rolling kernel
- 不改变公开 API

V2 的核心目标是：

> 让 planner 不只会给根表达式选 route，还能把深层链式 cross/grouped-over-ordered 表达式拆成线性的 staged chain。

## 2. V1 还不够的地方

`v1` 只能处理“根表达式本身需要 staged”的场景，例如：

- `demean(ts_rank(...))`
- `group_rank(ts_rank(...), industry)`

但下面这种深层链式表达式，`v1` 仍然会留下中间层嵌套：

- `rank(demean(ts_mean(close, 5)), pct=true)`

这会导致：

- 结果可能只在浮点层面接近，但不完全等于手工分步
- 性能上也会多走一些重复的 nested compile/execute 路径

## 3. V2 的新增能力

V2 让 planner 能递归识别 staged root，并把它们压平成一条线性的 staged chain。

例如：

```text
rank(demean(ts_mean(close, 5)), pct=true)
```

在 V2 里会规划成：

### Stage 1

- `__stage_value = ts_mean(close, 5)`

### Stage 2

- `__stage_value_0 = demean(__stage_value)`

### Stage 3

- `result = rank(__stage_value_0, pct=true)`

也就是说，planner 现在能把：

- 根级 staged
- staged 套 staged
- grouped staged 套 staged

收敛成一个单一的线性 chain。

## 4. 当前支持的线性 staged chain

V2 当前支持的 staged step family 仍然是：

- `demean`
- `zscore`
- `rank`
- `group_demean`
- `group_zscore`
- `group_rank`

但与 V1 的区别在于：

- V1 只能识别“根节点 staged”
- V2 能把这些节点递归串起来

## 5. 计划数据结构

V2 把原先的单个 staged plan 提升成：

- `StagedCrossSectionStep`
  - 单一步骤
- `StagedChainPlan`
  - `source_expr`
  - `steps`

其中：

- `source_expr` 必须是需要先物化的源表达式
- `steps` 是一个顺序执行的 staged step 列表

## 6. 执行模型

执行器不再把 staged route 理解成“一个 staged 外层函数”，而是：

1. 先在 ordered prepared frame 上计算 `source_expr`
2. 再按 `steps` 顺序逐步生成中间列
3. 最后一步直接写入目标输出列
4. 恢复原始输入行顺序

这意味着：

- 深层链式表达式终于能和“手工拆步”严格对齐
- `evaluate_many()` 也能稳定承接这类 deep staged chain

## 7. 当前收益

V2 已经覆盖的关键场景包括：

- `rank(demean(ts_mean(close, 5)), pct=true)`
- `rank(demean(ts_rank(close, 10)), pct=true)`
- `group_rank(group_demean(ts_rank(...), industry), industry, pct=true)` 这类线性 staged chain

其中最直接的收益是：

- 嵌套写法与手工分步写法 `max_abs_diff = 0.0`
- 链式深层表达式不再依赖“偶然接近”的后端嵌套窗口语义

## 8. V2 仍然不做的事情

V2 仍然保持以下边界：

- 不做跨表达式公共子表达式复用
- 不做同一 batch 内的 DAG 级共享
- 不做成本模型
- 不对任意表达式树自动做最优 stage 切分

换句话说，V2 是：

- `planner v1` 的递归线性增强版
- 不是通用图优化器

## 9. 后续最合理的方向

如果后面还要继续推进，最自然的顺序是：

1. 让 `evaluate_many()` 在 planner 层合并相同 `source_expr`
2. 再考虑跨输出列共享 staged chain 的前缀
3. 最后才考虑 DAG/CSE

## 10. 一句话总结

`execution_planner_v2` 的本质是：

> 把“单层 staged”推进成“递归线性 staged chain”，让深层链式调用也能稳定等价于手工分步计算。
