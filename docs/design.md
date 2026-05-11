# 因子表达式引擎当前设计

本文档只描述 Factor Engine 的当前设计与模块分工，不承担历史演进记录职责。系统的历史变更、阶段性决策与复杂度演进，请参见 [revolution.md](history/revolution.md)。

文档拆分后的单一来源约定是：

- 语言语义只写在 [language.md](language.md)
- 函数语义只写在 [functions.md](functions.md)
- workflow 行为只写在 [workflow.md](workflow.md)
- 错误格式只写在 [errors.md](errors.md)

`design.md` 只描述结构和责任边界，不重复规范级语义。

## 1. 文档职责

- `README.md`
  - 当前项目入口说明
  - 安装、使用、能力概览、文档导航
- `docs/language.md`
  - DSL 语法、运算符优先级、逻辑与 null 语义
- `docs/functions.md`
  - 完整函数参考与 edge case
- `docs/workflow.md`
  - 文件驱动批量工作流与结果写出
- `docs/errors.md`
  - 错误类型、错误阶段与失败载荷
- `docs/design.md`
  - 当前系统设计
  - 模块分工、核心抽象、扩展入口
- `docs/execution_planning_optimization.md`
  - 执行规划、批量执行与相关优化专题
- `docs/benchmark/benchmark.md`
  - benchmark 口径与性能记录落点
- `docs/documentation_policy.md`
  - 文档治理规则与再次优化条件
- `docs/history/revolution.md`
  - 历史演进记录与复杂度分析

## 2. 系统目标

Factor Engine 是一个基于 Python + Polars 的因子表达式计算原型系统，面向量化研究中的表达式解析、语义校验与 DataFrame 执行场景。

当前设计重点是：

- 让表达式系统具备清晰的内部表示
- 让语义校验与执行规划在结构上可分离
- 让列级与表级表达式共存，但边界明确
- 让新增函数可以通过统一的语义层接入，而不是散落在执行器中隐式扩张

## 3. 总体执行链路

系统的统一执行链路如下：

```text
expression string
-> Lexer
-> Token list
-> Parser
-> AST
-> Validator
-> ValidationResult / ExecutionProfile
-> Executor
-> Polars expression / DataFrame result
```

对于批量列级执行：

```text
list[(output_name, expression)]
-> parse / validate / execution-profile inference
-> by-profile execution routing
-> shared execution shell
-> merged output DataFrame
```

对于文件驱动工作流：

```text
expression batch file (.json / .yaml / .yml)
-> workflow loader
-> list[BatchExpression]
-> FactorEngine.evaluate_many(...) or per-expression report path
-> result DataFrame / BatchEvaluationReport
-> optional parquet / csv writer
```

## 4. 核心抽象

### 4.1 抽象语法树

AST 是表达式系统的核心内部表示，定义在 `src/factor_engine/ast_nodes.py`。

当前节点类型包括：

- `Expr`
- `NumberNode`
- `BooleanNode`
- `ListNode`
- `VariableNode`
- `UnaryOpNode`
- `BinaryOpNode`
- `CallNode`

设计目标：

- 结构清晰
- 易于递归校验
- 易于编译为 `polars.Expr`
- 易于为执行规划推导整棵 AST 的需求画像

### 4.2 函数规格

函数语义统一由 `src/factor_engine/registry.py` 中的 `FunctionSpec` 描述。

当前它负责表达：

- 参数个数
- 允许的命名参数
- 参数输入规则
- 结果形态：`column` / `table`
- 后端路由信息
- 对 `time` / `code` 上下文的依赖
- 执行规划元信息：
  - `execution_kind`
  - `needs_code_group`
  - `needs_time_group`
  - `needs_time_order`

`FunctionSpec` 的定位是“语义层”，用于连接解析器、校验器和执行器。

### 4.3 ValidationResult 与 ExecutionProfile

`validator.py` 在完成合法性校验后返回 `ValidationResult`。

当前它至少包含：

- `result_kind`
- `profile`
- `backend`

其中 `ExecutionProfile` 是 AST 级执行画像，用于描述整棵表达式树真正需要的执行上下文，而不是只看根节点函数名。

当前主要依赖的需求位包括：

- `needs_code_group`
- `needs_time_group`
- `needs_time_order`

这让 grouped cross-sectional expressions 与 time-series / segmented expressions 可以继续共用同一套画像推导，而不需要单独引入新的根级结果类型。

### 4.4 PreparedFrame

`PreparedFrame` 是 executor 内部的轻量预处理上下文。

当前它只服务于 ordered time-series 路径，负责：

- 保存原始 DataFrame
- 保存带 `row_idx` 的排序视图
- 在 ordered 执行后恢复原始输入顺序
- 按 segmented spec 复用 prepared segmented views

它不是公共 API，也不是通用调度框架。

### 4.5 FactorEngine

`FactorEngine` 是统一对外入口，定义在 `src/factor_engine/engine.py`。

当前公开能力包括：

- `parse()`
- `validate()`
- `evaluate()`
- `evaluate_many()`

同时它维护实例级编译缓存，用于复用：

