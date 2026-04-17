# 错误系统说明

本文档描述当前错误类型、错误阶段、结构化失败载荷和批量失败摘要格式。表达式语义和工作流路径请分别看 [language.md](language.md)、[functions.md](functions.md) 和 [workflow.md](workflow.md)。

## 1. 错误分层

当前错误系统分两层：

- 表达式核心层
- workflow 边界层

它们共享一个共同基类：`FactorEngineError`。

## 2. 错误类型

### 2.1 共同基类

- `FactorEngineError`

### 2.2 表达式核心层

- `LexerError`
  - 词法切分失败
- `ParserError`
  - 语法解析失败
- `ValidationError`
  - 语义校验失败
- `ExecutionError`
  - 执行期失败

`ValidationError` 当前还包含这些子类：

- `UnknownVariableError`
- `UnknownFunctionError`
- `ArgumentError`
- `UnsupportedOperatorError`

### 2.3 Workflow 边界层

- `WorkflowError`
  - workflow 相关错误的共同基类
- `WorkflowConfigError`
  - 文件格式、schema、输出格式等配置问题
- `WorkflowIOError`
  - 文件读写失败

## 3. 错误阶段

workflow report 路径会把异常分类成 `stage` 字段。当前映射如下：

| stage | 典型异常 |
| --- | --- |
| `io` | `WorkflowIOError` |
| `config` | `WorkflowConfigError` |
| `lexer` | `LexerError` |
| `parser` | `ParserError` |
| `validation` | `ValidationError` 及其子类 |
| `execution` | `ExecutionError` |
| `unknown` | 未命中以上分类的异常 |

## 4. 结构化失败载荷

批量汇总模式使用 `ExpressionFailure` 表示单条失败：

```python
ExpressionFailure(
    name: str | None,
    expression: str | None,
    stage: str,
    error_type: str,
    message: str,
)
```

字段说明：

- `name`
  - 表达式名；如果失败发生在文件读取前或 schema 层，可能是 `None`
- `expression`
  - 原始表达式文本；文件级失败时可能是 `None`
- `stage`
  - 分类后的错误阶段
- `error_type`
  - Python 异常类名，例如 `ParserError`
- `message`
  - 原始错误消息文本

## 5. 批量失败摘要格式

`evaluate_expression_batch_report(...)` 和 `evaluate_expression_file_report(...)` 返回：

```python
BatchEvaluationReport(
    result_df: pl.DataFrame,
    successes: list[BatchExpression],
    failures: list[ExpressionFailure],
)
```

它还提供：

```python
report.has_failures
```

### 5.1 语义

- `result_df`
  - 只包含成功表达式产出的结果列
- `successes`
  - 成功的 `BatchExpression` 列表
- `failures`
  - 失败的 `ExpressionFailure` 列表

## 6. 单条错误示例

### 6.1 语法错误

输入表达式：

```text
close +
```

在汇总模式下会形成一条失败记录，典型字段如下：

```python
ExpressionFailure(
    name="bad_syntax",
    expression="close +",
    stage="parser",
    error_type="ParserError",
    message="..."
)
```

### 6.2 校验错误

输入表达式：

```text
unknown + 1
```

典型字段如下：

```python
ExpressionFailure(
    name="bad_validation",
    expression="unknown + 1",
    stage="validation",
    error_type="UnknownVariableError",
    message="Unknown variable: unknown"
)
```

## 7. 批量报告示例

假设批次里有三条表达式：

- `spread = close - open`
- `bad = unknown + 1`
- `lagged = delay(close, 1)`

汇总模式下会得到：

- `successes = ["spread", "lagged"]`
- `failures = ["bad"]`
- `result_df` 只包含：
  - 原表列
  - `spread`
  - `lagged`

失败项的典型载荷如下：

```python
ExpressionFailure(
    name="bad",
    expression="unknown + 1",
    stage="validation",
    error_type="UnknownVariableError",
    message="Unknown variable: unknown"
)
```

## 8. 文件级失败示例

如果表达式文件本身是坏的，例如：

```yaml
expressions:
  spread: close - open
```

那么 `evaluate_expression_file_report(...)` 不会抛异常，而是返回：

- `result_df = 原始输入 df`
- `successes = []`
- `failures = [一条 config 失败]`

典型失败项：

```python
ExpressionFailure(
    name=None,
    expression=None,
    stage="config",
    error_type="WorkflowConfigError",
    message="Expression file '...' must contain 'expressions' as a list"
)
```

## 9. 当前边界

- 结构化失败摘要当前只存在于 workflow helper 路径
- `FactorEngine.evaluate_many()` 仍保持 strict、fail-fast 行为
- 当前没有单独的 error code 枚举；稳定字段是 `stage` 与 `error_type`
