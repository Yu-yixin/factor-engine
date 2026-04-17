# DSL 语言说明

本文档是 Factor Engine DSL 的单一语义来源，负责描述表达式形状、运算符优先级、逻辑语义和通用 null 规则。函数级细节请看 [functions.md](functions.md)，工作流和错误系统请分别看 [workflow.md](workflow.md) 与 [errors.md](errors.md)。

## 1. 表达式类型

当前 DSL 支持以下表达式形状：

- 数值字面量：`1`、`3.14`
- 布尔字面量：`true`、`false`
- 变量引用：`close`、`volume`
- 一元运算：`+x`、`-x`、`not x`
- 二元运算：
  - 算术：`+`、`-`、`*`、`/`
  - 比较：`>`、`<`、`>=`、`<=`、`==`
  - 逻辑：`and`、`or`
- 函数调用：`ts_mean(close, 5)`
- 命名参数：`rank(close, ascending=false, pct=true)`
- 列表字面量：`[3, 5, 2]`

当前不支持：

- 字符串字面量
- 属性访问
- 点号链式调用

## 2. 结果类型

DSL 当前只有两种结果类型：

- 列级结果：返回与输入 DataFrame 同高、逐行对齐的列
- 表级结果：返回新的结果表

当前唯一表级函数是 `fft(x)`，而且只能作为根表达式出现。

## 3. 语法约束

### 3.1 变量与函数名

- 标识符由字母、数字和下划线组成
- 首字符必须是字母或下划线
- `true`、`false`、`and`、`or`、`not` 是保留关键字

### 3.2 命名参数

- 命名参数语法是 `name=value`
- 命名参数值本身仍然是表达式
- 某些函数会进一步要求命名参数必须是布尔字面量，例如 `ascending=false`

### 3.3 列表字面量

- 语法上允许写 `[expr1, expr2, ...]`
- 语义上当前只允许把列表字面量放在 `seglen_*` family 的第二个参数位置
- `seglen_*` 之外，列表字面量不能作为独立表达式或通用参数类型使用

## 4. 运算符优先级

当前解析器的优先级从高到低如下：

1. 括号与函数调用
2. 一元 `+`、一元 `-`
3. `*`、`/`
4. `+`、`-`
5. 比较：`>`、`<`、`>=`、`<=`、`==`
6. `not`
7. `and`
8. `or`

运算是按当前优先级自上而下组合的；括号总是优先生效。

### 4.1 优先级示例

```text
not a and b or c
```

会被解析为：

```text
((not a) and b) or c
```

```text
close > open and volume > 0
```

会被解析为：

```text
(close > open) and (volume > 0)
```

## 5. 逻辑语义

逻辑运算要求布尔输入：

- `not x`
- `a and b`
- `a or b`

当前执行器直接编译为 Polars 布尔表达式：

- `not` -> `~x`
- `and` -> `a & b`
- `or` -> `a | b`

因此逻辑运算采用三值逻辑。下面这张表给出当前环境下实际锁定的 null 行为：

| a | b | `a and b` | `a or b` | `not a` |
| --- | --- | --- | --- | --- |
| `true` | `true` | `true` | `true` | `false` |
| `true` | `false` | `false` | `true` | `false` |
| `true` | `null` | `null` | `true` | `false` |
| `false` | `true` | `false` | `true` | `true` |
| `false` | `false` | `false` | `false` | `true` |
| `false` | `null` | `false` | `null` | `true` |
| `null` | `true` | `null` | `true` | `null` |
| `null` | `false` | `false` | `null` | `null` |
| `null` | `null` | `null` | `null` | `null` |

### 5.1 逻辑优先级示例

```text
not is_null(close) and fill_null(flag, false)
```

等价于：

```text
(not is_null(close)) and fill_null(flag, false)
```

## 6. 通用 null 规则

### 6.1 运算符层

- 算术和比较运算沿用 Polars 表达式语义，`null` 不会被 DSL 额外改写
- 逻辑运算的 null 规则见上面的三值逻辑表

### 6.2 条件分支

`where(cond, a, b)` 虽然是函数，但它承担了语言级条件分支角色。当前语义是：

- `cond == true` 时返回 `a`
- `cond == false` 时返回 `b`
- `cond == null` 时也返回 `b`

### 6.3 显式 null 工具

与 null 直接相关的两个基础函数是：

- `is_null(x)`：检测空值
- `fill_null(x, v)`：替换空值

这两个函数的参数限制和返回语义属于函数级规则，详见 [functions.md](functions.md)。

## 7. 语言级边界

- rolling / segmented 窗口参数不是通用表达式；它们由对应函数单独约束
- 表级表达式不能嵌入列级表达式
- `evaluate_many()` 只接受列级表达式
- 当前没有字符串、枚举、对象或嵌套表结构的 DSL 表达能力

## 8. 最小示例

### 8.1 逻辑优先级

```text
not a and b or c
```

### 8.2 null 参与逻辑

```text
is_null(close) or fill_null(flag, false)
```

### 8.3 组合表达式

```text
not is_null(close) and ts_mean(close, 5) > 10
```
