# 函数参考

本文档是 Factor Engine 的完整函数语义参考。它覆盖 `registry.py` 中当前注册的全部函数。DSL 语法和运算符规则请看 [language.md](language.md)，工作流与错误系统请看 [workflow.md](workflow.md) 和 [errors.md](errors.md)。

Experimental branch note:

- This branch documents an experimental `ema()` path for isolated evaluation.
- `ema()` and MACD-shaped compositions are not accepted as stable-master DSL commitments.

## 1. 函数总览

### 1.1 条件与 null

- `where`
- `is_null`
- `fill_null`

### 1.2 标量数学

- `abs`
- `clip`
- `sign`

### 1.3 截面

- `demean`
- `zscore`
- `rank`
- `group_demean`
- `group_zscore`
- `group_rank`

### 1.4 时间序列

- `delay`
- `delta`
- `ema`
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
- `argmax`
- `argmin`
- `corr`
- `cov`
- `skew`
- `kurt`

### 1.5 分段时间范围

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

### 1.6 表级

- `fft`

## 2. 通用约定

### 2.1 列级 vs 表级

- 除 `fft` 外，本文档中的函数都返回列级结果
- 列级结果始终与输入 DataFrame 同高、逐行对齐

### 2.2 时间序列约定

所有 time-series 与 segmented family 都遵守这组基础规则：

- 先按 `code` 分组
- 再按 `time` 升序处理
- 只使用当前行及其历史行，不使用未来行
- 最终返回结果会恢复到原始输入顺序

### 2.3 布尔窗口约定

以下函数把布尔窗口中的 `null` 当成 `false`：

- `ts_count`
- `ts_any`
- `ts_all`
- `seg_count`
- `seg_any`
- `seg_all`
- `seglen_count`
- `seglen_any`
- `seglen_all`

## 3. 条件与 null

### `where(cond, a, b)`

- 定义：条件分支函数
- 参数：
  - `cond`：布尔表达式
  - `a`：条件成立时返回的值
  - `b`：条件不成立时返回的值
- 返回类型：列级；返回值类型由 `a / b` 决定
- 语义规则：
  - `cond == true` 时返回 `a`
  - `cond == false` 时返回 `b`
  - `cond == null` 时也返回 `b`
- 边界情况：
  - 参数个数必须正好是 3
- 最小示例：
  - `where(volume > 0, ret_1d, 0)`

### `is_null(x)`

- 定义：检查 `x` 是否为空
- 参数：
  - `x`：任意列级表达式
- 返回类型：布尔列
- 语义规则：
  - 非空返回 `false`
  - 空值返回 `true`
- 边界情况：
  - 参数个数必须正好是 1
- 最小示例：
  - `is_null(close)`

### `fill_null(x, v)`

- 定义：用 `v` 替换 `x` 中的空值
- 参数：
  - `x`：数值或布尔表达式
  - `v`：与 `x` 同类的 fill 值
- 返回类型：与 `x` 同类的列
- 语义规则：
  - 只替换 `x` 中的 `null`
  - 非空值保持原样
- 边界情况：
  - 参数个数必须正好是 2
  - 当前只支持数值路径和布尔路径
  - `x` 与 `v` 必须共享同一大类类型
- 最小示例：
  - `fill_null(close, 0)`
  - `fill_null(flag, false)`

## 4. 标量数学

### `abs(x)`

- 定义：绝对值
- 参数：
  - `x`：数值表达式
- 返回类型：数值列
- 语义规则：
  - 返回 `|x|`
- 边界情况：
  - `null` 保持 `null`
  - 参数个数必须正好是 1
- 最小示例：
  - `abs(delta(close, 1))`

### `clip(x, lower, upper)`

- 定义：把 `x` 约束到闭区间 `[lower, upper]`
- 参数：
  - `x`：数值表达式
  - `lower`：下界表达式
  - `upper`：上界表达式
- 返回类型：数值列
- 语义规则：
  - `x < lower` 时返回 `lower`
  - `x > upper` 时返回 `upper`
  - 否则返回 `x`
- 边界情况：
  - 参数个数必须正好是 3
  - `lower / upper` 不要求是字面量，可以是数值表达式
  - `null` 输入保持 `null`
