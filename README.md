# 因子表达式引擎

Factor Engine 是一个基于 Python + Polars 的因子表达式计算原型系统，用来把表达式字符串解析、校验并执行成 DataFrame 结果。

## What This Engine Is

这个引擎面向研究型工作流，重点解决三件事：

- 把 DSL 表达式解析成可执行内部表示
- 在执行前做语义校验
- 在 Polars DataFrame 上执行 pointwise、cross-sectional、time-series、segmented 和 table 表达式

`README` 只保留入口信息。完整语言语义、函数规则、工作流和错误系统已经拆到 `docs/` 下的专门文档。

## What You Can Do

- 写逐点表达式：`close - open`
- 写截面表达式：`demean(close)`、`group_rank(close, industry, pct=true)`
- 写时序表达式：`delta(close, 1)`、`ts_rank(close, 20, pct=true)`
- 写分段表达式：`seg_mean(close, 3)`、`seglen_sum(close, [3, 5, 2])`
- 写组合表达式：`where(not is_null(close), clip(ts_mean(close, 5), 0, 100), 0)`
- 跑单表达式或批量表达式
- 从 YAML / JSON 文件加载表达式批次并把结果写到 parquet / csv

## 安装

建议使用 Python `3.10+`。

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install polars pytest ruff
```

## Quick Example

```python
import polars as pl

from factor_engine.engine import FactorEngine

df = pl.DataFrame(
    {
        "time": [1, 2, 3],
        "code": ["A", "A", "A"],
        "close": [10.0, 20.0, 30.0],
        "open": [9.0, 18.0, 29.0],
    }
)

engine = FactorEngine()

single = engine.evaluate("delta(close, 1)", df)
batch = engine.evaluate_many(
    [
        ("spread", "close - open"),
        ("ts_rank_3", "ts_rank(close, 3, pct=true)"),
    ],
    df,
)

print(single)
print(batch)
```

组合表达式示例：

```text
where(not is_null(close), clip(ts_mean(close, 5), 0, 100), 0)
```

文件工作流示例入口：

```powershell
$env:PYTHONPATH="src"
py scripts/workflow/file_batch_workflow.py input.parquet expressions.yaml --output result.parquet
```

## Core Concepts

- `pointwise`
  - 逐行计算，不依赖分组排序
- `cross-sectional`
  - 按 `time` 分组
- `grouped cross-sectional`
  - 按 `[time, group_col]` 分组
- `time-series`
  - 按 `code` 分组、按 `time` 排序
- `segmented`
  - 仍走 time-series 路径，但把每个 `code` 序列切成段后再聚合
- `table`
  - 返回新表；当前是 `fft(...)`

## Public API

核心入口仍然是 `FactorEngine`：

- `parse(expression)`
- `validate(expression, df)`
- `evaluate(expression, df, output_name="result")`
- `evaluate_many(expressions, df)`

## Repository Map

- `src/factor_engine/`: core package and execution implementation.
- `tests/`: layered test suite; see [tests/README.md](tests/README.md).
- `examples/`: minimal usage examples only.
- `scripts/`: workflow, maintenance, and developer utilities; see [scripts/README.md](scripts/README.md).
- `benchmarks/`: benchmark scripts, curated reports, latest local runs, and archived snapshots; see [benchmarks/README.md](benchmarks/README.md).
- `docs/current/`: current truth source for architecture, invariants, repository rules, setup, and cleanup plans.
- `docs/history/`, `docs/benchmark/`, `docs/strategy/`, `docs/archive/`: historical context, benchmark methodology, future direction, and old references.
- `artifacts/`, `outputs/`, and `data/`: local generated artifacts, runtime outputs, and data boundaries. Large/generated files should not be committed.

New developers and AI coding agents should start with [docs/current/README.md](docs/current/README.md), then read [docs/current/architecture.md](docs/current/architecture.md) and [docs/current/invariants.md](docs/current/invariants.md) before changing behavior.

## Docs Navigation

- [docs/README.md](docs/README.md)
  - documentation topology and current/history split
- [docs/index.md](docs/index.md)
  - 文档总导航与阅读顺序
- [docs/current/README.md](docs/current/README.md)
  - 当前真相源与推荐阅读顺序
- [docs/language.md](docs/language.md)
  - DSL 语法、表达式类型、运算符优先级、逻辑与 null 规则
- [docs/functions.md](docs/functions.md)
  - 全量函数参考，包括 `ts_median`、`argmax / argmin`、`group_*`、`seglen_*`
- [docs/workflow.md](docs/workflow.md)
  - YAML / JSON 批量输入、严格模式、continue-on-error、结果写出
- [docs/errors.md](docs/errors.md)
  - 错误类型、错误阶段、失败载荷、批量报告格式
- [docs/design.md](docs/design.md)
  - 当前代码结构与模块边界
- [docs/execution_planning_optimization.md](docs/execution_planning_optimization.md)
  - 执行规划、批量执行与缓存复用
- [docs/history/execution_planner/execution_planner_v1.md](docs/history/execution_planner/execution_planner_v1.md)
  - `planner v1` 的 route 规划、staged materialization 规则与实现边界
- [docs/history/execution_planner/execution_planner_v2.md](docs/history/execution_planner/execution_planner_v2.md)
  - `planner v2` 的递归 staged chain、深层链式调用修复范围与后续扩展方向
- [docs/history/execution_planner/execution_planner_v3.md](docs/history/execution_planner/execution_planner_v3.md)
  - `planner v3` 的 CSE-ready key、batch staged source/prefix 复用，以及通往 DAG 的前置结构
- [docs/history/execution_planner/execution_planner_v4.md](docs/history/execution_planner/execution_planner_v4.md)
  - `planner v4` 的 staged node graph、output binding，以及更接近 DAG 的 batch 执行形态
- [docs/history/execution_planner/execution_planner_v5.md](docs/history/execution_planner/execution_planner_v5.md)
  - `planner v5` 的 ordered batch fusion：让 compiled ordered 输出和 staged graph 共用一个 prepared frame
- [docs/history/execution_planner/execution_planner_v6.md](docs/history/execution_planner/execution_planner_v6.md)
  - `planner v6` 的 ordered-over-cross 修复：让 `corr/cov` 先物化 cross/grouped 输入，再做 ordered rolling
- [docs/benchmark/benchmark.md](docs/benchmark/benchmark.md)
  - benchmark 口径与结果落点
- [docs/documentation_policy.md](docs/documentation_policy.md)
  - 文档治理与再次优化条件
- [docs/history/revolution.md](docs/history/revolution.md)
  - 演进记录与阶段性决策

## 开发与验证

运行全部测试：

```powershell
$env:PYTHONPATH="src"
py -m pytest
```

运行静态检查：

```powershell
.venv\Scripts\python -m ruff check
```

运行 demo：

```powershell
$env:PYTHONPATH="src"
py examples/demo.py
```

## 当前边界

- 当前不支持字符串字面量
- `evaluate_many()` 只接受列级表达式
- workflow 文件输入当前只支持固定 YAML / JSON schema
- 当前缓存只覆盖编译层，不覆盖整列执行结果
- 若表达式要用于下一期交易决策，通常应显式滞后，例如 `delay(signal, 1)`
