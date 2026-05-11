# 因子表达式引擎演进记录

本文件负责记录 Factor Engine 的系统级演进。`README` 只描述当前系统状态；本文件负责回答“为什么会演进成现在这样”。

## 文档约定

- 本文按“系统级变更”记录，不展开零碎 bugfix、纯测试补丁和文案微调
- 每个条目都尽量回答同一组问题：
  - 背景
  - 目标
  - 任务
  - 验收
  - 风险
  - 非目标
  - 理论上最简单或最优的时间复杂度
  - 当前实现复杂度
  - 当前未达到理论上界的原因
  - 对未来的建议
  - 再次优化的必要条件
- 对不适合用复杂度描述的文档或接口组织类变更，复杂度字段写 `N/A`

## R0：初始表达式引擎基线

### 背景

项目最初需要一个可运行的因子表达式原型，验证从字符串表达式到 DataFrame 计算结果的完整链路是否可落地。

### 目标

- 建立最小可用 DSL
- 打通 `Lexer -> Parser -> Validator -> Executor`
- 形成可测试、可扩展的模块边界

### 任务

- 建立 AST 节点定义
- 实现基础词法分析与语法解析
- 建立变量、函数、参数数量等基础校验
- 建立列级表达式执行路径

### 验收

- 能稳定解析并执行基础算术、比较和简单函数调用
- 单元测试覆盖词法、语法、校验和执行主链路

### 风险

- DSL 一旦边界不清，后续函数扩展会持续返工
- 如果 parser / validator / executor 分工不稳，后续功能会耦合

### 非目标

- 不追求复杂查询优化
- 不追求实盘级增量状态系统
- 不追求表级表达式能力

### 理论上最简单的时间复杂度

- parse / validate / compile：`O(|expr|)`
- pointwise 列级执行：`O(n)`

### 当前实现复杂度

- 与理论基线一致，属于原型级最小实现

### 当前未达到更强上界的原因

- 当时目标是先打通能力，不是做优化器

### 对未来的建议

- 持续把语义层与执行层分开
- 新函数尽量通过统一 registry 接入，而不是散落在 executor 中硬编码

### 再次优化的必要条件

- 需要扩展 DSL 语法层能力
- 当前 AST / parser 结构开始阻碍 validator 或 executor 的演进
- 错误定位质量或解析性能变成真实问题

## R1：列级时序与截面能力建立

### 背景

仅有基础算术与条件表达式不足以支撑因子研究，系统需要最常见的时间序列与截面原语。

### 目标

- 建立按 `code / time` 组织的时间序列计算能力
- 建立按 `time` 组织的截面计算能力

### 任务

- 接入 `delay`、`ts_mean`、`ts_sum`、`ts_std`
- 接入 `demean`、`zscore`、`rank`
- 补齐 `corr`、`cov`、`skew`、`kurt` 等窗口统计能力

### 验收

- 时序函数按 `code` 分组、按 `time` 排序
- 截面函数按 `time` 分组
- 多个函数在统一校验与执行链路下可稳定运行

### 风险

- 时序与截面函数的执行上下文不同，若没有结构化抽象，后续会混成一条重路径

### 非目标

- 不做执行规划优化
- 不做批量执行共享

### 理论上最简单的时间复杂度

- shift / rolling 聚合：历史批量计算通常可做到 `O(n)` 到 `O(n log n)` 之间
- 截面排序：通常至少 `O(n log n)` 或按分组规模累加

### 当前实现复杂度

- 主要取决于底层 Polars rolling / ranking / group-by backend

### 当前未达到更强上界的原因

- 当时没有引入 AST 级执行画像，也没有针对不同函数拆分执行壳

### 对未来的建议

- 把“函数语义”和“执行需求”拆开描述，为后续执行规划做准备

### 再次优化的必要条件

- 基础时序或截面函数族出现明显 correctness 缺口
- benchmark 证明这些基础函数族重新成为主瓶颈
- 新函数类别已经无法沿当前结构平滑接入

## R2：执行规划与 `evaluate_many()`

### 背景

列级表达式早期共享一条统一重壳，导致 pointwise 与 cross-sectional 表达式也要付出排序与恢复顺序的固定成本。

### 目标

- 消除“所有列级表达式都走同一重壳”的明显浪费
- 建立 AST 级执行画像
- 新增批量列级执行接口

### 任务

- 引入 `FunctionSpec` 执行规划元信息
- 在 validator 中产出 AST 级 `ExecutionProfile`
- 在 executor 中按 `row_aligned_no_time_order / row_aligned_time_ordered / table` 分流
- 新增 `evaluate_many()`
- 引入内部 `PreparedFrame` 以共享排序与恢复顺序成本

### 验收

- 非时序表达式不再无条件走 `sort(code, time)`
- 时序表达式继续保持正确的有序执行语义
- `evaluate_many()` 能稳定返回“原表 + 多结果列”

### 风险

- mixed-profile AST 的执行路径选择容易失真
- 如果 validator 和 executor 的职责边界不清，会出现重复推导

### 非目标

- 不做通用 DAG / CSE
- 不做复杂查询优化器
- 不支持 table expr 的批量混合执行

### 理论上最简单的时间复杂度

- pointwise 路径：`O(n)`
- 需要排序的时序路径：`O(n log n)` + rolling / shift 成本
- 批量执行理想情况：同一执行壳只预处理一次

### 当前实现复杂度

- pointwise / 截面表达式已不再支付统一排序壳
- 时序表达式仍需排序视图与恢复顺序
- `evaluate_many()` 已能共享同类执行壳

### 当前未达到理论上界的原因

- 没有对不同表达式间的公共子表达式做复用
- 没有引入更细粒度的执行重写

### 对未来的建议

- 保持 `ExecutionProfile` 作为执行选路主依据
- 后续优化优先从“共享更多重复工作”而不是“增加更多路径种类”入手

### 再次优化的必要条件

- benchmark 证明执行壳开销仍是主瓶颈
- mixed-profile AST 频繁走到明显不合理的保守路径
- 需要支持 table expr 批量执行或更细粒度分桶

## R3：表级表达式与 FFT 接入

### 背景

系统早期默认所有合法表达式都返回“原表 + 一列结果”，这限制了表级结果的表达能力。

### 目标

- 打破“表达式只能返回一列”的假设
- 在不重写 DSL 的前提下接入第一类 table-valued expression

### 任务

- 为函数注册表增加 `result_kind` 与 backend 信息
- 在 validator 中建立 table / column 边界
- 在 executor 中接入 table path
- 实现 `fft(close)` 作为 root-only table expression

### 验收

- `fft(close)` 返回结构化新表
- table expr 不能嵌入 column expr
- 现有列级表达式行为保持兼容

### 风险

- table / column 边界如果不清，会污染整个表达式类型系统

### 非目标

- 不扩展链式频域语法
- 不支持 `fft(close - open)`
- 不支持把 table expr 当作中间值继续组合

### 理论上最简单的时间复杂度

- FFT backend 理论目标是 `O(n log n)`
- 结果字段选择理论上应接近 `O(1)` 元信息路由

### 当前实现复杂度

- 接入初期的 FFT backend 还是原型级，核心计算路径偏向 `O(n^2)`

### 当前未达到理论上界的原因

- 当时重点是先建立表级表达式路径，而不是一次性完成高性能 FFT kernel

### 对未来的建议

- 表级表达式扩展必须谨慎，不要在 parser 和类型系统尚未准备好时过早做链式访问

### 再次优化的必要条件

- 需要更多 table-valued expression
- 需要链式频域语法或字段访问
- table / column 边界已经成为功能扩展阻碍

## R4：列级时序原语增强

### 背景

系统已有基础 rolling 能力，但缺少一些使用频率很高的原语，尤其是最值和差分类函数。

### 目标

- 补齐一批低歧义、高频率的列级时序函数

### 任务

- 新增 `ts_min`
- 新增 `ts_max`
- 新增 `delta`
- 新增 `pct_change`
- 扩充 validator 的数值表达式识别能力

### 验收

- 新函数支持数值列和数值表达式输入
- 在 `code / time` 语义下结果稳定
- 测试覆盖窗口、排序、输入类型和边界错误

### 风险

- `pct_change` 的零分母行为若未写清，后续使用者会误判

### 非目标

- 不做零分母保护开关
- 不引入新的结果类型

### 理论上最简单的时间复杂度

- `delta / pct_change / ts_min / ts_max`：历史批量计算理论上通常可做到 `O(n)`

### 当前实现复杂度

- 当前实现依赖 rolling / shift backend，整体接近 `O(n)`

### 当前未达到更强上界的原因

- 尚未引入增量状态系统，所以单条新数据的 `O(1)` 更新没有落地

### 对未来的建议

- 新增时序函数时优先选择语义清楚、实现边界稳的原语

### 再次优化的必要条件

- 出现明确的在线增量更新需求
- `pct_change`、最值类函数的语义边界反复引发问题
- benchmark 证明这些函数在真实 workload 中是热点

## R5：编译层复用 / 编译缓存

### 背景

随着函数和批量接口增多，重复 parse / validate / compile 的固定成本开始变得明显。

### 目标

- 消除重复表达式的编译层重复工作
- 让 `evaluate_many()` 对相同表达式只编译一次

### 任务

- 为 AST 增加实例级缓存
- 为 `ValidationResult` 增加实例级缓存
- 为 compiled expression 增加实例级缓存
- 在 `evaluate_many()` 中对相同表达式去重编译

### 验收

- 相同表达式重复调用不再重复 parse / validate / compile
- `evaluate_many()` 中相同表达式仅编译一次
- cache key 至少绑定 `expression`、schema fingerprint、`time_col`、`code_col`