- 最小示例：
  - `clip(ts_mean(close, 5), 0, 100)`

### `sign(x)`

- 定义：符号函数
- 参数：
  - `x`：数值表达式
- 返回类型：数值列
- 语义规则：
  - `x < 0` -> `-1.0`
  - `x == 0` -> `0.0`
  - `x > 0` -> `1.0`
- 边界情况：
  - `null` 保持 `null`
  - 参数个数必须正好是 1
- 最小示例：
  - `sign(close - open)`

## 5. 截面函数

### `demean(x)`

- 定义：按时间截面去均值
- 参数：
  - `x`：数值表达式
- 返回类型：数值列
- 语义规则：
  - 对每个 `time` 分组计算 `x - mean(x)`
- 边界情况：
  - 需要 `time` 列
  - 参数个数必须正好是 1
- 最小示例：
  - `demean(close)`

### `zscore(x)`

- 定义：按时间截面标准化
- 参数：
  - `x`：数值表达式
- 返回类型：数值列
- 语义规则：
  - 对每个 `time` 分组计算 `(x - mean(x)) / std(x)`
- 边界情况：
  - 需要 `time` 列
  - 参数个数必须正好是 1
  - 当前没有额外的零标准差保护；结果直接遵循当前除法语义
- 最小示例：
  - `zscore(ret_1d)`

### `rank(x, ascending=false, pct=false)`

- 定义：按时间截面对 `x` 排名
- 参数：
  - `x`：数值表达式
  - `ascending`：是否升序，默认 `false`
  - `pct`：是否返回百分位，默认 `false`
- 返回类型：数值列
- 语义规则：
  - 默认按降序排名，值越大排名越靠前
  - `pct=true` 时返回 `rank / 分组长度`
  - 当前实现调用 Polars `rank()`，未暴露 tie-handling 配置；在当前测试环境里 ties 采用 average 结果
- 边界情况：
  - 需要 `time` 列
  - 参数个数必须正好是 1
  - `ascending` 和 `pct` 必须是布尔字面量
- 最小示例：
  - `rank(close, ascending=false, pct=true)`

### `group_demean(x, group)`

- 定义：在同一时间切片内按分组列去均值
- 参数：
  - `x`：数值表达式
  - `group`：直接分组列引用
- 返回类型：数值列
- 语义规则：
  - 对每个 `[time, group]` 分组计算 `x - mean(x)`
  - 分组只发生在同一时间切片内部，不跨时间聚合
- 边界情况：
  - 需要 `time` 列
  - 第二个参数必须是直接列引用，不能是派生表达式
  - `group == null` 的行会形成独立 bucket，而不是自动丢弃
- 最小示例：
  - `group_demean(close, industry)`

### `group_zscore(x, group)`

- 定义：在同一时间切片内按分组列做 z-score
- 参数：
  - `x`：数值表达式
  - `group`：直接分组列引用
- 返回类型：数值列
- 语义规则：
  - 对每个 `[time, group]` 分组计算 `(x - mean(x)) / std(x)`
- 边界情况：
  - 需要 `time` 列
  - 第二个参数必须是直接列引用
  - 单元素组或零标准差组没有额外保护，结果遵循当前标准差/除法语义
  - `group == null` 仍然是独立 bucket
- 最小示例：
  - `group_zscore(ret_1d, industry)`

### `group_rank(x, group, ascending=false, pct=false)`

- 定义：在同一时间切片内按分组列排名
- 参数：
  - `x`：数值表达式
  - `group`：直接分组列引用
  - `ascending`：是否升序，默认 `false`
  - `pct`：是否返回百分位，默认 `false`
- 返回类型：数值列
- 语义规则：
  - 分组键是 `[time, group]`
  - `pct=true` 时返回 `rank / 分组长度`
  - 当前实现调用 Polars `rank()`，未暴露 tie-handling 配置；在当前测试环境里 ties 采用 average 结果
- 边界情况：
  - 需要 `time` 列
  - 第二个参数必须是直接列引用
  - `group == null` 的行在自己的 null bucket 内排名
- 最小示例：
  - `group_rank(close, industry, ascending=false, pct=true)`

## 6. 时间序列函数

### `delay(x, n)`

- 定义：返回 `x` 的历史滞后值
- 参数：
  - `x`：任意列级表达式
  - `n`：非负整数字面量