- AST
- `ValidationResult`
- 已编译表达式

它本身仍保持轻量门面，不直接承担文件输入、结果写出或批量失败汇总职责；这些能力当前放在 `workflow.py`。

### 4.6 Workflow Helper

`src/factor_engine/workflow.py` 提供研究工作流层的辅助能力，而不改变 `FactorEngine` 公共 API 形状。

当前包括：

- `BatchExpression`
- `BatchEvaluationReport`
- `load_expression_file(path)`
- `evaluate_expression_file(path, df, engine=None)`
- `evaluate_expression_batch_report(expressions, df, engine=None)`
- `evaluate_expression_file_report(path, df, engine=None)`
- `write_result(df, path)`

其定位是：

- 负责 YAML / JSON 批量表达式文件加载
- 负责 parquet / csv 结果写出
- 负责 workflow 边界的错误分类和聚合
- 不侵入 parser / validator / executor 的原始异常语义

## 5. 当前执行模型

### 5.1 逐点计算

特点：

- 输出逐行对齐
- 不依赖 `code` 分组
- 不依赖 `time` 分组
- 不依赖 `time` 排序

当前典型表达式：

- `close`
- `open + close`
- `where(close > open, close, open)`

### 5.2 截面计算

特点：

- 输出逐行对齐
- 依赖 `time` 分组
- 不天然依赖 `code,time` 排序

当前典型表达式：

- `demean(x)`
- `zscore(x)`
- `rank(x, ...)`
- `group_demean(x, industry)`
- `group_zscore(x, industry)`
- `group_rank(x, industry, ...)`

### 5.3 时序计算

特点：

- 输出逐行对齐
- 依赖 `code` 分组
- 依赖 `time` 排序

当前典型表达式：

- `delay`
- `delta`
- `pct_change`
- `ts_min / ts_max / ts_mean / ts_sum / ts_std`
- `ts_count / ts_any / ts_all / ts_rank`
- `corr / cov / skew / kurt`

### 5.4 表级结果

特点：

- 返回新的结构化结果表
- 不与原表逐行对齐

当前典型表达式：

- `fft(x)`

## 6. 模块分工

### 6.1 `tokens.py`

- 定义 token 类型与词法单元结构

### 6.2 `lexer.py`

- 将字符串切分为 token 序列
- 识别数字、标识符、布尔值、括号、比较运算符、命名参数赋值符号
- 对非法字符与非法数字抛出词法错误

### 6.3 `parser.py`

- 使用递归下降解析器将 token 序列转换为 AST
- 处理括号表达式、函数调用、命名参数和运算符优先级

### 6.4 `registry.py`

- 维护 `FunctionSpec`
- 为校验器和执行器提供统一函数元信息

### 6.5 `validator.py`

- 校验变量、函数、参数个数、命名参数合法性
- 校验数值输入、布尔输入、列级 / 表级边界
- 产出 `ValidationResult` 与 AST 级 `ExecutionProfile`

### 6.6 `executor.py`

- 将 AST 编译为 `polars.Expr`
- 根据 `ExecutionProfile` 选择执行路径
- 负责列级表达式和表级表达式的实际执行

### 6.7 `fourier.py`

- 提供 FFT 后端
- 当前包含 radix-2 快路径与任意长度回退路径
- 为表级 `fft(...)` 提供执行支持

## 7. Current execution-planning boundary

The current design should be read as a planner-led execution system, not as a pure recursive compiler.

At the time of writing, planner-owned routes are:

- `compiled`
- `segmented`
- `staged`
- `materialized_ordered`
- `table`

### What `staged` means

`staged` is currently used for expressions where a cross-sectional or grouped root cannot safely consume an ordered child expression directly.

Typical examples:

- `demean(ts_rank(close, 10))`
- `rank(demean(ts_mean(close, 5)), pct=true)`

In these cases the planner lowers the expression into:

1. ordered source expression
2. one or more cross/grouped materialization steps

### What `materialized_ordered` means

`materialized_ordered` is currently a narrow route for:

- `corr`
- `cov`

when ordered rolling execution would otherwise consume cross/grouped child expressions directly.

Typical example:

- `corr(rank(open), rank(volume), 10)`

In these cases the planner lowers the expression into:

1. materialize the left input expression
2. materialize the right input expression
3. run ordered rolling `corr/cov` over those materialized columns

### What this design does not claim yet

The current design does **not** claim that arbitrary nested windows are solved in full generality.

What is solved today is narrower:

- a staged chain for `cross/grouped over ordered`
- a materialized ordered route for `corr/cov over cross/grouped`

That boundary is intentional. The repository is still choosing the next widening step from reproduced failures and benchmark evidence, rather than promoting every ordered root into a generalized graph route immediately.

### 6.8 `engine.py`

- 作为统一 API 门面
- 串联 parse / validate / execute
- 管理实例级编译缓存

### 6.9 `errors.py`

- 定义统一异常体系
- 当前分为底层表达式异常与 workflow 边界异常两层：
  - 表达式层：`LexerError / ParserError / ValidationError / ExecutionError`
  - workflow 层：`WorkflowError / WorkflowConfigError / WorkflowIOError`