### 风险

- schema 变化导致缓存误命中
- 缓存命中如果改变错误语义，会让问题更隐蔽

### 非目标

- 不做整列结果缓存
- 不做 DAG / CSE
- 不做跨数据版本缓存

### 理论上最简单的时间复杂度

- cache hit：`O(1)`
- cache miss：`O(|expr|)`

### 当前实现复杂度

- 与上述目标一致

### 当前未达到更强上界的原因

- 没有跨表达式子树复用
- 没有执行结果缓存

### 对未来的建议

- 下一步更值得做的是可观测性与 benchmark，而不是直接上 DAG / CSE

### 再次优化的必要条件

- benchmark 证明 compile 层仍占明显比例
- 需要 cache stats / clear cache 支撑 benchmark 与调试
- 命中率、内存占用或 schema churn 暴露出新问题

## R6：布尔时序原语与 `ts_rank`

### 背景

系统此前能做数值滚动统计，但对“条件是否发生”“是否持续成立”“当前值在过去窗口中的位置”表达不足。

### 目标

- 增加条件类时序原语
- 增加窗口内相对位置排序能力

### 任务

- 新增 `ts_count(cond, n)`
- 新增 `ts_any(cond, n)`
- 新增 `ts_all(cond, n)`
- 新增 `ts_rank(x, n, ascending=false, pct=false)`
- 固定 `null` 和 tie-handling 语义

### 验收

- 布尔表达式可稳定作为时序函数输入
- `null` 行为写清并有测试覆盖
- `ts_rank` 在乱序输入、多 code、并列值下语义稳定

### 风险

- `null` 语义如果不先钉死，会持续返工
- `ts_rank` 容易在正确性完成后陷入过早优化

### 非目标

- 不做状态机
- 不做 entry / exit 生命周期逻辑
- 不承诺 `ts_rank` 第一版是最优热路径实现

### 理论上最简单的时间复杂度

- `ts_count / ts_any / ts_all`：历史批量计算理论上 `O(n)`，增量状态理想上可到 `O(1)`
- `ts_rank`：若使用更强数据结构，理论上可逼近 `O(n log w)`

### 当前实现复杂度

- `ts_count / ts_any / ts_all`：当前为 `O(n)` 级 rolling 聚合
- `ts_rank`：当前保守按 `O(n * w log w)` 理解更安全

### 当前未达到理论上界的原因

- 布尔类函数未引入增量状态系统
- `ts_rank` 未引入 order-statistics 结构或专门窗口状态维护

### 对未来的建议

- `ts_count / ts_any / ts_all` 可作为未来增量状态系统的优先落地点
- `ts_rank` 必须先用 benchmark 证明它是热点，再决定是否做性能专项

### 再次优化的必要条件

- 真实场景需要不同 `null` 语义
- `ts_count / ts_any / ts_all` 成为增量系统优先落地点
- benchmark 证明 `ts_rank` 是明显热点

## R7：FFT backend 优化

### 背景

FFT 路径接入后，功能已可用，但原型级 backend 在大样本上缺少真实的性能价值。

### 目标

- 在不改变 `fft(close)` 语义的前提下，降低 FFT backend 的 Python 层开销

### 任务

- 对 2 的幂长度输入增加 radix-2 FFT 快路径
- 保留任意长度输入的 correctness-first fallback
- 将结果构造从 `rows.append(dict)` 改成列式一次性建表

### 验收

- `fft(close)` 输出字段与语义不变
- 2 的幂长度输入不再走纯 Python 朴素 DFT
- 新旧实现结果一致，允许浮点误差

### 风险

- 零依赖策略会限制任意长度输入的高性能化空间
- Python 层分组调度仍可能是剩余瓶颈

### 非目标

- 不做链式频域语法
- 不做 Rust 重写
- 不修改 table DSL

### 理论上最简单的时间复杂度

- FFT 理论目标：`O(n log n)`

### 当前实现复杂度

- 2 的幂长度分组：`O(n log n)`
- 非 2 的幂长度分组：仍为 `O(n^2)` fallback

### 当前未达到理论上界的原因

- 当前刻意保持零额外依赖
- 尚未实现任意长度输入的统一高性能 FFT kernel

### 对未来的建议

- 先用真实 benchmark 判断 FFT 是否值得继续投入
- 若 FFT 在真实 workload 中是热点，应优先拍板依赖策略，而不是继续在零依赖路径上拖延

### 再次优化的必要条件

- benchmark 证明 FFT 是真实热点
- 非 2 的幂长度输入占主流且当前 fallback 成本过高
- 需要统一任意长度高性能 backend

## R8：README / Revolution 文档职责重构

### 背景

随着系统迭代增多，`README` 同时承担“当前说明书”和“历史演进日志”两类职责，导致首页越来越重，也越来越不适合作为项目入口。

### 目标

- 让 `README` 回归当前说明书
- 让 `revolution` 文档承接系统演进记录

### 任务

- 重构 `README`，删去大段历史演进叙述
- 新增 `docs/history/revolution.md`
- 明确 `README / revolution / design / 专题文档` 的职责边界

### 验收

- `README` 聚焦“现在是什么、怎么用、支持什么、有什么边界”
- `revolution` 统一承接历史变更记录与复杂度讨论

### 风险

- 如果后续继续把历史更新堆回 `README`，文档会再次失焦

### 非目标

- 不试图让 `revolution` 替代设计文档
- 不要求零碎修补都写成完整里程碑

### 理论上最简单的时间复杂度

- `N/A`

### 当前实现复杂度

- `N/A`

### 当前未达到理论上界的原因

- `N/A`

### 对未来的建议

- `README` 只维护当前真相
- `revolution` 以追加式方式维护系统级变更
- 对纯算法或 backend 变更保留复杂度分析，对文档或接口组织类变更允许使用 `N/A`

### 再次优化的必要条件

- 文档职责再次明显重叠
- benchmark、复杂度、当前真相又开始混写
- 新人或开发者重复找不到正确文档入口

## R9：Segmented Time Range v1 (`seg_mean`)

### 背景

系统已有 rolling time-series 能力，但还缺少“先把每个 `code` 的完整序列切成若干固定段，再在段内独立计算”的表达能力。这个能力和 rolling 不同，它不是相对当前位置的滑动窗口，而是固定分段后的段内聚合。

### 目标

- 在不发明新执行框架的前提下，为 DSL 增加第一批 segmented time range 能力
- 保持列级、逐行对齐的结果契约
- 先用一个语义最清晰的函数验证 segmented execution path 是否站得住

### 任务

- 在 `FunctionSpec` 中新增 `window_kind`，并把 segmented 作为独立窗口类别建模
- 新增 `seg_mean(x, n)`
- 在 validator 中将 `n` 限制为正整数 literal
- 在 executor 的 ordered time-series path 中生成 `segment_id`
- 将 `seg_mean` 实现为“段内均值聚合后广播回每一行”
- 在 engine 中为 segmented 表达式保留 AST 执行路径，不提前进入 compiled-expression cache

### 验收

- `seg_mean(x, n)` 能在单 code、多 code、乱序输入下稳定执行
- 结果保持原行数与原顺序
- 当组内样本数 `m < n` 时，仅物化前 `m` 个非空段，不报错
- `seg_mean` 可参与更大表达式，例如 `where(close > seg_mean(close, 2), close, open)`
- 全量测试通过

### 风险

- segmented execution 和普通 compile 流程边界如果不清晰，后续会把 helper 列语义污染到通用编译路径
- 如果过早为 segmented 做 prepared view 缓存，第一版实现复杂度会明显抬升
- 不同 `n` 的 segmented 调用混在同一个表达式里，会把当前 v1 的执行模型拉复杂

### 非目标

- 不做自然时间长度分段
- 不做按交易日历或 session 分段
- 不做 `seg_sum / seg_count / seg_any / seg_all / seg_rank`
- 不做 segmented prepared view 缓存
- 不做任意多个不同 `n` 的 segmented 调用共享执行上下文

### 理论上最简单的时间复杂度

- 如果输入已经按 `code / time` 有序，`seg_mean` 理论上可以在 `O(n)` 内完成：一次分段编号、一次段内聚合、一次结果广播

### 当前实现复杂度

- 当前按保守口径理解为 `O(n log n) + O(n)` 更安全
- 其中 `O(n log n)` 主要来自 ordered path 里的排序，后续 `segment_id` 生成、段内均值聚合与广播接近 `O(n)`

### 当前未达到理论上界的原因

- 系统当前的 ordered time-series path 默认以“先排序，再执行”为契约，没有假设输入已预排序
- segmented v1 故意优先保持和现有 ordered path 的结构一致，没有引入专门的 segmented prepared view 复用
- engine 当前也没有把 segmented 表达式纳入 compiled-expression cache

### 对未来的建议

- 第二批可以沿同一执行骨架补 `seg_sum / seg_count / seg_any / seg_all`
- 在 correctness 稳定后，再考虑 `evaluate_many()` 下按 `segment_count` 共享 prepared segmented view
- 如果 segmented 在真实 workload 中频繁出现，再决定是否把“多个不同 `n`”的表达式一起优化

### 再次优化的必要条件

- 真实 workload 里出现明显的 segmented 使用需求，而 `seg_mean` 一项已不足以表达
- benchmark 证明 segmented path 的排序或重复预处理已经成为可见瓶颈
- 用户开始频繁需要多个不同 `n` 的 segmented 调用出现在同一表达式里
- 需要自然时间长度分段、交易 session 分段或 segment-level 新结果契约