- 返回类型：与 `x` 同类的列
- 语义规则：
  - 对每个 `code` 独立做 `shift(n)`
- 边界情况：
  - 需要 `time` 和 `code` 列
  - 前 `n` 行没有足够历史时返回 `null`
- 最小示例：
  - `delay(close, 1)`

### `delta(x, n)`

- 定义：差分
- 参数：
  - `x`：数值表达式
  - `n`：非负整数字面量
- 返回类型：数值列
- 语义规则：
  - 精确定义为 `x - delay(x, n)`
- 边界情况：
  - 需要 `time` 和 `code` 列
  - 历史不足时返回 `null`
- 最小示例：
  - `delta(close, 1)`

### `pct_change(x, n)`

- 定义：相对变化率
- 参数：
  - `x`：数值表达式
  - `n`：非负整数字面量
- 返回类型：数值列
- 语义规则：
  - 精确定义为 `x / delay(x, n) - 1`
- 边界情况：
  - 需要 `time` 和 `code` 列
  - 历史不足时返回 `null`
  - 若 `delay(x, n) == 0`，当前结果会返回 `inf`
- 最小示例：
  - `pct_change(close, 1)`

### `ema(x, span)`

Experimental status:

- Available on `feature/ema-macd-experiment` for isolated evaluation only.
- Not a stable-master contract.

- 定义：指数移动平均，语义固定为 `pandas.Series.ewm(span=span, adjust=False).mean()`
- 参数：
  - `x`：数值表达式
  - `span`：正整数字面量
- 返回类型：数值列
- 语义规则：
  - `alpha = 2 / (span + 1)`
  - 对每个 `code` 独立按 `time` 升序递推
  - 第一条非空输入成为 EMA 初始状态
  - 后续非空输入按 `ema[t] = alpha * x[t] + (1 - alpha) * ema[t-1]` 更新
  - 输入为 `null` 时遵循 pandas `adjust=False` 默认行为：输出延续上一条 EMA，下一条非空输入仍按绝对位置衰减后的权重更新
- 边界情况：
  - 需要 `time` 和 `code` 列
  - `span` 必须大于 0，且必须是整数字面量
  - EMA 是 ordered recursive operator，不是 rolling-window operator
  - `ema(x, span)` 不等价于 `ts_mean(x, span)`
- 最小示例：
  - `ema(close, 12)`
  - `ema(close, 12) - ema(close, 26)`
  - MACD 可由 `ema(close, 12) - ema(close, 26)` 与 `ema(ema(close, 12) - ema(close, 26), 9)` 组合表达；当前没有 `macd()` 函数

### `ts_min(x, n)`

- 定义：历史窗口最小值
- 参数：
  - `x`：数值表达式
  - `n`：正整数字面量
- 返回类型：数值列
- 语义规则：
  - 对每个 `code` 计算包含当前行在内的最近 `n` 行最小值
  - 使用部分窗口；第一行也会返回结果
- 边界情况：
  - 需要 `time` 和 `code` 列
  - `n` 必须大于 0
- 最小示例：
  - `ts_min(close, 5)`

## Factor Engine MACD DSL Contract

Experimental status:

- This section documents experiment-branch behavior only.
- It must not be read as a stable-master rollout claim.

Trading-system integration should compose MACD from `ema()` and should not call
or register a `macd()` primitive.

Required input columns:

```text
code
time
close
```

Recommended downstream fields and exact expressions:

```text
macd_dif  = ema(close, 12) - ema(close, 26)
macd_dea  = ema(ema(close, 12) - ema(close, 26), 9)
macd_hist = (ema(close, 12) - ema(close, 26)) - ema(ema(close, 12) - ema(close, 26), 9)
```

Ordering and alignment contract:

- The engine sorts internally by `code`, then `time`, for ordered EMA execution.
- EMA state is isolated per `code`.
- Outputs are row-aligned with the input.
- Original input row order is restored in the returned frame.

Important boundary:

- `macd()` is intentionally unsupported.
- `ts_mean(close, n)` is not equivalent to `ema(close, n)`.
- The current implementation prioritizes correctness through the Polars/Python
  ordered EMA path, not a native optimized kernel.

### `ts_max(x, n)`

