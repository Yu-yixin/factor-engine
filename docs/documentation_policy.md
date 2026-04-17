# 因子表达式引擎文档治理策略

本文档定义 Factor Engine 当前的文档治理规则、停止优化标准，以及再次优化的必要条件。目标不是让文档无限变多，而是让文档体系在短时间内保持稳定、低重复、可维护。

## 1. 目标

当前文档治理的目标是：

- 让每份文档只承担一种主要职责
- 让“当前真相”和“历史演进”分开维护
- 让 benchmark、复杂度、执行规划、架构设计各有固定落点
- 让后续功能开发时，知道应该改哪份文档
- 让文档体系在短时间内不需要继续结构性重构

## 2. 当前文档职责矩阵

### [README.md](../README.md)

- 当前项目说明书
- 当前能力、限制、安装、快速开始、入口函数

### [index.md](index.md)

- 文档导航页
- 文档阅读顺序
- 文档维护规则入口

### [design.md](design.md)

- 当前系统设计
- 模块分工、核心抽象、扩展方式

### [language.md](language.md)

- DSL 语法
- 运算符优先级
- 通用逻辑 / null 语义

### [functions.md](functions.md)

- 完整函数参考
- 参数、返回类型、edge case、最小示例

### [workflow.md](workflow.md)

- 文件批次 schema
- 严格模式 / 汇总模式
- 结果写出

### [errors.md](errors.md)

- 错误类型
- 错误阶段
- 失败载荷与批量报告格式

### [execution_planning_optimization.md](execution_planning_optimization.md)

- 当前执行规划专题
- `ExecutionProfile`、执行分流、`evaluate_many()`、`PreparedFrame`、缓存配合

### [benchmark.md](benchmark.md)

- benchmark 口径
- benchmark 数据样本、表达式集合、记录格式
- benchmark 结果的固定落点

### [revolution.md](revolution.md)

- 系统级历史演进
- 复杂度演进
- 阶段性决策与再次优化条件

## 3. 短期停止继续优化的评价标准

满足以下条件后，文档体系应视为“短期冻结”，不再继续做结构性优化：

1. 新人只看 `README` 就能完成安装、运行最小例子、理解当前能力边界。
2. 需要 DSL 语义时只看 `language + functions` 就能找到答案。
3. 开发者只看 `index + design` 就能知道当前代码结构与改动入口。
4. 涉及执行路径的问题只需要看 `execution_planning_optimization`，不需要再去 `README` 或 `revolution` 里翻方案。
5. 历史演进、复杂度、阶段判断都能在 `revolution` 中查到，不需要继续堆回首页。
6. benchmark 已经有固定落点，不再需要把性能记录散落在多个文档里。
7. 同一条信息不再同时由三份以上文档重复维护。
8. 同一术语在不同文档里没有冲突定义。

只要以上八条同时成立，短时间内就不应再继续优化文档结构本身。

## 4. 再次优化文档体系的必要条件

只有满足以下至少一条，才重新开启文档体系级重构：

- 文档职责再次明显重叠，导致同一事实需要在多处同步改动
- 新增一类长期存在的专题内容，但当前没有稳定落点
- 新人或开发者在 onboarding 中反复找不到正确文档入口
- benchmark、复杂度、当前真相再次混回同一份文档
- `README` 再次膨胀成规范文档而不是入口文档
- 文档更新流程已经无法支持当前开发节奏

如果只是小幅内容变更、函数新增、测试补充，不构成再次优化文档体系的理由。

## 5. 文档更新规则

### 改动当前行为时

- 更新 `README`

### 改动 DSL 语法、优先级或通用 null 语义时

- 更新 `language`

### 改动函数参数、返回语义或 edge case 时

- 更新 `functions`

### 改动文件驱动 workflow、结果写出或 continue-on-error 行为时

- 更新 `workflow`

### 改动错误类型、错误阶段或失败载荷时

- 更新 `errors`

### 改动当前系统结构时

- 更新 `design`

### 改动文件驱动 workflow、结果写出或错误汇总时
- 若属于阶段性里程碑，再追加 `revolution`

### 改动执行路径、批量执行、缓存与分流时

- 更新 `execution_planning_optimization`

### 追加 benchmark 口径或记录 benchmark 结果时

- 更新 `benchmark`

### 出现系统级里程碑变更时

- 在 `revolution` 追加记录

## 6. 功能与模块的再次优化必要条件总表

下面这张表定义“当前哪些东西已经足够稳定，不需要继续优化；什么时候才值得再次动它”。

### 6.1 词法 / 语法 / 抽象语法树

当前状态：

- 已满足原型级表达式系统需求
- 支持当前 DSL 边界内的解析与 AST 构造
- 已支持逻辑运算与受限 list literal

再次优化的必要条件：

- 需要引入属性访问、字符串字面量或新的语法层能力
- AST 节点设计开始阻碍校验器 / 执行器扩展
- 解析器复杂度或错误定位质量成为明显问题

### 6.2 `FunctionSpec` / `Validator` / `ExecutionProfile`

当前状态：

- 已能稳定描述函数语义、输入约束和 AST 级执行需求

再次优化的必要条件：

- 新函数类别无法被当前 `FunctionSpec` 字段表达
- 混合画像 AST 的执行画像频繁失真
- 新的结果类型或更复杂的 column / table 组合边界出现

### 6.3 逐点计算与截面计算基线能力

当前状态：

- 已从统一有序执行路径中拆出
- 当前收益已经足够明显

再次优化的必要条件：