## R10：Segmented Benchmark 与 Prepared View 复用

### 背景

`seg_mean` v1 落地后，系统已经具备 segmented execution path，但还不清楚真正的主瓶颈在排序、`segment_id` 构造，还是 `evaluate_many()` 下的重复预处理。继续扩 `seg_*` 家族之前，需要先用数据判断这条路径是否值得做 execution 层复用。

### 目标

- 建立 segmented benchmark 基线
- 识别 `seg_mean` 路径的主要性能瓶颈
- 若同一 `segment_count` 的重复预处理明显，就在 `PreparedFrame` 中增加最小 segmented view 复用

### 任务

- 新增 [benchmarks/scripts/benchmark_segmented.py](../../benchmarks/scripts/benchmark_segmented.py)
- 生成 [benchmarks/reports/segmented_v1.md](../../benchmarks/reports/segmented_v1.md)
- 用三档数据规模覆盖单表达式、同 `segment_count`、不同 `segment_count`、混合表达式和 `evaluate_many()`
- 在 `PreparedFrame` 中新增 `segmented_views: dict[int, pl.DataFrame]`
- 新增 `_get_segmented_view(segment_count)`，让同一 `segment_count` 的 segmented 表达式共享预处理结果
- 为 `evaluate_many()` 增加“同 count 只构造一次”的测试

### 验收

- benchmark 能回答：
  - `segment_id` 是否为主瓶颈
  - `evaluate_many()` 是否存在显著重复预处理
  - 不同 `segment_count` 是否产生明显额外成本
- 同一 `segment_count` 的 segmented 表达式在 `evaluate_many()` 下只构造一次 segmented view
- 全量测试通过

### 风险

- segmented view 缓存 key 若设计错误，会导致结果语义错乱
- 如果缓存范围扩大过快，容易引入不必要的内存占用
- benchmark 结果会受机器状态影响，因此更适合做相对比较而不是绝对承诺

### 非目标

- 不把 segmented 表达式纳入 compiled-expression cache
- 不做任意多个不同 `n` 的多层级共享执行计划
- 不扩展 segmented 函数族
- 不修改 execution model

### 理论上最简单的时间复杂度

- 对同一 `segment_count` 的多个 segmented 表达式，如果预处理能够完全共享，理想上可以做到一次 `O(n log n)` 排序、一次 `O(n)` 分段编号，后续每个附加聚合表达式只增加接近 `O(n)` 的计算

### 当前实现复杂度

- 单个 segmented 表达式仍按 `O(n log n) + O(n)` 理解更安全
- 同一 `segment_count` 的 `evaluate_many()` 现在能够共享 segmented view，避免重复执行 `segment_id` 构造
- 不同 `segment_count` 仍然各自独立准备 segmented view

### 当前未达到理论上界的原因

- segmented 表达式当前仍保留在 AST 执行路径，没有进入 compiled-expression cache
- 只有 `segment_count` 粒度的 view 复用，还没有更细的表达式级共享
- 不同 `segment_count` 之间没有尝试复用分段准备结果

### 对未来的建议

- 如果下一步扩 `seg_sum / seg_count / seg_any / seg_all`，应直接复用当前 `segment_id` 与 segmented view 骨架
- benchmark 已经证明同 count 复用是值得的，后续是否继续优化应聚焦“不同 `segment_count` 的成本是否仍值得下降”
- 在功能扩展前，先保持 execution 层结构稳定，不要为了抽象而抽象

### 再次优化的必要条件

- benchmark 持续显示不同 `segment_count` 的重复准备成本仍是热点
- segmented 函数族扩展到 3 个以上，出现明显重复逻辑
- 真实 workload 中 `evaluate_many()` 大量混合 segmented 表达式
- 需要更细粒度的缓存统计或 memory/latency 权衡分析

## R11：Segmented Function Family 第一批补齐

### 背景

在 `seg_mean` 和 segmented prepared view 复用稳定之后，segmented 路径已经证明可用，也证明同一 `segment_count` 复用值得保留。下一步最自然的工作不是继续改执行模型，而是把同一语义骨架下最常用的 segmented 函数族补齐。

### 目标

- 在不改变 execution model 的前提下，补齐第一批 segmented family
- 让数值聚合和布尔聚合都复用同一套 `segment_id` 语义
- 固定 segmented 布尔函数与 rolling 布尔函数一致的 `null -> false` 规则

### 任务

- 新增 `seg_sum(x, n)`
- 新增 `seg_count(cond, n)`
- 新增 `seg_any(cond, n)`
- 新增 `seg_all(cond, n)`
- 在 registry / validator / executor / engine / tests 中接入对应函数
- 让 `evaluate_many()` 下的 segmented functions 继续复用按 `segment_count` 缓存的 prepared view

### 验收

- `seg_sum / seg_count / seg_any / seg_all` 在单 code、多 code、乱序输入、`n > m` 情况下语义稳定
- `seg_count / seg_any / seg_all` 对 `null` 的处理统一为 `fill_null(False)`
- segmented family 可参与更大表达式，例如 `seg_sum(close, 2) / seg_count(close > open, 2)`
- 全量测试通过

### 风险

- 如果数值类和布尔类分别长出各自的 segmented helper，后续函数越多越容易出现语义漂移
- 如果 `null` 语义没有和 rolling 布尔函数保持一致，用户会得到两套规则
- segmented function family 扩展过快时，容易诱发过早抽象

### 非目标

- 不做 `seg_rank`
- 不做按自然时间长度分段
- 不做 `[t1, t2]` 固定时间区间 DSL
- 不做 rolling + segmented 嵌套
- 不做非 literal `n`

### 理论上最简单的时间复杂度

- 对已排序输入和已复用的同 count segmented view，`seg_sum / seg_count / seg_any / seg_all` 理论上都可以按接近 `O(n)` 的段内聚合与广播完成

### 当前实现复杂度

- 单个 segmented family 表达式当前仍按 `O(n log n) + O(n)` 理解更安全
- 同一 `segment_count` 的 `evaluate_many()` 里，预处理 view 可以复用，新增函数主要增加段内聚合与广播成本

### 当前未达到理论上界的原因

- 系统仍沿用 ordered path，默认先排序后执行，不假设输入预排序
- segmented expressions 仍保留在 AST 执行路径，没有 compiled-expression cache
- 当前只做了按 `segment_count` 的 view 复用，没有进一步抽象出更细粒度的 segmented aggregation cache

### 对未来的建议

- 如果下一步继续扩 segmented family，应优先选择 `seg_rank` 之外的同类聚合函数，保持 execution 语义可复制
- 如果 segmented function family 再扩到更多函数，再考虑抽 `_compile_segmented_numeric_agg` / `_compile_segmented_boolean_agg` 这类 helper
- 继续让 benchmark 决定是否要做更深层的 segmented execution 优化

### 再次优化的必要条件

- segmented function family 扩展后开始出现明显重复逻辑或语义漂移
- benchmark 证明 segmented 聚合本身而不是 view 预处理已经成为热点
- 用户开始频繁要求 `seg_rank`、calendar-based 分段或更复杂的 segment-aware DSL

## R12：Segmented Real Workload Benchmark

### 背景

在 `seg_mean`、prepared view 复用和第一批 segmented family 落地之后，系统已经具备一条完整的 segmented execution 路径，但此前的 benchmark 仍然偏向阶段性专项验证。是否继续扩 `seg_rank` 或继续做更深的 execution 优化，应该先用真实 workload 来回答。

### 目标

- 用真实 intraday parquet 样本验证 segmented family 的成本结构
- 量化 `evaluate_many()` 下同 count 复用的真实收益
- 量化不同 `segment_count` 的额外成本边界
- 为“继续扩 segmented family”还是“先停功能、继续围绕性能边界收口”提供决策依据

### 任务

- 新增 [benchmarks/scripts/benchmark_segmented_workload.py](../../benchmarks/scripts/benchmark_segmented_workload.py)
- 生成 [benchmarks/reports/segmented_workload.md](../../benchmarks/reports/segmented_workload.md)
- 基于真实样本 [data/minute_2026_03.parquet](../data/minute_2026_03.parquet) 生成 `S / M / L` 三档 workload
- 在 benchmark 中覆盖：
  - 单个 segmented 表达式
  - 同 `segment_count` 的多表达式
  - 不同 `segment_count` 的多表达式
  - mixed workload
  - `evaluate()` 与 `evaluate_many()` 对比
- 在结果中单独记录排序、segmented view 构造、聚合广播、恢复原顺序的粗粒度阶段耗时

### 验收

- benchmark 能回答：
  - 同一 `segment_count` 的 prepared view 复用是否在真实 workload 下仍然显著有效
  - 不同 `segment_count` 是否仍然明显更贵
  - segmented 的额外成本在 mixed workload 中是否已经可控
- 结果文档能够作为后续 segmented roadmap 的决策依据
- benchmark 入口、结果落点与文档引用完整打通

### 风险

- 真实数据 benchmark 会受机器状态与 parquet 扫描路径影响，不适合做绝对数值承诺
- 单月 intraday 数据的分布不能代表所有市场或所有周期
- 若 benchmark 口径后续频繁漂移，会降低不同阶段结果之间的可比性

### 非目标

- 不在本轮 benchmark 中继续扩 `seg_rank`
- 不在本轮 benchmark 中改变 execution model
- 不在本轮 benchmark 中把 segmented 表达式纳入 compiled-expression cache
- 不在本轮 benchmark 中支持自然时间长度分段

### 理论上最简单的时间复杂度