- 定义：历史窗口最大值
- 参数：
  - `x`：数值表达式
  - `n`：正整数字面量
- 返回类型：数值列
- 语义规则：
  - 对每个 `code` 计算包含当前行在内的最近 `n` 行最大值
  - 使用部分窗口；第一行也会返回结果
- 边界情况：
  - 需要 `time` 和 `code` 列
  - `n` 必须大于 0
- 最小示例：
  - `ts_max(close, 5)`

### `ts_median(x, n)`

- 定义：历史窗口中位数
- 参数：
  - `x`：数值表达式
  - `n`：正整数字面量
- 返回类型：数值列
- 语义规则：
  - 对每个 `code` 计算包含当前行在内的最近 `n` 行中位数
  - 使用部分窗口；第一行也会返回结果
  - 窗口里只对非空样本取中位数
  - 若窗口中非空样本数为偶数，返回中间两个值的平均数
  - 若窗口里没有任何非空样本，结果为 `null`
- 边界情况：
  - 需要 `time` 和 `code` 列
  - `n` 必须大于 0
- 最小示例：
  - 输入 `close=[5, 1, 7, 3, null]`，表达式 `ts_median(close, 3)` 输出 `[5, 3, 5, 3, 5]`

### `ts_mean(x, n)`

- 定义：历史窗口均值
- 参数：
  - `x`：数值表达式
  - `n`：正整数字面量
- 返回类型：数值列
- 语义规则：
  - 对每个 `code` 计算最近 `n` 行的 rolling mean
  - 使用部分窗口；第一行也会返回结果
- 边界情况：
  - 需要 `time` 和 `code` 列
  - `n` 必须大于 0
- 最小示例：
  - `ts_mean(close, 5)`

### `ts_sum(x, n)`

- 定义：历史窗口求和
- 参数：
  - `x`：数值表达式
  - `n`：正整数字面量
- 返回类型：数值列
- 语义规则：
  - 对每个 `code` 计算最近 `n` 行的 rolling sum
  - 使用部分窗口；第一行也会返回结果
- 边界情况：
  - 需要 `time` 和 `code` 列
  - `n` 必须大于 0
- 最小示例：
  - `ts_sum(close, 5)`

### `ts_std(x, n)`

- 定义：历史窗口标准差
- 参数：
  - `x`：数值表达式
  - `n`：正整数字面量
- 返回类型：数值列
- 语义规则：
  - 对每个 `code` 计算最近 `n` 行的 rolling std
  - 最少需要 2 个有效样本
- 边界情况：
  - 需要 `time` 和 `code` 列
  - `n` 必须大于 0
  - 首个样本窗口通常返回 `null`
- 最小示例：
  - `ts_std(close, 5)`

### `ts_count(cond, n)`

- 定义：统计历史窗口中条件成立的次数
- 参数：
  - `cond`：布尔表达式
  - `n`：正整数字面量
- 返回类型：整数列
- 语义规则：
  - `true` 记为 1，`false` 记为 0
  - `null` 先按 `false` 处理
  - 对每个 `code` 计算最近 `n` 行累计和
- 边界情况：
  - 需要 `time` 和 `code` 列
  - `n` 必须大于 0
- 最小示例：
  - `ts_count(close > open, 5)`

### `ts_any(cond, n)`

- 定义：历史窗口内是否至少出现一次 `true`
- 参数：
  - `cond`：布尔表达式
  - `n`：正整数字面量
- 返回类型：布尔列
- 语义规则：
  - `null` 先按 `false` 处理
  - 只要窗口内存在一次 `true`，结果就是 `true`
- 边界情况：
  - 需要 `time` 和 `code` 列
  - `n` 必须大于 0
- 最小示例：
  - `ts_any(close > open, 5)`

### `ts_all(cond, n)`

- 定义：历史窗口内是否全部为 `true`
- 参数：
  - `cond`：布尔表达式
  - `n`：正整数字面量
- 返回类型：布尔列
- 语义规则：
  - `null` 先按 `false` 处理
  - 只有窗口内全部为 `true`，结果才是 `true`
- 边界情况：
  - 需要 `time` 和 `code` 列
  - `n` 必须大于 0
- 最小示例：
  - `ts_all(close > open, 5)`

