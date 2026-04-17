# 因子表达式引擎性能基准

本文档是 Factor Engine benchmark 的固定落点。它负责记录 benchmark 的口径、样本、表达式集合和结果模板，不承担系统历史演进记录职责。

## 1. 文档职责

本文档回答：

- benchmark 用什么数据样本
- benchmark 测哪些表达式
- 冷缓存 / 热缓存怎么定义
- 单表达式与 `evaluate_many()` 怎么对比
- FFT 的幂长 / 非幂长怎么对比

本文档不回答：

- 系统为什么这样演进
- 当前架构怎么组织
- 当前功能怎么使用

## 2. 当前状态

当前 benchmark 文档已建立固定落点，且 segmented 专项 benchmark 已经有两层正式记录；更大范围的 P0 benchmark 结果仍待补齐。

这意味着：

- 后续 benchmark 结果应统一写入本文档
- 不再把 benchmark 细节散落到 `README`、`design` 或 `revolution` 中

当前已经落地的专项 benchmark：

- segmented window v1：
  - 脚本入口：[examples/benchmark_segmented.py](../examples/benchmark_segmented.py)
  - 结果记录：[benchmarks/segmented_v1.md](../benchmarks/segmented_v1.md)
  - 关注问题：`segment_id` 是否为主瓶颈、`evaluate_many()` 是否存在重复预处理、不同 `segment_count` 是否带来显著额外成本
- segmented workload benchmark：
  - 脚本入口：[examples/benchmark_segmented_workload.py](../examples/benchmark_segmented_workload.py)
  - 结果记录：[benchmarks/segmented_workload.md](../benchmarks/segmented_workload.md)
  - 真实样本：`data/minute_2026_03.parquet`，约 2904 万行、5495 个 `code`
  - 当前结论：同一 `segment_count` 的 prepared view 复用收益显著，不同 `segment_count` 仍然有明显额外成本
- segmented spec gate benchmark：
  - 脚本入口：[examples/benchmark_segmented_spec_gate.py](../examples/benchmark_segmented_spec_gate.py)
  - 结果记录：[benchmarks/segmented_spec_gate.md](../benchmarks/segmented_spec_gate.md)
  - 关注问题：length-based segmentation 的成本边界、spec diversity 的增长代价、count+length 混合 workload 的放大效应
- positional rolling benchmark：
  - 脚本入口：[examples/benchmark_positional_rolling.py](../examples/benchmark_positional_rolling.py)
  - 结果记录：[benchmarks/positional_rolling.md](../benchmarks/positional_rolling.md)
  - 关注问题：`argmax / argmin` 从 phase-1 `concat_list -> list.arg_*` fallback 切换到 phase-3 grouped deque positional kernel 后的实际收益

R15 之后，benchmark 范围还应额外关注但尚未形成正式记录的方向：

- grouped cross-sectional expressions：
  - `group_demean(close, industry)`
  - `group_zscore(ret_1d, industry)`
  - `group_rank(close, industry, pct=true)`
- seglen family completion：
  - `seglen_sum(close, [3, 5, 2])`
  - `seglen_count(close > open, [3, 5, 2])`
- workflow helper：
  - YAML / JSON 文件加载成本
  - 逐条 report 模式相对 strict `evaluate_many()` 的开销

## 3. 建议的性能基准数据样本

优先顺序：

1. 真实数据样本
2. 中等规模可复现实验样本
3. 小规模回归样本

对真实数据样本，至少记录：

- 数据来源
- 行数
- `code` 数量
- 每个 `code` 的时间长度范围
- 是否包含 2 的幂长度与非 2 的幂长度分组

## 4. 建议的性能基准表达式集合

### 回归项

- `close`
- `demean(close)`
- `ts_mean(close, 20)`

### 编译缓存项

- 相同表达式 cold cache / hot cache
- `evaluate_many()` 中相同表达式重复出现

### 布尔时序项

- `ts_count(close > open, 20)`
- `ts_any(close > open, 20)`
- `ts_all(close > open, 20)`

### 时序排序项

- `ts_rank(close, 20, pct=true)`

### 行业内截面项

- `group_demean(close, industry)`
- `group_zscore(ret_1d, industry)`
- `group_rank(close, industry, pct=true)`

### 长度分段项

- `seglen_mean(close, [3, 5, 2])`
- `seglen_sum(close, [3, 5, 2])`
- `seglen_count(close > open, [3, 5, 2])`

### FFT 项

- `fft(close)` on power-of-two groups
- `fft(close)` on non-power-of-two groups

### 工作流项

- `load_expression_file()` on small / medium / large YAML
- `load_expression_file()` on small / medium / large JSON
- `evaluate_expression_file()` strict mode
- `evaluate_expression_file_report()` mixed good / bad expressions
- `write_result(df, path)` on parquet / csv

## 5. 性能基准输出模板

每次正式记录建议至少包含：

- 日期
- 环境
  - Python 版本
  - Polars 版本
  - 数据样本摘要
- benchmark 类别
  - cold cache
  - hot cache
  - single evaluate
  - evaluate_many
  - FFT power-of-two
  - FFT non-power-of-two
- 结果表
  - 表达式
  - 耗时
  - 备注

## 6. 停止继续优化性能基准文档的评价标准

满足以下条件后，benchmark 文档本身短期不再继续优化：

1. benchmark 有固定落点
2. benchmark 表达式集合固定
3. cold / hot cache 定义明确
4. `evaluate_many()` 对照组明确
5. FFT 幂长 / 非幂长对照明确

只要以上五条成立，就不应继续优化 benchmark 文档结构本身，而应去补真实 benchmark 结果。

## 7. 再次优化性能基准体系的必要条件

只有满足以下至少一条，才再次优化 benchmark 体系：

