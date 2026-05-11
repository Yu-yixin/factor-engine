# 算子添加指南

本文档定义 Factor Engine 当前可以接受什么类型的新算子、暂时不能接受什么类型的新算子，以及新增算子的标准工程流程。

**维护要求：每次系统能力升级后都必须更新本文档。**  
例如 planner route、DAG/CSE、lifecycle、native kernel、materialization discipline、M4 structural optimization 的边界发生变化时，都要同步更新这里的“可接受范围 / 禁止范围 / 流程 / 测试门槛”。

## 1. 当前系统能力基线

当前系统已经具备：

- registry 驱动的函数语义描述：`src/factor_engine/registry.py`
- validator 参数、列、窗口、特殊规则校验：`src/factor_engine/validator.py`
- physical properties / operator contract：`src/factor_engine/physical_properties.py`
- planner route：compiled / staged / materialized_ordered / positional_ordered / segmented / table
- DAG identity、有限 CSE、executor-native reuse
- non-native node-store lifecycle active drop
- helper column lifecycle first-wave 与 pure nested second-wave
- M3 materialization discipline 已收束
- M4 已 frozen：保留 accepted CSE expansion 与 unary-chain fusion，不继续扩结构优化候选

这意味着：新增算子必须优先落在现有 registry / validator / planner / executor 边界内。不能为了一个算子顺手扩大 M2/M3/M4 已冻结能力。

## 2. 当前可以接受的算子类型

### 2.1 低风险：pointwise column 算子

可以接受。

条件：

- 输入和输出都是列级结果
- 不改变行数
- 不改变输入行顺序
- 不需要 time/code 排序
- 不需要新增 planner route
- 可以用 Polars expression 在 `_compile_call()` 下实现
- 语义可由现有 `FunctionSpec` 字段表达

典型形态：

```text
f(x)
f(x, scalar)
f(condition, x, y)
```

示例同类：

- `abs`
- `clip`
- `sign`
- `where`
- `fill_null`
- `is_null`

### 2.2 中低风险：cross-sectional 算子

可以接受，但必须显式声明 group 语义。

条件：

- 输出仍然逐行对齐
- 分组语义能落在当前 code/group 模型中
- 不需要跨时间窗口
- 不需要改变 frame 高度
- 可用现有 executor group/rank/zscore/demean 类路径实现

示例同类：

- `rank`
- `demean`
- `zscore`
- `group_rank`
- `group_demean`
- `group_zscore`

要求：

- `execution_kind="cross_sectional"`
- 如依赖 code/group，需要设置对应 `needs_code_group` 或显式 group 参数校验
- 必须有结果顺序恢复测试

### 2.3 中风险：普通 rolling time-series 算子

可以接受，但必须通过 ordered audit。

条件：

- 以 `code` 分组、`time` 升序
- 只看当前行和历史行，不看未来
- window 参数是正整数 literal
- 输出逐行对齐
- 可用现有 rolling 编译路径实现
- 不需要新增 native kernel
- 不需要新增 lifecycle 行为

示例同类：

- `delay`
- `delta`
- `pct_change`
- `ts_min`
- `ts_max`
- `ts_median`
- `ts_mean`
- `ts_sum`
- `ts_std`
- `ts_count`
- `ts_any`
- `ts_all`
- `ts_rank`

要求：

- `execution_kind="time_series"`
- `window_kind="rolling"`
- `requires_time_col=True`
- `requires_code_col=True`
- `needs_code_group=True`
- `needs_time_order=True`
- `requires_partition_by=("$code",)`
- `requires_order_by=("$time",)`
- 如果作为 ordered root 支持 materialized child，必须更新 ordered audit 矩阵与测试

### 2.4 中高风险：positional ordered 算子

只接受与现有 positional 模型完全同构的算子。

条件：

- 单输入或现有 positional pair 模型可以表达
- window 是正整数 literal
- 语义是 code/time 有序窗口内的位置型计算
- 可以复用现有 native positional bridge 或已有 Python fallback
- 不新增 native buffer lifecycle 语义
- 不新增未审计 route

示例同类：

- `argmax`
- `argmin`
- `corr`
- `cov`

要求：

- `window_kind="positional"`
- ordered audit 必须通过
- native / fallback 结果一致性必须测试
- full route correctness 必须覆盖：
  - direct column input
  - materialized child input
  - grouped/cross-sectional child input，如 `argmax(rank(close), 2)`
  - unsupported segmented child 必须明确 fail 或被审计支持

### 2.5 中高风险：segmented time-series 算子

谨慎接受，只接受现有 segmented/seglen family 模式内的新成员。

条件：

- segment 长度语义能由当前 validator 表达
- 不改变行数
- segment coverage、边界、错误行为可测试
- 不需要新增 route

示例同类：

- `seg_mean`
- `seg_sum`
- `seg_count`
- `seg_any`
- `seg_all`
- `seglen_mean`
- `seglen_sum`
- `seglen_count`
- `seglen_any`
- `seglen_all`

要求：

- `window_kind="segmented"`
- segment 参数校验必须覆盖非法长度、覆盖不足、超界等场景

### 2.6 表级 root-only 算子