- 对同一 `segment_count` 的 grouped workload，若排序和分段准备可完全共享，则额外增加一个 segmented 聚合表达式理论上只需接近 `O(n)` 的段内聚合与广播
- 若不同 `segment_count` 之间也能共享更多预处理，中间成本上界还能继续下降，但这已经超出当前实现范围

### 当前实现复杂度

- 单个 segmented 表达式仍按 `O(n log n) + O(n)` 理解更安全
- 同一 `segment_count` 的 `evaluate_many()` 已能够把排序后 prepared view 与 `segment_id` 准备共享给多个表达式
- 不同 `segment_count` 的调用当前仍然需要各自独立构造 segmented view

### 当前未达到理论上界的原因

- 系统默认不假设输入已经按 `code / time` 预排序，因此排序成本仍然保留
- segmented view 复用目前只做到 `segment_count` 粒度，没有做跨 count 复用
- segmented 表达式仍保留在 AST 执行路径，没有进入 compiled-expression cache

### 对未来的建议

- 真实 workload 结果已经足以支持当前判断：先不要扩 `seg_rank`
- 若继续围绕 segmented 优化，应优先聚焦“不同 `segment_count` 的额外成本是否值得继续下降”
- 若真实用户场景里同 count multi-expression 是主流，当前 prepared view 复用策略值得保留
- 若 mixed workload 的比例继续上升，应观察 segmented 与 rolling 共存时 ordered path 是否重新成为热点

### 再次优化的必要条件

- 真实 workload 持续显示不同 `segment_count` 的额外成本仍是主瓶颈
- 真实 workload 中开始大量出现需要 `seg_rank` 的段内排序需求
- 用户开始频繁提出跨 count 复用、calendar-based 分段或 segment-level 结果契约需求
- benchmark 结果开始显示 mixed workload 下 ordered path 或恢复顺序步骤重新成为热点

## 下一步建议

基于当前阶段状态，下一步最稳的顺序是：

1. 先保持 segmented 当前支持集稳定，不继续扩 `seg_rank`
2. 若继续做 segmented，优先围绕不同 `segment_count` 的成本边界和 mixed workload 表现做判断
3. 主线回到全局 benchmark / 可观测性 / FFT / `ts_rank` 等更高优先级议题
4. 若主线稳定，再补 `clip(x, lower, upper)` 这类低风险辅线函数

## R13.5：Segmented 规格扩展与成本闸门

R12 answered whether the existing segmented family was worth keeping and whether same-count reuse had real value. R13.5 is a different kind of step: it is not “more segmented functions”, but a controlled semantic extension that tests whether the engine can carry a second segmented spec without losing its cost boundary.

### 目标

- introduce exactly one length-based PoC function: `seglen_mean(x, [l1, l2, ...])`
- 保持现有有序执行路径，以及 `(code, segment_id)` 的段内聚合加广播模型
- turn “should we continue the seglen family?” into an explicit stop/go gate instead of a default continuation

### 变更内容

- 词法分析 / 解析 / AST 现在通过 `ListNode` 接受列表字面量
- 校验器会对 `seglen_mean` 的长度规格做严格检查，要求它必须是非空的正整数字面量列表
- 执行器把 segmented 预处理视图的键从 `segment_count` 扩展为不可变规格键：
  - `("equal", n)`
  - `("length", (l1, l2, ...))`
- 执行器把等分和定长两类构造器保持为分开的实现，而不是塞进一个分支复杂的辅助函数
- 同规格复用仍然保留
- 跨规格复用在这一阶段仍然刻意禁用

### 冻结范围

- no `seg_rank`
- no `seglen_sum / seglen_count / seglen_any / seglen_all`
- no non-literal specs
- no execution-model rewrite
- 在闸门结论出来之前，不做跨规格缓存重构

### 交付物

- `seglen_mean` implementation
- list-literal validation for segmented length specs
- 以 `SegmentSpecKey` 为键的 segmented 预处理视图缓存
- benchmark script: [benchmarks/scripts/benchmark_segmented_spec_gate.py](../../benchmarks/scripts/benchmark_segmented_spec_gate.py)
- benchmark report: [benchmarks/reports/segmented_spec_gate.md](../../benchmarks/reports/segmented_spec_gate.md)

### 闸门结果

R13.5 benchmark result on 2026-04-14:

- `single(length) / single(count) = 0.94`
- `diversity(8) / (diversity(1) * 8) = 0.73`
- `mixed(count+length) / (single(count) + single(length)) = 0.57`
- gate decision = `GOOD`

### 当前解读

- length-based segmentation is not more expensive than count-based segmentation in the current PoC workload shape
- spec diversity growth stayed sub-linear relative to the naive 8x baseline
- mixed count + length execution did not show abnormal amplification

### 下一步

R13.5 已通过自己的闸门，因此现在允许进入 Phase 7 扩展。这里最重要的约束仍然成立：之所以允许扩展，是因为闸门通过了。如果未来的 workload 推翻了这条边界，正确做法是重新冻结或继续优化，而不是默认一路扩下去。

## R14：Core Expression 与 TS Primitives v1

### 背景

在 R13.5 之后，segmented 路径和 benchmark 边界已经暂时稳定，主线更适合回到 DSL 自身的“高频缺口”补齐。此时系统仍缺少几类会频繁出现在真实表达式里的基础能力：

- 逻辑运算 `and / or / not`
- 显式空值检测与替换
- 低风险标量数学 helper
- 一个高频但低歧义的 rolling 统计量 `ts_median`
- rolling 窗口内极值位置 helper

这些能力都可以沿现有 `Lexer -> Parser -> Validator -> Executor -> Engine` 结构接入，而不需要重写执行模型，因此适合在一个受控版本内完成。

### 目标

- 在不改变 `FactorEngine` 公共 API 形状的前提下，补齐上述五类核心能力
- 保持列级表达式逐行对齐、同高返回契约
- 保持 time-series 路径的 `code` 隔离、`time` 有序执行和原顺序恢复
- 用分 slice 的方式控制语义风险，避免一次性扩太多类型系统或执行抽象

### 任务

- slice 1：
  - 新增逻辑运算 `and / or / not`
  - 新增 `is_null(x)` / `fill_null(x, v)`
- slice 2：
  - 新增 `abs(x)` / `clip(x, lower, upper)` / `sign(x)`
- slice 3：
  - 新增 `ts_median(x, n)`
- slice 4：
  - 新增 `argmax(x, n)` / `argmin(x, n)`
- 同步补齐：
  - lexer / parser / validator / executor / engine 分层测试
  - `README` 当前真相

### 验收

- `parse / validate / evaluate / evaluate_many` 公共 API 形状保持不变
- 逻辑表达式可解析、可校验、可执行
- `is_null / fill_null / abs / clip / sign` 可单独使用，也可嵌入更大表达式
- `ts_median / argmax / argmin` 被识别为 time-series 表达式，保持 `code` 隔离、按 `time` 排序、并恢复原始行顺序
- `evaluate_many()` 对新能力保持兼容，且继续拒绝 table expressions
- 全量测试继续保持绿色

### 风险

- 逻辑运算的优先级一旦定义不清，后续会不断出现“表达式读法不一致”的问题
- `fill_null` 若过早追求广泛类型支持，会把现有轻量 type inference 拉复杂
- `ts_median` 的 null / 偶数窗口语义如果不钉死，底层 backend 变化会让用户难以判断结果
- `argmax / argmin` 如果不先冻结“返回距离还是返回绝对位置”“tie 取哪一个”，后续表达式会出现语义歧义

### 非目标

- 不支持字符串字面量
- 不支持 industry grouping
- 不扩展 `seglen_*` family
- 不改文件输入输出能力
- 不重构 cache 架构
- 不改变 FFT 行为
- 不改变 segmented execution 语义

### 理论上最简单的时间复杂度

- 逻辑运算与标量 helper：`O(n)`
- `is_null / fill_null`：`O(n)`
- `ts_median(x, n)`：rolling median 理论上通常至少按 `O(n log w)` 理解更稳妥
- `argmax / argmin`：
  - 若有专门窗口状态结构，理论上可以逼近 `O(n)`
  - 若按窗口扫描实现，更保守地按 `O(n * w)` 理解

### 当前实现复杂度

- 逻辑运算与标量 helper：当前实现接近 `O(n)`
- `is_null / fill_null`：当前实现接近 `O(n)`
- `ts_median`：当前依赖底层 rolling median backend，按 `O(n log w)` 理解更安全
- `argmax / argmin`：当前通过 `rolling_map` 按窗口执行 Python 级极值位置逻辑，更保守地按 `O(n * w)` 理解

### 当前未达到理论上界的原因

- 系统目前优先保持 execution model 稳定，不为了这批新函数额外引入窗口状态机或 specialized kernel
- `argmax / argmin` 第一版优先锁定语义：返回“距离当前行最近的极值距离”、并列取最近、忽略 null；性能不是第一目标
- `fill_null` 当前只对数值/布尔路径给出明确约束，没有顺手做更宽的类型系统扩展

### 对未来的建议

- 若逻辑表达式继续扩展，应优先补“错误信息更具体”和“复杂优先级组合测试”，而不是过早引入新的 AST node 类型
- 若 `fill_null` 后续需要支持更宽类型，应先明确 type coercion 规则，再扩 validator
- 若 benchmark 证明 `argmax / argmin` 成为热点，应优先决定是否接受更专门的 backend / 状态结构，而不是继续在 `rolling_map` 上堆复杂逻辑
- 若未来还要补更多 rolling 位置类函数，可先抽统一 helper，但当前版本没有必要为两个函数过早抽象

### 再次优化的必要条件

