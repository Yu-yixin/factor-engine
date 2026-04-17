# 工作流说明

本文档描述文件驱动批量工作流、结果写出和 continue-on-error 路径。DSL 语义与函数语义请看 [language.md](language.md) 和 [functions.md](functions.md)，错误载荷格式请看 [errors.md](errors.md)。

## 1. 目标

工作流 helper 的定位是：

- 从文件加载表达式批次
- 把表达式批次送入 `FactorEngine`
- 输出 parquet / csv 结果
- 在需要时返回结构化失败摘要

这些能力都在 `src/factor_engine/workflow.py` 中实现，不改变 `FactorEngine` 的核心 API 形状。

## 2. 当前 helper

### 2.1 严格模式

- `load_expression_file(path)`
- `evaluate_expression_file(path, df, engine=None)`
- `write_result(df, path)`

### 2.2 汇总模式

- `evaluate_expression_batch_report(expressions, df, engine=None)`
- `evaluate_expression_file_report(path, df, engine=None)`

## 3. 文件输入格式

### 3.1 支持的文件类型

- `.json`
- `.yaml`
- `.yml`

当前不支持：

- plain text 批次文件
- 自定义 schema 版本字段
- 运行参数与表达式定义混写

### 3.2 固定 schema

当前 v1 schema 只有一种：

```yaml
expressions:
  - name: spread
    expression: close - open
  - name: ts_rank_20
    expression: ts_rank(close, 20, pct=true)
```

JSON 等价写法：

```json
{
  "expressions": [
    {"name": "spread", "expression": "close - open"},
    {"name": "ts_rank_20", "expression": "ts_rank(close, 20, pct=true)"}
  ]
}
```

### 3.3 schema 规则

- 顶层必须是 mapping / object
- 顶层必须包含 `expressions`
- `expressions` 必须是 list
- 每个元素必须是 `{name, expression}` 形式的 mapping
- `name` 必须是非空字符串
- `expression` 必须是非空字符串
- 同一文件中 `name` 不能重复

## 4. 严格模式

### 4.1 `load_expression_file(path)`

- 作用：只做读取和 schema 校验
- 返回：`list[BatchExpression]`
- 失败时：
  - 文件读不到 -> `WorkflowIOError`
  - JSON/YAML/schema 不合法 -> `WorkflowConfigError`

### 4.2 `evaluate_expression_file(path, df, engine=None)`

- 作用：读取文件后直接调用 `FactorEngine.evaluate_many(...)`
- 返回：单个结果 DataFrame
- 行为：
  - 走严格模式
  - 任一表达式失败时，整个调用中止并抛出异常
  - 成功时返回“原表 + 多个结果列”

### 4.3 严格模式示例

```python
import polars as pl

from factor_engine.workflow import evaluate_expression_file

df = pl.read_parquet("input.parquet")
result = evaluate_expression_file("expressions.yaml", df)
print(result)
```

## 5. 汇总模式

### 5.1 `evaluate_expression_batch_report(expressions, df, engine=None)`

- 作用：对内存中的 `BatchExpression` 列表逐条执行并汇总成功/失败
- 返回：`BatchEvaluationReport`

### 5.2 `evaluate_expression_file_report(path, df, engine=None)`

- 作用：从文件读取表达式后，走汇总模式执行
- 返回：`BatchEvaluationReport`

### 5.3 汇总模式行为

- 成功表达式会继续追加到 `result_df`
- 失败表达式不会阻塞后续表达式继续执行
- 每条失败都会生成一个 `ExpressionFailure`
- 文件读取失败或 schema 失败时，也会返回一个带失败条目的 `BatchEvaluationReport`

### 5.4 continue-on-error 示例

```python
import polars as pl

from factor_engine.workflow import evaluate_expression_file_report

df = pl.read_parquet("input.parquet")
report = evaluate_expression_file_report("expressions.yaml", df)

print(report.result_df)
for failure in report.failures:
    print(failure.stage, failure.error_type, failure.name, failure.message)
```

## 6. 结果写出

### 6.1 `write_result(df, path)`

- 作用：按文件后缀写出结果
- 当前支持：
  - `.parquet`
  - `.csv`

### 6.2 规则

- 保留传入 DataFrame 的全部列
- 不做列筛选
- 不做额外压缩/分区配置
- 后缀不支持时抛出 `WorkflowConfigError`
- 写出失败时抛出 `WorkflowIOError`

### 6.3 写出示例

```python
from factor_engine.workflow import write_result

write_result(result_df, "result.parquet")
write_result(result_df, "result.csv")
```

## 7. 端到端示例

### 7.1 YAML 文件

```yaml
expressions:
  - name: spread
    expression: close - open
  - name: safe_signal
    expression: where(not is_null(close), clip(ts_mean(close, 5), 0, 100), 0)
  - name: industry_rank
    expression: group_rank(close, industry, pct=true)
```

### 7.2 Python 调用

```python
import polars as pl

from factor_engine.workflow import evaluate_expression_file, write_result

df = pl.read_parquet("input.parquet")
result = evaluate_expression_file("expressions.yaml", df)
write_result(result, "result.parquet")
```

## 8. CLI 示例

仓库当前提供示例脚本 [examples/file_batch_workflow.py](../examples/file_batch_workflow.py)。

### 8.1 严格模式

```powershell
$env:PYTHONPATH="src"
py examples/file_batch_workflow.py input.parquet expressions.yaml --output result.parquet
```

### 8.2 continue-on-error

```powershell
$env:PYTHONPATH="src"
py examples/file_batch_workflow.py input.parquet expressions.yaml --continue-on-error --output result.csv
```

脚本在 `--continue-on-error` 模式下会：

- 调用 `evaluate_expression_file_report(...)`
- 打印每条失败的 `stage / error_type / name / expression / message`
- 仍然把成功表达式组成的结果表输出到目标文件

## 9. 当前边界

- YAML loader 当前是受限 schema 解析器，不是通用 YAML 解析器
- `evaluate_expression_file(...)` 仍然继承 `evaluate_many()` 的列级限制，不接受表级表达式批量执行
- report 模式是工作流层行为，不改变 `FactorEngine.evaluate_many()` 的 fail-fast 语义