原则上不作为普通新增算子接受。

当前只有非常窄的已知形态，例如 `fft`。如果要新增 table result 算子，必须先写设计文档并明确：

- 是否 root-only
- 返回 schema
- 是否改变行数
- workflow 输出行为
- batch failure 行为
- 是否能与 evaluate_many 共存

没有设计和端到端测试，不接受 table 级新算子。

## 3. 当前不能接受的算子类型

以下类型当前不接受，除非先进入单独设计阶段：

### 3.1 需要修改 DSL 语义的算子

不接受。

包括：

- 新语法
- 新字面量类型
- 新运算符优先级
- 新变量解析规则
- 改变现有 null / boolean / comparison 规则

### 3.2 改变行数或行顺序的列级算子

不接受。

列级算子必须保持与输入 DataFrame 同高、逐行对齐。任何 explode、join、resample、聚合成更短表、生成多行结果的能力都不属于当前普通算子添加范围。

### 3.3 需要新增 execution route 的算子

不接受作为普通算子添加。

如果一个算子无法落到现有 compiled / staged / materialized_ordered / positional_ordered / segmented / table route 中，必须先做 planner 设计，不允许在 executor 中硬塞临时路径。

### 3.4 需要改变 M2 lifecycle 的算子

不接受。

M2 已冻结。新算子不能要求：

- 扩 first-wave node-store drop
- 扩 second-wave helper drop
- native-heavy active drop
- 新的 working-frame drop 语义
- allocator / GC 级释放

### 3.5 需要继续扩 M4 结构优化的算子

不接受。

M4 已 frozen。新算子不能借机要求：

- 新 CSE family
- 新 fusion family
- wide-fanout batching
- heavy-path rewrite
- structural materialization elimination

除非明确开启新的 M4+ cycle，并重新走 proposal -> executable -> benchmark -> score -> freeze 流程。

### 3.6 native-heavy 新算子

默认不接受。

如果算子需要新的 native kernel、native buffer 生命周期、或新的 compiled fallback-heavy path，必须先做独立 native design / probe。不能直接作为普通算子进入 registry。

### 3.7 外部状态或非确定性算子

不接受。

包括：

- 依赖当前时间
- 依赖随机数且没有显式 seed 和稳定语义
- 依赖外部网络、文件、数据库
- 依赖全局 mutable state

Factor Engine 的表达式必须可复现、可缓存、可审计。

## 4. 新增算子的标准流程

### Step 0：先分类

新增前必须先把算子归类到以下之一：

```text
pointwise
cross_sectional
rolling time_series
positional ordered
segmented time_series
table root-only
unsupported / requires design
```

如果无法分类，默认视为 `unsupported / requires design`。

### Step 1：写语义说明

先在 PR / 设计记录里写清：

- 函数名
- 参数列表
- 参数类型
- 是否允许 kwargs
- null 行为
- tie-break 行为，如 rank / argmax 类
- window 边界行为
- 分组和排序要求
- 返回类型
- 是否保持行数
- 是否 root-only

这一步没写清，不进入代码实现。

### Step 2：更新 registry

在 `src/factor_engine/registry.py` 中添加 `FunctionSpec`。

必须选择正确字段：

- `min_args`
- `max_args`
- `allowed_kwargs`
- `result_kind`
- `root_only`
- `arg_rule`
- `backend`
- `requires_time_col`
- `requires_code_col`
- `numeric_arg_positions`
- `boolean_arg_positions`
- `execution_kind`
- `window_kind`
- `needs_code_group`
- `needs_time_group`
- `needs_time_order`
- `requires_partition_by`
- `requires_order_by`
- `requires_segment`
- `produces_*`
- `accepts_materialized_input`
- `is_single_input_ordered_root`

如果无法用这些字段表达该算子，停止。先扩设计，不要硬加。

### Step 3：更新 validator

确认 `src/factor_engine/validator.py` 可以正确校验：

- 参数个数
- kwargs
- required columns
- variable-only 参数
- numeric 参数
- boolean 参数
- window 参数
- segmented 参数
- 特殊语义，如 `where` / `fft` / `fill_null` / `is_null`

如果需要新增特殊校验，必须加单元测试。

### Step 4：更新 physical contract

确认 `build_operator_contract()` 能得到正确 properties。

必须明确：

- 该算子 requires 什么 partition/order/segment
- 该算子 produces 什么 properties
- materialization 是否会清空 properties
- 是否接受 materialized input
- 是否是 single-input ordered root

新增 ordered 算子时，这一步是硬门槛。

### Step 5：实现 executor

优先在 `src/factor_engine/executor.py` 的 `_compile_call()` 下实现。

原则：

- 能用 Polars expression 就不要加 route
- 能复用已有 helper 就不要新增执行通道
- 不要在 executor 中偷偷改变 planner 决策
- 错误必须抛 `ExecutionError` 或现有错误类型
- 直接列输入和嵌套表达式输入都要考虑

如果需要专门 route，例如 positional/native/table，必须先确认该 route 已存在且算子完全同构。

### Step 6：更新 planner / ordered audit

如果算子是 ordered root 或会影响 ordered composition，必须更新：