- benchmark 证明 pointwise / cross-sectional 路径重新出现明显固定开销
- 新增函数让它们不得不频繁走保守重路径
- 截面函数需要独立 path 才能获得稳定收益

### 6.3.1 行业内截面函数族

包含：

- `group_demean`
- `group_zscore`
- `group_rank`

当前状态：

- 已通过显式 `group_*` family 落地
- 当前语义冻结为按 `[time, group_col]` 分组
- `group_col` 当前要求直接列引用

再次优化的必要条件：

- 需要支持多列 group key 或派生 group 表达式
- benchmark 证明 grouped rank 成为明显热点
- 用户开始要求把 grouped 语义回灌进 `demean / zscore / rank` 原函数签名

### 6.4 基础时序函数族

包含：

- `delay`
- `delta`
- `pct_change`
- `ts_min / ts_max / ts_mean / ts_sum / ts_std`
- `corr / cov / skew / kurt`

当前状态：

- 批量历史计算已经可用，语义边界稳定

再次优化的必要条件：

- benchmark 证明有序执行路径仍是系统主要瓶颈
- 出现明确的在线增量更新需求
- 当前 rolling 后端的行为或数值边界反复引发问题

### 6.5 布尔时序原语

包含：

- `ts_count`
- `ts_any`
- `ts_all`

当前状态：

- 语义已经固定，`null` 统一按 `false` 处理

再次优化的必要条件：

- 真实场景需要不同的 `null` 语义
- benchmark 证明这三类函数成为热点
- 系统进入流式或增量状态维护阶段

### 6.6 `ts_rank`

当前状态：

- 第一版正确性已闭环
- 不承诺热路径最优性能

再次优化的必要条件：

- benchmark 证明它在真实 workload 中是明显热点
- 窗口增大后耗时远高于同类 rolling 函数
- 需要更复杂的 tie-handling 或更强的排名语义

### 6.7 表级路径与 `fft`

当前状态：

- `fft(close)` 语义边界稳定
- 2 的幂长度输入已有 radix-2 快路径

再次优化的必要条件：

- benchmark 证明 FFT 是真实热点
- 非 2 的幂长度输入占主流且当前 fallback 成本过高
- 需要引入更多 table-valued expression
- 需要链式频域访问能力，迫使 table 类型系统扩展

### 6.8 `evaluate_many()` 与 `PreparedFrame`

当前状态：

- 已支持列级批量执行
- 已能共享有序执行路径的排序壳

再次优化的必要条件：

- benchmark 证明批量执行中仍存在明显重复预处理
- 需要支持表级表达式批量执行
- 需要更细粒度的分桶或更复杂的混合画像调度

### 6.9 编译缓存

当前状态：

- 已具备实例级 LRU 编译缓存
- 已覆盖 AST、`ValidationResult`、已编译表达式

再次优化的必要条件：

- benchmark 证明 compile 层仍占明显比例
- 需要冷缓存 / 热缓存可观测性或 clear cache 支撑 benchmark
- 命中率、内存占用或 schema churn 暴露出新问题
- 出现跨表达式公共子树复用的强需求

### 6.10 Benchmark 体系

当前状态：

- 已有固定文档落点
- 还需要持续补真实数据记录

再次优化的必要条件：

- 当前 benchmark 无法支持 P0/P1/P2 决策
- benchmark 口径反复被误解或无法复现
- 新增一类重要 workload，但当前 benchmark 没有覆盖

### 6.11 Segmented Length Family

包含：

- `seglen_mean`
- `seglen_sum`
- `seglen_count`
- `seglen_any`
- `seglen_all`

当前状态：

- 已形成第一版完整 family
- 与长度规格校验、under-cover 报错、over-cover 截断规则保持一致

再次优化的必要条件：

- 需要支持更多 `seglen_*` 聚合或排序类函数
- 需要支持非 literal 长度规格
- benchmark 证明长度规格多样性重新成为明显瓶颈

### 6.12 研究工作流 Helper

包含：

- `load_expression_file`
- `evaluate_expression_file`
- `evaluate_expression_file_report`
- `write_result`

当前状态：

- 已支持固定 schema 的 YAML / JSON 文件输入
- 已支持 parquet / csv 输出
- 已支持 workflow 边界的结构化失败汇总

再次优化的必要条件：

- 当前固定 schema 不能支撑真实工作流
- 用户开始要求 plain text、版本化 schema、运行参数或 richer metadata
- 失败汇总需要 partial retry、重跑或更稳定的机器可消费协议

### 6.13 错误分层与汇总

当前状态：

- 底层表达式异常与 workflow 异常已经分层
- `evaluate_many()` 仍保持原有 fail-fast 语义
- 汇总模式当前只在 workflow helper 边界提供

再次优化的必要条件：

- 需要跨 engine / CLI / notebook 一致的错误展示协议
- 当前 stage 分类不足以支撑用户定位
- 批量工作流开始需要更复杂的错误恢复策略

## 7. 实施顺序规则

当未来出现“要不要优化”的讨论时，按以下顺序判断：

1. 先看是否存在 correctness 问题
2. 再看是否存在 benchmark 证据
3. 再看是否已经影响开发效率或用户理解
4. 只有满足前面条件，才讨论是否值得投入结构性优化

如果没有 benchmark、没有错误、没有反复的使用痛点，就默认不继续优化。

## 8. 一句话结论

当前这轮治理完成后的默认状态应该是：

> 文档体系短期冻结，功能体系按 benchmark 和 correctness 驱动优化，而不是继续做“为了更整齐而优化”的文档或结构重构。