- 逻辑表达式开始频繁出现复杂组合，当前 precedence/错误信息不足以支撑定位
- `fill_null` 需要支持字符串、枚举或更复杂的类型兼容规则
- benchmark 证明 `ts_median` 或 `argmax / argmin` 成为真实热点
- 用户开始要求更多 arg-position / rank-position 系列函数，当前实现出现明显重复逻辑

## R15：Research Workflow 与 Grouped Semantics v1

### 背景

在 R14 之后，DSL 基础表达能力已经覆盖到一批高频原语，但研究工作流层面仍然有几个明显缺口：

- 截面只能按 `time` 做全市场聚合，缺少行业内截面能力
- `seglen_*` 仍停留在 `seglen_mean` 单函数 PoC，family 不完整
- 批量表达式仍主要依赖 Python 里手写 tuple 列表，不适合文件驱动研究流程
- 结果落盘需要用户自己拼 parquet / csv 写出逻辑
- 工作流层一旦批量表达式中混入坏表达式，错误缺少“哪一条、在哪一层失败”的结构化汇总

这些问题的共同特点是：它们都可以在不改 `FactorEngine` 核心 API 的前提下，沿现有 registry / validator / executor / workflow helper 边界增量接入。

### 目标

- 增加行业内截面函数族，同时保持现有 `demean / zscore / rank` 语义不变
- 补齐第一批 `seglen_*` family
- 提供 YAML / JSON 驱动的批量表达式工作流
- 提供 parquet / csv 结果输出 helper
- 在 workflow 边界提供分层错误分类与批量失败汇总

### 任务

- Track A：
  - 新增 `group_demean(x, group)`
  - 新增 `group_zscore(x, group)`
  - 新增 `group_rank(x, group, ascending=false, pct=false)`
  - 新增 `seglen_sum / seglen_count / seglen_any / seglen_all`
- Track B：
  - 新增 `src/factor_engine/workflow.py`
  - 支持从 `.json / .yaml / .yml` 读取批量表达式文件
  - 新增 `write_result(df, path)`，按后缀输出 parquet / csv
  - 新增 [scripts/workflow/file_batch_workflow.py](../../scripts/workflow/file_batch_workflow.py)
- Track C：
  - 新增 workflow 层错误类型 `WorkflowError / WorkflowConfigError / WorkflowIOError`
  - 新增结构化失败 payload `ExpressionFailure`
  - 新增 `evaluate_expression_file_report(...)` 与批量失败汇总路径
  - 维持 parser / validator / executor 的原始错误类型不变
- 同步补齐：
  - grouped / seglen / workflow / error tests
  - `README` 当前真相

### 验收

- `FactorEngine.parse / validate / evaluate / evaluate_many` 保持可用且签名不变
- `group_*` family 能按 `[time, group_col]` 正确隔离计算
- `seglen_*` family 的长度规则、under-cover 报错、over-cover 截断行为与 `seglen_mean` 对齐
- 用户可以从 YAML / JSON 文件加载表达式批次并执行
- 用户可以把结果输出到 `.parquet` / `.csv`
- 批量工作流在 mixed good/bad expressions 下可以返回结构化失败 summary
- 全量测试继续保持绿色

### 风险

- grouped API 若直接污染现有 `demean / zscore / rank` 参数形状，会抬高兼容风险，因此 v1 选择显式 `group_*` family
- `group_col` 若允许派生表达式，会把当前轻量 validator 和 executor 路径一起复杂化，因此 v1 冻结为“直接列引用”
- `seglen_*` 如果与 `seglen_mean` 的 under-cover / over-cover 规则不一致，用户会得到两套分段语义
- workflow 错误系统如果从底层全面重构，会侵入 parser / validator / executor，因此 v1 只在 helper 边界做包装与汇总

### 非目标

- 不改变已有逻辑 / null / math / ts primitive 语义
- 不重构 `FactorEngine` 核心 API
- 不改变 FFT 行为
- 不改变 equal-count segmented 语义
- 不引入通用 DAG / CSE / 结果缓存
- 不新增字符串字面量 DSL

### 理论上最简单的时间复杂度

- `group_demean / group_zscore / group_rank`：在既有截面 group-by / rank backend 上，按分组后的 `O(n)` 到 `O(n log n)` 理解更安全
- `seglen_*`：在已排序输入和已准备 segmented view 上，段内聚合与广播可按接近 `O(n)` 理解
- YAML / JSON 文件加载：`O(file_size)`
- parquet / csv 写出：通常随结果表规模线性增长，按 `O(n)` 理解
- workflow 失败汇总：对 `k` 条表达式按 `O(k)` 聚合元信息

### 当前实现复杂度

- grouped 截面函数复用现有 Polars `over([...])` 路径，没有引入额外执行模型
- `seglen_*` family 复用现有 segmented prepared view 与长度规格 key
- YAML 读取当前使用受限 schema 的轻量解析器，而非外部 YAML 依赖
- 错误汇总当前按表达式逐条执行并收集 `ExpressionFailure`

### 当前未达到理论上界的原因

- grouped `rank` 仍依赖底层 rank backend，没有专门的行业内排序 kernel
- segmented 表达式仍保留在 AST 执行路径，没有进入 compiled-expression cache
- 文件工作流仍是 helper 层，不做更复杂的增量执行或结果缓存
- 失败汇总为了保留“哪条表达式失败”信息，当前 report 路径按表达式逐条执行，而不是直接复用 `evaluate_many()` 的 fail-fast 语义

### 对未来的建议

- 若行业内截面函数继续扩展，优先延续显式 `group_*` family，而不是回头重载旧函数签名
- 若 workflow 配置继续增大，优先引入正式 schema 校验层，再考虑支持更宽文件格式
- 若 batch report 成为主工作流，应继续补 CLI / 示例层的人类可读 summary，而不是只停留在 Python dataclass
- 若 segmented family 继续扩张，再考虑抽象更统一的 `seglen_*` helper，而不是现在就过早重构 executor

### 再次优化的必要条件

- 用户开始要求行业层级之外的更多分组语义，例如 style bucket 或多列 group key
- `seglen_*` family 继续扩张到更多数值 / 排序类函数，当前 helper 出现明显重复
- workflow 文件 schema 需要版本化、注释、元数据或运行参数，当前轻量 loader 不再够用
- batch 错误汇总开始需要 partial retry、失败重跑或机器可消费的更稳定协议

## R16：README 收口与文档语义拆分 v1

### 背景

随着 R14 和 R15 把 DSL、grouped semantics、workflow helper、错误汇总逐步补齐，`README` 已经从“入口文档”膨胀成了“半份规范文档”。这会带来两个问题：

- 新人第一次进入项目时，首屏信息过重
- 同一条语义开始同时出现在 `README`、`design` 和多个专题文档里，后续维护很容易漂移

### 目标

- 把 `README` 收口成真正的 entrypoint
- 把 DSL、函数、workflow、错误系统拆到单独文档
- 明确“每类语义只在一个地方维护”

### 任务

- 新增 [docs/language.md](language.md)
- 新增 [docs/functions.md](functions.md)
- 新增 [docs/workflow.md](workflow.md)
- 新增 [docs/errors.md](errors.md)
- 将 `README` 改写为：
  - 一句话定位
  - 能力概览
  - quick start
  - core concepts
  - docs navigation
- 更新 [docs/index.md](index.md)、[docs/design.md](design.md)、[docs/documentation_policy.md](documentation_policy.md)，使其承认新的文档职责边界

### 验收

- `README` 可以在 2 分钟内读完并完成入口指引
- 详细 DSL 语义不再停留在 `README`
- `functions.md` 覆盖当前注册表中的全部函数
- workflow 和 error 语义都有独立文档落点

### 风险

- 若拆得太碎，会让读者找不到入口，因此 `README` 和 `index` 必须同时承担强导航作用
- 若拆分后仍把规范级语义留在 `design` 或 `README`，就会重新引入重复维护

### 非目标

- 不修改 engine 代码
- 不改变 DSL 语义
- 不重组 `docs/` 之外的目录结构
- 不为这次拆分重写现有示例脚本

### 理论上最简单的时间复杂度

- `N/A`

### 当前实现复杂度

- `N/A`

### 当前未达到理论上界的原因

- `N/A`

### 对未来的建议

- 后续新增 DSL 语义，优先更新 `language` 或 `functions`，而不是往 `README` 回填
- 后续新增 workflow 或错误行为，优先更新 `workflow` / `errors`
- `design` 继续保持“结构文档”，不要回到“半份规范文档”

### 再次优化的必要条件

- `README` 再次膨胀成规范文档
- 新专题出现但没有稳定落点
- 多份文档开始重复维护同一条函数或 DSL 语义
## R17：性能基线与 Workflow Report 快路

### 背景

在 R15 之后，系统已经具备 grouped semantics、seglen family 和 workflow helper，但缺少一套固定、可复现、能覆盖真实研究路径的统一性能基线。与此同时，workflow report 模式虽然语义完整，却仍然沿用“逐条 `evaluate()` + 逐列 append”的慢路径，无法复用 `evaluate_many()` 已有的排序与批量执行收益。

### 目标

- 建立固定 benchmark workload，作为后续所有优化的共同对照面
- 建立阶段级 profile，而不是只看总耗时
- 在不改 `FactorEngine` 公共 API 的前提下完成至少一处低侵入优化
- 把性能结果正式沉淀到 `benchmarks/` 和 `revolution`

### 任务