- `docs/ordered_roots_matrix.md`
- `docs/ordered_boundary_rules.md`
- `docs/ordered_correctness_audit.md`
- `tests/integration/test_ordered_audit.py`

并回答：

- direct column input 是否支持
- pointwise child 是否支持
- cross-sectional child 是否支持
- materialized child 是否支持
- segmented child 是否支持
- 当前 route 是 compiled、materialized_ordered、positional_ordered，还是 blocked

ordered audit 不完整，不接受新增 ordered 算子。

### Step 7：检查 DAG/CSE/lifecycle 边界

新增算子会进入 DAG identity。必须确认：

- `FunctionSpec.execution_kind` 和 `window_kind` 会进入 route-sensitive identity
- 不会误触发 M4 CSE expansion selected family
- 不会误触发 unary-chain fusion selected family
- repeated cheap node 是否仍 inline
- repeated expensive ordered/window node 是否按当前 materialization policy 处理
- lifecycle 不需要新增 drop class

如果该算子需要新的 CSE/fusion/lifecycle family，停止。那不是普通算子添加，是新阶段设计。

### Step 8：补测试

最低测试集：

1. registry 测试  
   文件：`tests/unit/test_registry_new_functions.py`

2. validator 测试  
   覆盖参数数量、非法 kwargs、类型错误、缺少 time/code/group 列。

3. executor 语义测试  
   文件按类别放入 `tests/integration/test_executor*.py` 或新增专门测试。

4. FactorEngine 端到端测试  
   至少覆盖 `evaluate()`；如果可用于 batch，则覆盖 `evaluate_many()`。

5. null / edge case 测试  
   包括空窗口、窗口不足、null 输入、tie-break、boolean 行为等。

6. ordered audit 测试  
   仅 ordered 算子需要，但需要就必须完整。

7. DAG/CSE smoke  
   repeated expensive 算子至少确认不会破坏 existing CSE/lifecycle profiling。

### Step 9：补文档

必须更新：

- `docs/functions.md`
- 本文档：`docs/operator_addition_guide.md`，如果新增算子扩大了系统能力边界

如果改变 planner / ordered / lifecycle / M4 边界，还必须更新对应 architecture 文档。

### Step 10：跑验收命令

最低验收：

```powershell
.venv\Scripts\python.exe -m ruff check src tests examples
.venv\Scripts\python.exe -m pytest -q
```

ordered / native / performance-sensitive 算子还必须跑对应 benchmark 或 probe，并把结果落到 `benchmarks/`。

## 5. 接受判定表

| 算子类型 | 当前是否接受 | 前提 |
| --- | --- | --- |
| pointwise column | 接受 | 不改行数、不改 route、Polars expression 可实现 |
| cross-sectional | 接受 | group 语义明确，结果逐行对齐 |
| ordinary rolling time-series | 接受 | 通过 ordered audit，不新增 route/native/lifecycle |
| positional ordered | 谨慎接受 | 与现有 positional 模型同构，native/fallback 一致性测试完整 |
| segmented time-series | 谨慎接受 | 落在现有 segmented family，边界测试完整 |
| table root-only | 默认不接受 | 需单独设计和端到端 schema/workflow 测试 |
| native-heavy 新算子 | 不接受 | 需先做 native design/probe |
| 改 DSL 语义 | 不接受 | 需独立语言设计 |
| 改 frame 高度或顺序 | 不接受 | 不属于当前列级算子模型 |
| 需要新 route | 不接受 | 先做 planner 设计 |
| 需要扩 lifecycle | 不接受 | M2 frozen |
| 需要扩 M4 structural optimization | 不接受 | M4 frozen，需新 M4+ cycle |

## 6. 最小 PR 清单

新增一个普通可接受算子时，PR 至少包含：

- `src/factor_engine/registry.py`
- `src/factor_engine/executor.py`
- 必要时 `src/factor_engine/validator.py`
- 必要时 `src/factor_engine/planner.py`
- `tests/unit/test_registry_new_functions.py`
- executor / engine 语义测试
- `docs/functions.md`
- 如能力边界变化，更新 `docs/operator_addition_guide.md`

ordered 算子还必须包含：

- ordered audit 文档更新
- `tests/integration/test_ordered_audit.py`
- planner route inspection 测试
- direct / nested / materialized child 结果一致性测试

## 7. 后续能力升级时必须更新本文档

以下任一变化发生时，必须更新本文档：

- 新 execution route 被正式接受
- 新 native kernel family 被接受
- native-heavy lifecycle 从 observable 进入 active drop
- M2 lifecycle freeze 边界变化
- M3 materialization discipline 重新打开
- M4 或 M4+ structural optimization 重新打开
- DAG/CSE selected family 扩大
- unary-chain fusion selected family 扩大
- table result 能力扩大
- DSL 语义扩大

更新时必须同步修改：

- “当前系统能力基线”
- “当前可以接受的算子类型”
- “当前不能接受的算子类型”
- “新增算子的标准流程”
- “接受判定表”

本文档是新增算子的入口门槛。没有在这里被允许的算子，默认不能作为普通算子添加。
   