### `ts_rank(x, n, ascending=false, pct=false)`

- 定义：当前值在历史窗口中的相对排名
- 参数：
  - `x`：数值表达式
  - `n`：正整数字面量
  - `ascending`：是否升序，默认 `false`
  - `pct`：是否返回百分位，默认 `false`
- 返回类型：数值列
- 语义规则：
  - 窗口包含当前行
  - 默认按降序排名，值越大排名越靠前
  - ties 明确采用 `average`
  - `pct=true` 时返回 `rank / 有效非空样本数`
- 边界情况：
  - 需要 `time` 和 `code` 列
  - `n` 必须大于 0
  - `ascending` 和 `pct` 必须是布尔字面量
- 最小示例：
  - `ts_rank(close, 20, pct=true)`

### `argmax(x, n)`

- 定义：返回窗口内最近一次最大值距离当前行的距离
- 参数：
  - `x`：数值表达式
  - `n`：正整数字面量
- 返回类型：整数列
- 语义规则：
  - 窗口包含当前行
  - 返回值是“当前行往回数，需要退几步才能到最近一次最大值”
  - 当前行自己就是最近最大值时返回 `0`
  - ties 明确取最近一次出现的最大值
  - `null` 会被忽略
  - 前 `n - 1` 行使用部分窗口，不强制返回 `null`
  - 若窗口全部为 `null`，结果为 `null`
- 边界情况：
  - 需要 `time` 和 `code` 列
  - `n` 必须大于 0
- 最小示例：
  - 输入 `close=[5, 1, 7, 3]`，表达式 `argmax(close, 3)` 输出 `[0, 1, 0, 1]`
  - 输入 `close=[None, 2, None, 2]`，表达式 `argmax(close, 3)` 输出 `[null, 0, 1, 0]`

### `argmin(x, n)`

- 定义：返回窗口内最近一次最小值距离当前行的距离
- 参数：
  - `x`：数值表达式
  - `n`：正整数字面量
- 返回类型：整数列
- 语义规则：
  - 窗口包含当前行
  - 返回值是“当前行往回数，需要退几步才能到最近一次最小值”
  - ties 明确取最近一次出现的最小值
  - `null` 会被忽略
  - 前 `n - 1` 行使用部分窗口，不强制返回 `null`
  - 若窗口全部为 `null`，结果为 `null`
- 边界情况：
  - 需要 `time` 和 `code` 列
  - `n` 必须大于 0
- 最小示例：
  - 输入 `close=[5, 1, 7, 3]`，表达式 `argmin(close, 3)` 输出 `[0, 0, 1, 2]`
  - 输入 `close=[None, 2, None, 2]`，表达式 `argmin(close, 3)` 输出 `[null, 0, 1, 0]`

### `corr(x, y, n)`

- 定义：历史窗口相关系数
- 参数：
  - `x`：数值表达式
  - `y`：数值表达式
  - `n`：整数字面量，且 `n >= 2`
- 返回类型：数值列
- 语义规则：
  - 对每个 `code` 计算最近 `n` 行 rolling correlation
- 边界情况：
  - 需要 `time` 和 `code` 列
  - `n < 2` 会报错
- 最小示例：
  - `corr(close, volume, 5)`

### `cov(x, y, n)`

- 定义：历史窗口协方差
- 参数：
  - `x`：数值表达式
  - `y`：数值表达式
  - `n`：整数字面量，且 `n >= 2`
- 返回类型：数值列
- 语义规则：
  - 对每个 `code` 计算最近 `n` 行 rolling covariance
- 边界情况：
  - 需要 `time` 和 `code` 列
  - `n < 2` 会报错
- 最小示例：
  - `cov(close, volume, 5)`

### `skew(x, n)`

- 定义：历史窗口偏度
- 参数：
  - `x`：数值表达式
  - `n`：整数字面量，且 `n >= 3`
- 返回类型：数值列
- 语义规则：
  - 对每个 `code` 计算最近 `n` 行 rolling skew
- 边界情况：
  - 需要 `time` 和 `code` 列
  - `n < 3` 会报错
- 最小示例：
  - `skew(close, 5)`

### `kurt(x, n)`

- 定义：历史窗口峰度
- 参数：
  - `x`：数值表达式
  - `n`：整数字面量，且 `n >= 4`