- 新增 [benchmarks/scripts/benchmark_real_workload.py](../../benchmarks/scripts/benchmark_real_workload.py)
- 固定 synthetic workload：
  - `120,000` 行
  - `500` 个 `code`
  - `12` 个 `industry`
  - `26` 条表达式
  - 固定种子 `20260414`
- 输出：
  - [benchmarks/reports/baseline.md](../../benchmarks/reports/baseline.md)
  - [benchmarks/reports/profile.md](../../benchmarks/reports/profile.md)
- 优化 [src/factor_engine/workflow.py](../src/factor_engine/workflow.py)：
  - 先逐条 `validate()`
  - 再对全部可执行列表达式走一次 `evaluate_many()` 快路
  - 若批量执行失败，再回退到逐条 `evaluate()`，保留失败表达式身份
- 补齐 workflow 相关测试，确保语义不漂移

### 验收

- baseline workload 已固定并落盘
- stage-level profile 已可复现
- 至少一个热点已经被识别：
  - 当前 synthetic workload 下，`rolling_time` 是明确第一瓶颈
- 至少一个优化已经带来可测收益：
  - `before_time = 7.733965s`
  - `after_time = 6.442421s`
  - `improvement_ratio = 1.20x`
  - `change_description = workflow report 从逐条 evaluate 改为 validate 后批量 evaluate_many 快路 + 个别失败回退`
- `evaluate_many()` 相对 `evaluate()` loop 的基线加速比为 `1.26x`
- 全量测试保持绿色

### 风险

- synthetic workload 不能替代真实生产数据，只能作为稳定对照面；如果后续真实 workload 与当前表达式分布差异很大，热点排序可能变化
- workflow report 快路如果直接 fail-fast，会丢失“哪条表达式失败”的身份信息；因此必须保留逐条回退路径
- profile 指标如果口径混杂执行与 IO，会误导优化方向；R17 已把 `io_time` 收紧到文件加载和结果写出本身

### 非目标

- 不改 `FactorEngine.parse / validate / evaluate / evaluate_many` 的公开形状
- 不引入通用 DAG / CSE / 结果缓存
- 不重写 rolling kernel
- 不改变 grouped / segmented / FFT 语义

### 理论上最简单的时间复杂度

- parse / validate / compile：`O(|expr|)`
- workflow file load / result write：`O(file_size)` 或 `O(n)`
- ordered rolling 路径：在当前 backend 约束下，保守按 `O(n * rolling_cost)` 理解更安全

### 当前实现复杂度

- benchmark 脚本本身保持线性数据构造与固定场景测量
- workflow report 快路的额外开销主要是逐条 `validate()`，但换来了批量执行复用
- 当前 synthetic workload 的主耗时集中在 ordered rolling path，而不是编译层或 workflow IO

### 当前未达到理论上界的原因

- rolling family 仍然主要依赖 backend rolling / rolling_map 能力，没有专门的 engine 内核
- `argmax / argmin` 仍然不是专门优化的窗口位置 kernel
- workflow report 为了保留失败身份，仍然需要一条 fallback 路径，无法完全退化成纯 `evaluate_many()`

### 对未来的建议

- 下一轮优化优先级应放在 rolling hot path，而不是先动 IO 或 parser
- 若后续真实 workload 以 workflow report 为主，应继续围绕“批量成功快路 + 个别失败回退”设计，不要回到逐条执行
- 若 future profile 证明 sort share 再次上升，再考虑排序视图复用的进一步细化

### 再次优化的必要条件

- 新的 benchmark 或真实 workload 证明 rolling 之外出现更大热点
- workflow report 的 fallback 命中率开始显著上升，导致快路收益下降
- grouped / segmented / IO 路径在新 workload 下进入 top bottleneck

## R18：Planner V6 与 ordered-over-cross 修复

### 背景

在 V1-V5 阶段，系统已经修复并稳定了 `cross/grouped over ordered` 这条嵌套方向，例如：

- `demean(ts_rank(...))`
- `rank(demean(ts_mean(...)))`

但真实数据 benchmark 暴露了反方向的同类问题：

- `corr(rank(open), rank(volume), 10)`

这类表达式会把横截面窗口表达式直接嵌进 ordered rolling window，结果在真实数据上退化成近乎整列 `NaN`。这说明系统虽然已经具备 staged chain 和 ordered batch fusion，但还没有覆盖 `ordered over cross/grouped` 这条执行域组合方向。

### 目标

- 修复 `corr/cov` 消费 cross/grouped 输入时的嵌套窗口语义错误
- 保持现有 public API 不变
- 让 mixed batch 里 compiled ordered、materialized ordered、staged graph 继续共用一个 prepared frame
- 不把这次修复扩张成“所有 ordered root 全面泛化”的大重构

### 任务

- 在 `planner.py` 中新增 `materialized_ordered` route
- 让 `corr/cov` 在检测到 cross/grouped 输入时，走“先物化输入，再 ordered rolling”的计划
- 在 `executor.py` 中新增 materialized ordered 执行路径
- 补齐 split-step 对照测试：
  - `corr(rank(...), rank(...), n)`
  - `cov(rank(...), rank(...), n)`
- 补齐 mixed batch prepared-frame 复用测试
- 补充 `execution_planner_v6.md`

### 验收

- `corr(rank(...), rank(...), n)` 与“先算 rank 列，再算 corr”一致
- `cov(rank(...), rank(...), n)` 与分步写法一致
- real-data 表达式 `corr(rank(open), rank(volume), 10)` 不再退化成近乎整列 `NaN`
- mixed batch 中 compiled ordered 与 materialized ordered 仍只使用一个 prepared frame
- 全量测试继续通过：
  - `.venv\\Scripts\\python -m pytest -q -> 247 passed, 1 warning`

### 风险

- 当前只修了 `corr/cov`，其余 ordered roots 仍可能存在同类问题
- `materialized_ordered` 目前只接受 compiled/staged 子输入，尚未泛化到更复杂 route 组合
- 如果过早把所有 ordered roots 一次性并入，容易把 correctness 修复和广义 DAG/CSE 重构混在一起

### 非目标

- 不把所有 `ordered over cross/grouped` 根函数一次修完
- 不在本阶段引入 full DAG/CSE
- 不改变 grouped / segmented / FFT 语义
- 不增加额外 pointer、meta、automation 机制

### 理论上最简单的时间复杂度

- 左右输入物化：保守按 `O(n)` 理解
- ordered rolling `corr/cov`：保守按 `O(n * rolling_cost)` 理解

### 当前实现复杂度

- 计划层只增加一条窄 route，不重写 staged chain
- 执行层复用现有 ordered prepared frame 与 row-order restore 机制
- batch 层继续沿用 V5 的“一个 ordered shell”思路，把 materialized ordered 纳入同一个 prepared frame

### 当前未达到理论上界的原因

- 其余 ordered roots 还没有统一进入同一套 materialization-boundary 规则
- materialized ordered 还不是更大 planner graph 的一等 reusable node
- 系统依旧优先 correctness widening，而不是先上更激进的共享子图抽取

### 对未来的建议

- 下一步先审计其余 ordered roots：
  - `ts_*`
  - `argmax / argmin`
  - `skew / kurt`
- 继续用“真实失败复现 + split-step 对照测试”决定 widening 顺序
- 只有在 failure surface 和 reuse shape 足够清晰后，再考虑把 materialized ordered 进一步纳入更通用的 DAG/CSE 规划结构

### 再次优化的必要条件

- 发现下一个明确的 `ordered over cross/grouped` 失败面
- benchmark 或真实任务证明某个 ordered root family 具有同类退化
- 需要跨多个 materialized ordered 表达式共享更多前缀或子图时，再讨论是否把这条 route 升格为更通用 graph node
- ????? materialized ordered ?????????????????????? route ?????? graph node
+ ????? materialized ordered ?????????????????????? route ?????? graph node

## R19?Ordered Correctness Audit v1

### ??

R18 ???????? `corr/cov over cross/grouped` ?????????? `materialized_ordered` ???? ordered family ?????????

- `ts_mean / ts_std / ts_sum / ts_min / ts_max / ts_median / skew / kurt` ?????????
- `argmax / argmin / ts_rank` ?????????????????? split-step ??????
- ????????????? planner ?????????ordered roots inventory + boundary rules + ??????????

?????????

- ??????? ordered roots ???????? cross/grouped ??
- ??? root ???????????????????

### ??

- ?? ordered roots inventory
- ? ordered families ???? boundary rules
- ? `argmax / argmin / ts_rank` ?? audited safe route
- ??? split-step ???? pointwise / cross / grouped child cases
- ?? ordered correctness audit ???????

### ??

- ?? `docs/ordered_roots_matrix.md`
- ?? `docs/ordered_boundary_rules.md`
- ?? `docs/ordered_correctness_audit.md`
- ?? `tests/integration/test_ordered_audit.py`
- ?? `registry.py`?? `argmax / argmin / ts_rank` ??? audited single-input ordered roots
- ?? `executor.py`?? materialized single-input ordered path ?? `argmax / argmin / ts_rank`

### ??

- ???? ordered roots ?? inventory ????
- family ? boundary rules ??? pointwise / cross / grouped / ordered ????
- `argmax(rank(close), 2)`?`argmin(rank(close), 2)`?`ts_rank(rank(close), 2)` ? split-step ????????
- grouped child cases ??? split-step / ??????
- ?????????????? ordered audited root

### ??

- ?? widening ???? `materialized_ordered` ??? `compiled` ? `staged` ????????????? route ???????????
- `ts_rank` ? materialized path ?????? rolling-rank ?????????????? correctness ????
- ????????????????????????? widened?????????????

### ???

- ??? full DAG/CSE
- ?? DSL grammar
- ?? workflow schema
- ?? performance-only refactor