- 当前 benchmark 不能支持性能决策
- 当前 benchmark 缺少关键 workload
- 当前 benchmark 结果不可复现
- 当前 benchmark 输出格式无法支撑阶段验收或 README 摘要

## 8. 参考文档

## 8. R13.5 基准补充说明

R13.5 新增了一份专门的 segmented spec 闸门基准：

- 脚本：[examples/benchmark_segmented_spec_gate.py](../examples/benchmark_segmented_spec_gate.py)
- 报告：[benchmarks/segmented_spec_gate.md](../benchmarks/segmented_spec_gate.md)
- workload 约定：
  - 使用真实日内 parquet 作为源样本
  - 将每个选中的 code 截成较短分片，确保 `[3,5,2]`、`[2,2,2,2]`、`[10,10]` 这类 PoC 长度规格依然合法
  - 再把这些短分组复制到带后缀的 code id 上，恢复足够行数用于成本对比
- 必答问题：
  - 单个 length spec 与单个 count spec 的成本对比
  - 从 1 到 8 个唯一 spec 的多样性增长成本
  - count + length 混合 workload 的放大效应
- 当前结果：
  - 闸门结论 = `GOOD`
  - `single(length) / single(count) = 0.94`
  - `diversity(8) / (diversity(1) * 8) = 0.73`
  - `mixed / (single(count) + single(length)) = 0.57`

## 8.1 R15 基准补充说明

R15 引入了三类新的 benchmark 候选面，但当前还没有正式 benchmark 报告落点，因此先冻结问题定义：

- grouped cross-sectional：
  - 目的不是证明 `group_*` 一定更快，而是确认分组键从 `time` 扩成 `[time, group_col]` 后没有出现异常放大
- seglen family completion：
  - 重点不是重新验证 `seglen_mean`，而是确认 `seglen_sum / count / any / all` 没有破坏现有 segmented prepared view reuse
- workflow helper：
  - 关注文件加载、report 模式和写出路径的固定开销
  - 只有当这些 helper 进入真实日常工作流主路径时，才值得形成正式 benchmark 报告

- [README.md](../README.md)
- [index.md](index.md)
- [documentation_policy.md](documentation_policy.md)
- [revolution.md](revolution.md)

## 8.3 Stage Lifecycle Benchmark

Stage lifecycle now has a dedicated benchmark entry:

- script: [examples/benchmark_stage_lifecycle.py](../examples/benchmark_stage_lifecycle.py)
- report: [benchmarks/stage_lifecycle.md](../benchmarks/stage_lifecycle.md)
- detailed outputs: `benchmarks/stage_lifecycle/*/{latest_run.json,history.csv,latest_batch_details.jsonl,latest_stage_details.jsonl,latest_stage_events.jsonl,benchmark_report.md}`

The benchmark compares:

- V1 profiling-only ordered batch execution
- V2 lifecycle sweep enabled

The required comparison metrics are:

- peak frame column count
- live/alive stage counts
- dropped stage count
- RSS trend

This benchmark is scoped to explicit ordered-batch stages only. It is not a DAG/CSE benchmark.

Stage lifecycle validation now also includes:

- focused tests: `python -m pytest tests\test_stage_lifecycle.py -q`
- real minute parquet smoke: `python examples\benchmark_stage_lifecycle_real_smoke.py --data data\minute_2026_03.parquet --rows 500000 --code-col ths_code`
- positional phase profiler: `python examples\benchmark_positional_phases.py --data data\minute_2026_03.parquet --rows 500000 --expr-counts 1,8,16,20 --code-col ths_code`
- real smoke report: `benchmarks/stage_lifecycle_real_smoke/real_smoke_report.md`
- native positional kernel notes: [docs/native_positional_kernel.md](native_positional_kernel.md)

The synthetic benchmark is a regression gate for structure metrics, not a wall-clock-only test. V2 must not worsen `peak_frame_col_count` or `peak_live_stage_count_estimate`, and it must reduce or eliminate `alive_stage_at_batch_end_count`.

## 8.2 R17 基线与 Profile 补充说明

R17 新增了一套更接近日常研究工作流的固定性能基线，并且第一次把 workflow helper 纳入正式 benchmark 口径。

- 脚本入口：[examples/benchmark_real_workload.py](../examples/benchmark_real_workload.py)
- 基线结果：[benchmarks/baseline.md](../benchmarks/baseline.md)
- 分阶段 profile：[benchmarks/profile.md](../benchmarks/profile.md)

R17 固定 workload 口径：

- 合成固定种子数据：`seed = 20260414`
- `120,000` 行
- `500` 个 `code`
- `12` 个 `industry`
- `26` 条表达式
- 同时覆盖：
  - `ts_mean / ts_std / ts_median`
  - `argmax / argmin`
  - `group_zscore / group_rank`
  - `seglen_*`
  - composed expressions
- 同时覆盖三种执行模式：
  - `evaluate()` loop
  - `evaluate_many()`
  - workflow batch

R17 当前记录的关键结果：

- `evaluate_many()` 相对 `evaluate()` loop 的加速比约为 `1.26x`
- strict workflow batch 与直接 `evaluate_many()` 的比值约为 `1.01x`
- workflow report 快路相对旧的逐条 `evaluate()` loop 约为 `1.20x`
- 当前 synthetic workload 下，主瓶颈已经不是 parse / validate / compile，也不是 workflow IO，而是 rolling ordered path

R17 对后续优化的含义：

- 第一优先级应继续围绕 rolling hot path，而不是先动 parser / validator / file IO
- `workflow` 层已经证明可以在不改核心 API 的前提下，通过复用 `evaluate_many()` 获得真实收益
- segmented / grouped 路径在这组 workload 下已不是首要瓶颈，后续只有在真实 workload 改变时才值得重新提升优先级