- `ExpressionFailure` 用于批量工作流中的结构化失败摘要

### 6.10 `workflow.py`

- 加载表达式批次文件
- 提供严格执行与 failure-report 两条 workflow 路径
- 提供 parquet / csv 写出 helper

### 6.11 `tests/`

- 提供单元测试、路径选择测试、函数语义测试和基础 smoke 测试

### 6.12 `examples/`

- 提供示例脚本、benchmark 脚本和真实数据 smoke 脚本
- 当前也包含文件驱动批量工作流示例

## 7. 输入输出约定

### 7.1 输入

系统输入包括：

- 表达式字符串
- `polars.DataFrame`

时间序列与表级表达式通常要求数据表中存在：

- `time`
- `code`

以及一个或多个数值字段，例如：

- `open`
- `high`
- `low`
- `close`
- `volume`
- `ret_1d`

### 7.2 输出

当前输出分两类：

- 列级表达式：返回“原表 + 一列结果”或“原表 + 多列结果”
- 表级表达式：返回新的结构化结果表

默认输出列名为 `result`，批量接口由调用方显式指定输出列名。

workflow helper 额外支持：

- 从表达式文件读取 `expressions: [{name, expression}]`
- 将结果写出到 `.parquet` 或 `.csv`
- 在汇总模式下返回 `BatchEvaluationReport(result_df, successes, failures)`

## 8. 当前扩展方式

新增一个函数时，推荐遵循以下顺序：

1. 在 `registry.py` 增加 `FunctionSpec`
2. 在 `validator.py` 补输入类型与上下文约束
3. 在 `executor.py` 补编译或 backend 分发逻辑
4. 在 `tests/` 中补：
   - registry 元信息测试
   - validator 测试
   - executor 测试
   - engine 测试
5. 在 `README` 更新当前能力说明
6. 若属于系统级变更，在 `revolution.md` 追加记录

如果改动属于研究工作流层而不是 DSL / execution core，推荐顺序改为：

1. 在 `workflow.py` 设计 helper 入口与失败载荷
2. 如有必要，在 `errors.py` 增加 workflow 级异常
3. 在 `tests/workflow/test_workflow_*.py` 补文件 schema、错误汇总、写出行为测试
4. 在 `README` 和 `design` 更新当前工作流说明
5. 若属于系统级交付，再在 `revolution.md` 追加记录

## 9. 当前已知设计边界

- 暂不支持字符串字面量
- 时间窗口参数当前要求为非负整数字面量
- 表级表达式不能嵌入列级表达式
- `group_*` family 当前要求第二个参数是直接分组列引用
- workflow 文件输入当前只支持固定 schema，不支持 plain text 批次文件
- 当前编译缓存仅覆盖编译层，不覆盖整列结果
- 当前 FFT 后端仅对 2 的幂长度输入走 `O(n log n)` 快路径
- `ts_rank` 第一版优先保证语义正确，不承诺热路径最优性能
- 批量错误汇总当前位于 workflow helper 边界，不改变 `evaluate_many()` 的 fail-fast 语义

## 10. 参考文档

## 10.1 R13.5 当前补充

R13.5 以刻意克制的方式扩展了当前设计：

- AST 新增了 `ListNode`，但列表字面量仍不是通用结果类型。它只用于让 `seglen_mean(x, [l1, l2, ...])` 能把字面量长度规格传过解析与校验阶段。
- `PreparedFrame.segmented_views` 不再只用 `segment_count` 做键，而是改为使用不可变的 segmented 规格键：
  - `("equal", n)`
  - `("length", (l1, l2, ...))`
- 执行器保留了两套独立的 segment-id 构造器：
  - `_build_equal_segment_id_expr(...)`
  - `_build_length_segment_id_expr(...)`
- 按长度分段仍沿用同一条有序执行路径，以及同一套 `(code, segment_id)` 段内聚合再广播的模型。R13.5 没有引入新的执行框架。
- 在 R13.5 当时，基于长度的 PoC 被刻意限制在 `seglen_mean` 单函数上；这一冻结在 R15 之后已解除，`seglen_sum / seglen_count / seglen_any / seglen_all` 已沿同一路径接入。

## 10.2 R15 当前补充

R15 在当前设计上的直接落点有三类：

- grouped cross-sectional family：
  - 新增 `group_demean / group_zscore / group_rank`
  - 仍沿用截面执行模型，只是把分组键从 `time` 扩展为 `[time, group_col]`
- seglen family completion：
  - `seglen_sum / seglen_count / seglen_any / seglen_all` 与 `seglen_mean` 共用长度规格校验和 segmented prepared view
- workflow layer：
  - 文件加载、结果写出、错误分层与失败汇总全部落在 `workflow.py`
  - 这样保持 `FactorEngine` API 和底层表达式异常体系稳定，不把研究流程细节压进核心执行链路

- [README.md](../README.md)
- [benchmark.md](benchmark/benchmark.md)
- [documentation_policy.md](documentation_policy.md)
- [revolution.md](history/revolution.md)
- [execution_planning_optimization.md](execution_planning_optimization.md)