### ????????????

- audited ordered roots ? materialization barrier ?????? rolling family ????????
- ??????????? asymptotic change??? correctness boundary ???

### ???????

- ???????? route widening?????? generalized graph route
- ???????? audited roots ? materialized ordered ????
- ????? family-aware split-step ???????? case-by-case patch

### ????????????

- ?????????????????????????????????????
- materialized ordered ??? full reusable node system

### ??????

- ???? ordered root ????? ordered roots matrix ? boundary rules???? planner route
- ??????? child route ????????????? + split-step ????????????????
- correctness audit ??????????? benchmark ??

### ?????????

- ? ordered root family ???? cross/grouped child expressions
- ?? audited roots ????????? child route ??
- benchmark ?? audited widening ??? family ????????????

## R20?Ordered Guardrail Hardening

### ??

R19 ????? ordered roots ? correctness audit ??????????? closure checks?

- ???? split-step ???????? planner ????? silently ? route
- ordered roots inventory ?????????? registry-backed completeness gate
- ????? audited support surface ???????? segmented child cases??????? negative coverage

### ??

- ? ordered planner ??? route-trace ????
- ? ordered audit ?? completeness gate???? root ??????
- ????????? child route ???? negative tests
- ?? row alignment?grouped-boundary?representative null behavior ???? invariant

### ??

- ? `planner.py` ???? `inspect_route(...)`
- ? `engine.py` ?? `inspect_plan(...)` ?????? route trace
- ? `registry.py` ?? ordered audit source of truth?
  - `get_ordered_roots()`
  - `get_ordered_audit_matrix()`
- ?? `tests/integration/test_ordered_audit.py`?
  - negative tests
  - route-trace tests
  - completeness tests
  - structural invariant tests
- ?? ordered audit ???????

### ??

- route assertions ??????????
- ?? rolling ordered root ???? audit matrix??????????
- segmented child unsupported surface ???????? silent fallback ?????
- representative materialized paths ???? row alignment?grouped-boundary?null behavior

### ??

- route inspection ?????????? production logging??????????????/????
- completeness gate ???? source of truth?????????????????????? source of truth ??? registry ?

### ???

- ????? ordered family ??
- ???????
- ??? DAG/CSE?workflow?DSL grammar

### ??????

- ?? widening ?????? route trace?? split-step?? completeness/doc sync????
- ? future audit ?? segmented child surface??????? boundary rules ? negative tests???? planner

## R21：Ordered Closure Documentation Sync

### 背景

R19 和 R20 已经把 ordered correctness audit 与 guardrail hardening 的已落地部分推进到代码、测试和专题文档中，但新的 closure 目标还没有完整落地到代码。此时如果继续沿用旧文档表述，就会把“当前已实现的事实”和“计划中的 closure 目标”混在一起，给后续开发和审计带来误导。

### 目标

- 停止当前轮次的代码修改
- 把 ordered 相关文档统一更新为“只描述当前已落地状态”
- 明确记录哪些 closure 项已经具备基础，哪些仍然没有完成
- 把 ordered 文档纳入正式文档导航，避免后续读者遗漏

### 任务

- 更新 `docs/index.md`，把 ordered audit / boundary / matrix 三份文档纳入阅读路径
- 更新 `docs/ordered_roots_matrix.md`，明确当前 inventory 已落地、但 canonical policy closure 尚未落地
- 更新 `docs/ordered_boundary_rules.md`，把 segmented child 的当前行为和审计边界写清楚
- 更新 `docs/ordered_correctness_audit.md`，区分当前 landed state 与 remaining closure gaps

### 验收

- ordered 文档不再把未完成 closure 表述成已完成事实
- 文档中明确区分：
  - 已落地的 audited root 覆盖
  - 已落地的 `materialized_ordered` / route inspection / completeness tests
  - 尚未落地的 canonical ordered policy、stable route contract、doc drift protection
- 文档导航中可以直接找到 ordered correctness 相关资料

### 风险

- 这是一次文档同步，不会自动修复代码中的 policy duplication 或 planner/doc drift
- `docs/history/revolution.md` 现有文件编码显示异常，新增记录虽然可读，但旧内容仍可能在部分终端里出现乱码

### 非目标

- 不继续修改 `registry.py`、`planner.py`、`engine.py`
- 不补新的 closure 测试
- 不宣称 ordered correctness closure 已经完成

### 当前状态与再次优化条件

- 当前状态：ordered audit 与 guardrail 的已落地范围已经被文档化，但 canonical policy closure 仍未完成
- 再次优化的必要条件：重新开始 ordered closure 时，必须同步推进代码、测试和文档，而不是只更新其中一层

## R22：Positional Rolling Pure-Polars Rewrite

### 背景

R17 的基线和 profile 已经说明：当前性能大头不在排序壳，也不在 parse / validate / workflow IO，而在 ordered rolling hot path。

进一步检查后发现，`argmax / argmin` 的主路径仍然是：

- `rolling_map(lambda ...)`
- 每个窗口进入一次 Python 回调
- 把窗口值转成 Python list
- 再在 Python 层扫描极值位置

这不是一个“还能继续微调”的实现，而是计算模型本身不对。它把原本应留在 Polars 表达式里的列式执行，退化成了逐窗口 Python 循环。

### 目标

- 去掉 `argmax / argmin` 主路径上的 Python callback 执行
- 保持当前 DSL 语义不变
- 在不重写整个执行引擎的前提下，把 positional rolling 明确成独立执行 family
- 用专项 benchmark 证明替换后的 pure-Polars 路径带来真实收益

### 任务

- 在 `registry.py` 中把 `argmax / argmin` 的 `window_kind` 从普通 `rolling` 改为显式 `positional`
- 在 `executor.py` 中移除 `rolling_map(lambda ...)` 主路径
- 新增 `_build_positional_rolling_extremum_expr(...)`
  - 按 `code` 分组构造显式 shift 链
  - 形成 `[x_t, x_{t-1}, ..., x_{t-window+1}]` 的 list window
  - 使用 `list.arg_max()` / `list.arg_min()`
  - 把 list 位置解释为 DSL 的“距离当前行”结果
- 保持 `materialized_ordered` 对 positional family 的支持
- 补充语义测试：
  - distance-to-current
  - 最近 tie
  - ignore null / all-null -> null
  - 多 `code` 组与乱序输入恢复
  - 不允许回退到 `rolling_map`
- 新增专项 benchmark：
  - [benchmarks/scripts/benchmark_positional_rolling.py](../../benchmarks/scripts/benchmark_positional_rolling.py)
  - [benchmarks/reports/positional_rolling.md](../../benchmarks/reports/positional_rolling.md)

### 验收

- `argmax / argmin` 主路径不再依赖 Python callback
- executor 主路径不再出现 positional rolling 的 `rolling_map`
- route inspection 可以显式看到 positional family：
  - `root_window_kind = positional`
- 语义保持不变：
  - 返回距离当前行的距离
  - ties 取最近
  - 忽略 null
  - 全 null 窗口返回 null
  - 前缀行继续使用部分窗口
- 目标测试通过：
  - `tests/integration/test_executor_new_functions.py`
  - `tests/integration/test_ordered_audit.py`
  - `tests/integration/test_engine_new_functions.py`
  - `tests/integration/test_planner.py`
  - `tests/integration/test_engine.py`
- 专项 benchmark 显示 pure-Polars 路径明显快于 legacy callback 路径

### 风险

- 当前实现虽然去掉了 Python callback，但仍然依赖显式 shift + list window 构造；窗口继续放大时，收益可能收敛
- positional family 已经从“错误计算模型”升级为“可接受的一阶段实现”，但不意味着已经达到理论最优
- 当前改动聚焦 `argmax / argmin`，不自动推广到其他 rolling family

### 非目标

- 不重写整个 rolling 引擎
- 不改变 `ts_mean / ts_std / ts_rank / corr / cov` 等其他 family 的语义
- 不引入 NumPy / Numba / Cython / Rust
- 不在本阶段做 full DAG / CSE
- 不为了更容易实现而改变 DSL 语义

### 理论上最简单的时间复杂度

- 纯 callback 模型按保守口径更接近 `O(n * w)`，并且包含明显的 Python 调度成本
- 当前 pure-Polars shift/list 模型仍会随窗口放大，但热点已回到列式表达式执行内部，而不是逐窗口 Python 调用

### 当前实现复杂度

- `argmax / argmin` 主路径现在是显式 shift + list reduction
- 小中窗口下收益显著
- 大窗口下收益仍然存在，但放大倍数会压缩

### 当前未达到理论上界的原因

- 当前实现优先完成“去掉错误计算模型”，而不是一步到位做最强 positional kernel
- list window 方案本身仍然会随窗口规模增加而扩大表达式体积

### 对未来的建议

- 先把 positional callback removal 视为一轮成功的计算模型纠偏
- 后续是否继续优化 `argmax / argmin`，应继续看专项 benchmark，而不是先入为主
- 如果未来窗口更大、positional 再次成为热点，再讨论更专门的 positional backend

### 再次优化的必要条件

- 专项 benchmark 显示大窗口 positional 仍然占显著比例
- 真实 workload 里 `argmax / argmin` 使用频率持续上升
- 需要比当前 shift/list 方案更稳定的高窗口性能

## R23：Positional Rolling Short-Window Fast Path

### 背景

R22 移除了 `argmax / argmin` 主路径上的 Python callback，但真实大数据验证继续暴露出 phase-1 list-window 模型的成本：

- `shift -> concat_list -> list.arg_max / list.arg_min`