- 返回类型：数值列
- 语义规则：
  - 对每个 `code` 计算最近 `n` 行 rolling kurtosis
- 边界情况：
  - 需要 `time` 和 `code` 列
  - `n < 4` 会报错
- 最小示例：
  - `kurt(close, 5)`

## 7. 分段时间范围函数

### 共同规则

`seg_*` 与 `seglen_*` 共享这些基本语义：

- 都先按 `code` 分组，再按 `time` 升序处理
- 结果保持列级、逐行对齐
- 同一段内广播相同聚合结果
- 这些函数当前都走 segmented 执行路径，因此单个表达式里不能混用多个不同 segmented spec

### `seg_*` 与 `seglen_*` 的关系

- `seg_*`：按“段数”切分完整序列
- `seglen_*`：按“长度列表”顺序切分完整序列
- 两个 family 的布尔函数都把 `null` 当成 `false`
- 两个 family 都允许嵌入更大列级表达式

### `seg_mean(x, n)`

- 定义：等分段均值
- 参数：
  - `x`：数值表达式
  - `n`：正整数字面量，表示段数
- 返回类型：数值列
- 语义规则：
  - 每个 `code` 的完整序列按样本数等分成 `n` 段
  - 若不能整除，余数优先分配给前面的段
- 边界情况：
  - 若组内样本数 `m < n`，只物化前 `m` 个非空段，每段 1 个样本
- 最小示例：
  - `seg_mean(close, 3)`

### `seg_sum(x, n)`

- 定义：等分段求和
- 参数：
  - `x`：数值表达式
  - `n`：正整数字面量
- 返回类型：数值列
- 语义规则：
  - 分段规则与 `seg_mean` 完全一致
- 边界情况：
  - `m < n` 时与 `seg_mean` 一样只物化非空段
- 最小示例：
  - `seg_sum(volume, 3)`

### `seg_count(cond, n)`

- 定义：等分段内 `true` 的个数
- 参数：
  - `cond`：布尔表达式
  - `n`：正整数字面量
- 返回类型：整数列
- 语义规则：
  - `null` 先按 `false` 处理
  - 其余分段规则与 `seg_mean` 一致
- 边界情况：
  - `m < n` 时仍不报错
- 最小示例：
  - `seg_count(close > open, 3)`

### `seg_any(cond, n)`

- 定义：等分段内是否至少一次为 `true`
- 参数：
  - `cond`：布尔表达式
  - `n`：正整数字面量
- 返回类型：布尔列
- 语义规则：
  - `null` 先按 `false` 处理
- 边界情况：
  - `m < n` 时仍不报错
- 最小示例：
  - `seg_any(close > open, 3)`

### `seg_all(cond, n)`

- 定义：等分段内是否全部为 `true`
- 参数：
  - `cond`：布尔表达式
  - `n`：正整数字面量
- 返回类型：布尔列
- 语义规则：
  - `null` 先按 `false` 处理
- 边界情况：
  - `m < n` 时仍不报错
- 最小示例：
  - `seg_all(close > open, 3)`

### `seglen_mean(x, [l1, l2, ...])`

- 定义：定长段均值
- 参数：
  - `x`：数值表达式
  - `[l1, l2, ...]`：正整数字面量列表，表示按顺序切分的长度规格
- 返回类型：数值列
- 语义规则：
  - 每个 `code` 分组按长度列表顺序切段
  - 每段计算均值并在段内广播
- 边界情况：
  - 第二个参数必须是非空正整数列表字面量
  - 若分组长度大于 `sum(lengths)`，执行期报错：`segment lengths do not cover full group`
  - 若 `sum(lengths)` 大于分组长度，最后一个非空段允许按剩余样本截断
- 最小示例：
  - `seglen_mean(close, [3, 5, 2])`

### `seglen_sum(x, [l1, l2, ...])`

- 定义：定长段求和
- 参数：
  - `x`：数值表达式
  - `[l1, l2, ...]`：正整数字面量列表
- 返回类型：数值列
- 语义规则：
  - 切段规则与 `seglen_mean` 完全一致
- 边界情况：
  - under-cover / over-cover 规则与 `seglen_mean` 完全一致
- 最小示例：
  - `seglen_sum(close, [3, 5, 2])`

### `seglen_count(cond, [l1, l2, ...])`

- 定义：定长段内 `true` 的个数
- 参数：
  - `cond`：布尔表达式
  - `[l1, l2, ...]`：正整数字面量列表
- 返回类型：整数列
- 语义规则：
  - `null` 先按 `false` 处理
  - 切段规则与 `seglen_mean` 一致
- 边界情况：
  - under-cover / over-cover 规则与 `seglen_mean` 一致
- 最小示例：
  - `seglen_count(close > open, [3, 5, 2])`

### `seglen_any(cond, [l1, l2, ...])`

- 定义：定长段内是否至少一次为 `true`
- 参数：
  - `cond`：布尔表达式
  - `[l1, l2, ...]`：正整数字面量列表
- 返回类型：布尔列
- 语义规则：
  - `null` 先按 `false` 处理
  - 切段规则与 `seglen_mean` 一致
- 边界情况：
  - under-cover / over-cover 规则与 `seglen_mean` 一致
- 最小示例：
  - `seglen_any(close > open, [3, 5, 2])`

### `seglen_all(cond, [l1, l2, ...])`

- 定义：定长段内是否全部为 `true`
- 参数：
  - `cond`：布尔表达式
  - `[l1, l2, ...]`：正整数字面量列表
- 返回类型：布尔列
- 语义规则：
  - `null` 先按 `false` 处理
  - 切段规则与 `seglen_mean` 一致
- 边界情况：
  - under-cover / over-cover 规则与 `seglen_mean` 一致
- 最小示例：
  - `seglen_all(close > open, [3, 5, 2])`

## 8. 表级函数

### `fft(x)`

- 定义：对单个原始数值列做频域变换，返回结果表
- 参数：
  - `x`：直接数值列引用
- 返回类型：表级结果
- 语义规则：
  - 当前只能写成根表达式 `fft(close)`
  - 结果列固定包含：
    - `code`
    - `frequency`
    - `sample_count`
    - `real`
    - `imag`
    - `magnitude`
    - `phase`
- 边界情况：
  - 需要 `time` 和 `code` 列
  - 不支持 `fft(close - open)`
  - 不支持 `rank(fft(close))`
  - 不支持 `fft(close) + 1`
  - 不支持属性访问形式，例如 `fft(close).magnitude`
- 最小示例：
  - `fft(close)`

## Alpha101 compatibility additions

This section records the Alpha101-compatible names added after the original
function inventory. These additions do not change DSL syntax, planner routes,
lifecycle behavior, native-heavy kernels, or M4 frozen structural rules.

### Alias functions

These names are parser-level aliases. They resolve to the canonical function
before validation, planning, DAG/CSE identity, and execution:

- `sum(x, n)` -> `ts_sum(x, n)`
- `stddev(x, n)` -> `ts_std(x, n)`
- `correlation(x, y, n)` -> `corr(x, y, n)`
- `covariance(x, y, n)` -> `cov(x, y, n)`
- `min(x, n)` -> `ts_min(x, n)`
- `max(x, n)` -> `ts_max(x, n)`

Alias functions must have the same route, ordered-audit behavior, and row-wise
results as their canonical targets.

### Pointwise functions

- `log(x)`: natural logarithm. `null` remains `null`; non-positive finite inputs
  follow backend floating-point semantics (`log(0) = -inf`, negative inputs
  become `NaN`).
- `signedpower(x, a)`: `sign(x) * abs(x) ^ a`. The exponent `a` must be a scalar
  numeric literal. `null` in `x` remains `null`.

Existing pointwise functions in this family include `abs(x)` and `sign(x)`.

### Cross-sectional function

- `scale(x, a=1)`: per-time cross-sectional scaling. For each `time` slice,
  non-null values are scaled so that `sum(abs(result)) = a`. The `a` argument
  must be a scalar numeric literal. `null` input rows remain `null`. If the
  denominator for a slice is zero or null, the result for that slice is `null`.

### Deferred function

- `product(x, d)` is intentionally not included in this batch. The current
  backend does not expose a clean vectorized rolling product expression, and
  the Python callback fallback is outside the accepted operator-addition
  boundary. It requires a separate design before it can be supported.