这个模型虽然已经是 pure Polars，但在大数据量和窗口 20 这类常见场景下，list materialization 仍然会制造明显中间数据压力。

### 目标

- 为短窗口 positional rolling 增加新的 pure-Polars fast path
- 避免短窗口继续走 `concat_list` 和 `list.arg_*`
- 保持当前语义完全一致
- 保留大窗口 list fallback，不把本阶段扩大成通用 positional kernel 重写

### 任务

- 在 `executor.py` 中新增 `SHORT_WINDOW_THRESHOLD`
- 对 `window <= SHORT_WINDOW_THRESHOLD` 走 short-window fast path：
  - grouped shift
  - horizontal max/min
  - candidate-distance selection
  - 返回最近命中 offset
- 对 `window > 64` 保留 phase-1 list fallback
- 补齐测试：
  - 单调递增 / 递减
  - 常数
  - 重复极值
  - null mixed / all-null
  - leading partial windows
  - short-window fast path 与 list fallback 在 `5 / 10 / 20 / 60` 上一致
  - short-window 不调用 `concat_list`
  - large-window 仍调用 list fallback
- 扩展 positional benchmark，增加三条真实关注表达式：
  - `argmax(fill_null(close, open), 20)`
  - `argmax(ts_mean(fill_null(close, open), 20), 20)`
  - `argmax(rank(ts_mean(fill_null(close, open), 20), pct=true), 20)`

### 验收

- short-window 结果与 phase-1 list fallback 一致
- large-window fallback 保持可用
- short-window 主路径不使用 Python callback
- short-window 主路径不使用 `concat_list`
- 目标测试通过：
  - `tests/integration/test_executor_new_functions.py`
  - `tests/integration/test_ordered_audit.py`
  - `tests/integration/test_engine_new_functions.py`
  - `tests/integration/test_planner.py`
  - `tests/integration/test_engine.py`
- benchmark 已更新到 [benchmarks/reports/positional_rolling.md](../../benchmarks/reports/positional_rolling.md)

### 风险

- `SHORT_WINDOW_THRESHOLD` 是策略阈值，不代表所有小窗口在所有 workload 上都必然快
- 当前 synthetic benchmark 显示：
  - `window=5/20` 对 callback 模型收益明显
  - `window=20` 的部分 nested expression 相对 list fallback 有收益
  - `window=60` 在当前 60k synthetic workload 上 slower
- 因此这个阶段应被理解为 short-window fast path 的第一版落地，而不是 positional rolling 的最终 kernel

### 非目标

- 不修改 planner route / ordered shell / prepared frame
- 不改变 `argmax / argmin` 语义
- 不优化其他 rolling family
- 不引入外部 backend

### 当前实现复杂度

- short-window fast path 构造 `window` 个 shift 表达式
- 再构造 `window` 个 candidate-distance 表达式
- 因此它避免了 list materialization，但仍然会随窗口线性扩大表达式体积

### 对未来的建议

- 继续用真实数据 benchmark 判断阈值是否应从当前保守默认值调整
- 如果 `window=60` 或更大窗口仍是热点，需要进入 positional kernel phase 3，而不是继续堆 horizontal 表达式
- 对用户当前的窗口 20 nested 表达式，应优先用真实数据对比 phase-1 fallback 与 phase-2 fast path，而不是只看 synthetic 60k 结果

### 再次优化的必要条件

- 真实数据显示 `window=20` 仍无法满足性能目标
- 大窗口 positional 在真实 workload 中持续占据主耗时
- synthetic 与真实数据 benchmark 对最佳阈值结论明显冲突，需要重新定义 window policy

### R23.1 安全阈值修正

真实 minute parquet 上的 `argmax(..., 20)` 验证显示，默认 `64` 阈值会让 horizontal fast path 在大数据量上展开过多 shifted / candidate 表达式，导致 CPU 长时间满载、内存接近耗尽，并且无法稳定产出结果。

因此默认策略已修正为：

- `SHORT_WINDOW_THRESHOLD = 8`
- `window=20` 默认回到 phase-1 list fallback
- fast path 仍保留，可在 benchmark 中通过 monkeypatch / 显式阈值 opt-in 验证

这次修正的含义是：phase 2 fast path 继续存在，但不再默认覆盖 `window=20` 这类真实大数据下已证明有风险的窗口。

## R24：Positional Rolling Dedicated Grouped Kernel

### 背景

真实 minute parquet 上继续验证后，`argmax(..., 20)` 的主要耗时已经不在 planner、排序或子表达式上，而是在 positional rolling kernel 本身：

- phase-1 list fallback 会做 `shift -> concat_list -> list.arg_*`
- phase-2 horizontal fast path 会做 `shift -> horizontal max/min -> candidate distance`
- 这两类 pure-Polars 表达式方案本质上都还会随窗口宽度做显式展开

因此继续调阈值已经不是正确方向。本轮把 `argmax / argmin` 升级为 dedicated grouped scanning kernel。

### 改动

- 新增 `positional_ordered` route，用于普通根表达式 `argmax(x, n)` / `argmin(x, n)`
- `materialized_ordered(argmax/argmin)` 在子表达式物化后也调用同一个 dedicated kernel
- kernel 按已排序的 `code/time` frame 执行，每个 `code` group 用 monotonic deque 线性扫描
- 修正 `argmin` registry 分类，确保它和 `argmax` 一样属于 `window_kind = positional`
- 保留 phase-1/phase-2 pure-Polars expression helper，作为组合表达式 fallback 和回归对照，不再作为默认根路径

### 语义

- 窗口仍然是当前行 + 前 `n - 1` 行
- 输出仍然是 distance-to-current
- ties 取最近，因此相等值会从 deque 尾部弹出旧候选，保留更新候选
- null 不入队；全 null 窗口返回 null
- 不跨 `code` group

### 验收

- `argmax / argmin` 根路径不调用 `rolling_map`
- 默认根路径不调用 `concat_list`
- `argmax(rank(...), n)` 等 materialized ordered positional root 不调用 `concat_list`
- list fallback 对照在 `n in {5, 10, 20, 60}` 上与新 kernel 一致
- benchmark 已更新到 [benchmarks/reports/positional_rolling.md](../../benchmarks/reports/positional_rolling.md)

当前 synthetic 60k / 250 groups benchmark 中，phase-3 dedicated kernel 相对 list fallback：

- `argmax(close, 20)`：约 `11.30x`
- `argmin(close, 20)`：约 `10.79x`
- `argmax(rank(ts_mean(fill_null(close, open), 20), pct=true), 20)`：约 `10.43x`

### 后续

- Python deque kernel 是清晰、可替换的 phase-3 原型；如果真实大数据仍不满足目标，下一步应把同一语义迁移到 native backend，而不是回到表达式展开
- 仍需在真实 `data/minute_2026_03.parquet` 上复测用户关心的双窗口嵌套表达式，并记录排序、子表达式、kernel 的拆分耗时

## R25：Ordered Batch Stage Lifecycle V1/V2

### 背景

在 positional rolling phase 3 后，计算模型已经明显改善，但 ordered batch 仍然会因为显式 stage 常驻而撑宽 working frame。

当前系统已经有 ordered shell 复用、staged prefix 复用、segment spec 复用和 materialized ordered route，但缺少统一的显式 stage 生命周期观测和 drop 纪律。

### 目标

本轮只做两件事：

- V1：建立 ordered batch 显式 stage lifecycle profiling baseline
- V2：在 ordered batch 内对已无消费者的显式 stage 做保守 sweep/drop

明确不做：

- 全局 DAG/CSE
- compiled expr 子树抽取
- route 规则重写
- positional kernel native 化

### 改动

- 新增 `profiling.py`，提供 run / batch / stage / event 四层 profiling schema
- 新增 `stage_registry.py`，提供显式 stage registry 与 drop 状态管理
- `FactorEngine.evaluate_many(...)` 新增可选开关：
  - `profiling=True`
  - `profile_output_dir=...`
  - `lifecycle=True`
- ordered batch 路径记录：
  - `stage_created`
  - `stage_consumed`
  - `stage_dropped`
  - `batch_end_stage_snapshot`
- 新增 stage lifecycle benchmark：
  - [benchmarks/scripts/benchmark_stage_lifecycle.py](../../benchmarks/scripts/benchmark_stage_lifecycle.py)
  - [benchmarks/reports/stage_lifecycle.md](../../benchmarks/reports/stage_lifecycle.md)
- 新增 lifecycle 设计文档：
  - [docs/stage_lifecycle.md](stage_lifecycle.md)

### 当前策略

V2 初版采用保守 sweep：

- positional/materialized route item 输出 alias 后 sweep 一次
- ordered restore 前再 sweep 一次
- drop 时同步 working frame、stage cache、registry 和 profiling event

这不是最终的最优生命周期策略，但它能先稳定证明：显式 stage 不必默认活到 batch end。

### benchmark 当前结果

synthetic 21,600 rows benchmark 中：

- `stage_accumulation`：peak frame cols 从 `23` 降到 `16`，alive-at-end 从 `11` 降到 `0`
- `long_lived_stage`：peak frame cols 从 `19` 降到 `17`，alive-at-end 从 `9` 降到 `0`

RSS 在小样本中仍有噪声，后续应在真实 minute parquet 上继续看趋势。

### 后续

- 基于 V1/V2 profile 输出再判断是否进入 batch-level CSE
- 如果 lifecycle sweep 造成过多重算，再引入 reuse economics，而不是提前做全局 DAG
- positional kernel 的 Python list 内存问题仍属于独立的 native/backend 议题，不在本轮 lifecycle 范围内
