# 因子表达式引擎文档索引

这是 Factor Engine 的文档导航页，用来说明每份文档的职责边界，以及建议的阅读顺序。

## 文档分工

### 1. [README.md](../README.md)

适合谁看：

- 第一次接触项目的人
- 只想快速知道项目现在能做什么的人
- 想快速安装、运行、试用的人

回答的问题：

- 项目是什么
- 怎么安装和运行
- 当前能做什么
- 去哪里找完整语义

### 2. [language.md](language.md)

适合谁看：

- 需要确认 DSL 语法、运算符优先级和 null 规则的人
- 写复杂表达式时不想猜解析顺序的人

回答的问题：

- 当前 DSL 支持哪些表达式类型
- 运算符如何结合
- 逻辑与 null 如何处理

### 3. [functions.md](functions.md)

适合谁看：

- 需要查完整函数语义的人
- 需要确认 edge case、参数约束和最小示例的人

回答的问题：

- 每个函数做什么
- 参数和返回类型是什么
- 当前 edge case 是什么

### 4. [workflow.md](workflow.md)

适合谁看：

- 想从文件批量跑表达式的人
- 需要 parquet/csv 输出或 continue-on-error 行为的人

回答的问题：

- YAML / JSON schema 长什么样
- 严格模式和汇总模式怎么用
- 结果怎么写出

### 5. [errors.md](errors.md)

适合谁看：

- 想知道错误会在哪一层抛出的人
- 需要理解 batch failure report 格式的人

回答的问题：

- 当前有哪些错误类型
- stage 怎么分类
- `ExpressionFailure` / `BatchEvaluationReport` 长什么样

### 6. [design.md](design.md)

适合谁看：

- 需要理解当前代码结构和模块边界的人
- 准备新增函数或修改解析器、校验器、执行器的人

回答的问题：

- 当前系统怎么组织
- 核心抽象有哪些
- 模块之间怎么分工

### 7. [execution_planning_optimization.md](execution_planning_optimization.md)

适合谁看：

- 需要理解执行规划、批量执行和缓存复用的人
- 准备优化 `evaluate_many()`、`ExecutionProfile` 或 ordered path 的人

回答的问题：

- 执行画像怎么推导
- 执行器如何按需求分流
- `evaluate_many()` 如何共享执行壳

### 7.1 [execution_planner_v1.md](execution_planner_v1.md)

适合谁看：

- 想理解 staged materialization 最初为什么被引入的人
- 想确认哪些表达式会进入 staged route 的人

回答的问题：

- `planner v1` 支持哪些 route
- staged materialization 的边界是什么

### 7.2 [execution_planner_v2.md](execution_planner_v2.md)

适合谁看：

- 想理解深层链式表达式如何被压平成 staged chain 的人
- 想确认 planner 如何修复多层嵌套语义错位的人

回答的问题：

- `planner v2` 如何构建递归 staged chain
- 深层链式表达式为什么能与手工分步一致

### 7.3 [execution_planner_v3.md](execution_planner_v3.md)

适合谁看：

- 想理解为什么系统已经是 CSE-ready 但还不是 full DAG/CSE 的人
- 想确认 batch staged source/prefix 复用结构的人

回答的问题：

- `planner v3` 提供了哪些稳定 key
- planner-side batch graph 长什么样
- 当前 batch staged prefix 复用做到哪一步

### 7.4 [execution_planner_v4.md](execution_planner_v4.md)

适合谁看：

- 想理解 staged batch 执行为什么已经开始变成“节点图 + 依赖 + 输出绑定”的人
- 想确认系统距离 full DAG/CSE 还差哪一步的人

回答的问题：

- `planner v4` 的 staged node graph 长什么样
- output binding 如何把 planner 节点映射到最终输出列
- executor 如何按 planner 节点顺序执行

### 7.5 [execution_planner_v5.md](execution_planner_v5.md)

适合谁看：

- 想理解 mixed ordered batch 为什么可以少走一次 prepared frame 的人
- 想确认 compiled ordered 输出与 staged graph 现在如何共用 ordered shell 的人

回答的问题：

- `planner v5` 解决了哪一类重复 ordered 工作
- compiled ordered 与 staged graph 如何在一个 batch 里融合执行
- 这一步和 full DAG/CSE 还有什么距离

### 7.6 [ordered_correctness_audit.md](ordered_correctness_audit.md)、[ordered_boundary_rules.md](ordered_boundary_rules.md)、[ordered_roots_matrix.md](ordered_roots_matrix.md)

适合谁看：

- 需要确认 ordered roots 当前 correctness 边界的人
- 想知道哪些 ordered family 已审计、哪些组合仍然不在保证面内的人
- 准备修改 ordered planner、guardrail 或测试覆盖的人

回答的问题：

- 当前哪些 ordered roots 已进入审计范围
- `cross / grouped / ordered / segmented` 子输入分别怎么处理
- 当前文档记录的是“已经落地的事实”还是“尚未落地的 closure 目标”

### 8. [benchmark.md](benchmark.md)

适合谁看：

- 准备做阶段验收、性能对比或热点决策的人

回答的问题：

- benchmark 用什么口径
- benchmark 结果落到哪里
- 如何定义对照与复现

### 9. [revolution.md](revolution.md)

适合谁看：

- 想理解系统为什么演进成现在这样的的人
- 需要查历史决策、阶段目标和复杂度分析的人

回答的问题：

- 做过哪些系统级变更
- 每次变更的背景、目标、任务、验收、风险、非目标是什么

### 10. [documentation_policy.md](documentation_policy.md)

适合谁看：

- 想知道文档什么时候该停、什么时候值得再优化的人
- 准备修改文档或讨论功能是否继续优化的人

回答的问题：

- 文档体系什么时候停止继续优化
- 再次优化的必要条件是什么

## 推荐阅读顺序

### 路线 A：第一次了解项目

1. 先看 [README.md](../README.md)
2. 再看 [language.md](language.md) 和 [functions.md](functions.md)
3. 如果关心代码结构，再看 [design.md](design.md)
4. 如果关心历史与演进，再看 [revolution.md](revolution.md)

### 路线 B：准备改代码

1. 先看 [README.md](../README.md)
2. 再看 [language.md](language.md) 和 [functions.md](functions.md)
3. 再看 [design.md](design.md)
4. 如果改动涉及执行路径，再看 [execution_planning_optimization.md](execution_planning_optimization.md)
5. 如果改动涉及 planner，再按 `v1 -> v2 -> v3 -> v4 -> v5 -> v6` 顺序读六份 planner 文档
6. 如果改动涉及 ordered correctness，再读 [ordered_correctness_audit.md](ordered_correctness_audit.md)、[ordered_boundary_rules.md](ordered_boundary_rules.md)、[ordered_roots_matrix.md](ordered_roots_matrix.md)

### 路线 C：准备做性能优化

1. 先看 [execution_planning_optimization.md](execution_planning_optimization.md)
2. 再看 [benchmark.md](benchmark.md)
3. 再按 `v1 -> v2 -> v3 -> v4 -> v5 -> v6` 阅读 planner 文档
4. 如果优化点落在 ordered family，再补读 [ordered_correctness_audit.md](ordered_correctness_audit.md)、[ordered_boundary_rules.md](ordered_boundary_rules.md)、[ordered_roots_matrix.md](ordered_roots_matrix.md)
5. 最后回到 [design.md](design.md) 看当前代码结构落点

### 路线 D：准备跑研究工作流

1. 先看 [README.md](../README.md)
2. 再看 [workflow.md](workflow.md)
3. 如果需要错误格式，再看 [errors.md](errors.md)

## 维护规则

- `README` 只保留入口信息，不承担完整语义说明
- `language` 只维护 DSL 语法、运算符和通用 null 语义
- `functions` 只维护函数级语义和 edge case
- `workflow` 只维护文件批量、结果写出和 continue-on-error 工作流
- `errors` 只维护错误类型、错误阶段和失败载荷
- `design` 只维护当前设计，不回收完整历史过程
- `execution_planning_optimization` 只维护执行规划与优化专题
- `execution_planner_v1/v2/v3` 只维护 planner 演进路径
- `ordered_*` 文档只维护 ordered correctness 审计、边界和盘点，不提前承诺尚未落地的 closure 设计
- `benchmark` 负责 benchmark 口径与结果落点
- `revolution` 负责系统级历史演进
- `documentation_policy` 负责定义“什么时候停”和“什么时候再优化”

## 一句话索引

- 想知道“现在怎么用”：看 [README.md](../README.md)
- 想知道“表达式怎么解析”：看 [language.md](language.md)
- 想知道“函数到底怎么定义”：看 [functions.md](functions.md)
- 想知道“怎么从文件批量跑并拿到失败摘要”：看 [workflow.md](workflow.md) 和 [errors.md](errors.md)
- 想知道“现在怎么设计”：看 [design.md](design.md)
- 想知道“现在怎么执行”：看 [execution_planning_optimization.md](execution_planning_optimization.md)
- 想知道“planner 是怎么一步步演进的”：看 [execution_planner_v1.md](execution_planner_v1.md)、[execution_planner_v2.md](execution_planner_v2.md)、[execution_planner_v3.md](execution_planner_v3.md)、[execution_planner_v4.md](execution_planner_v4.md)、[execution_planner_v5.md](execution_planner_v5.md)、[execution_planner_v6.md](execution_planner_v6.md)
- 想知道“ordered correctness 现在到底保证到哪”：看 [ordered_correctness_audit.md](ordered_correctness_audit.md)、[ordered_boundary_rules.md](ordered_boundary_rules.md)、[ordered_roots_matrix.md](ordered_roots_matrix.md)
- 想知道“为什么会变成这样”：看 [revolution.md](revolution.md)
- 想知道“什么时候该停、什么时候再优化”：看 [documentation_policy.md](documentation_policy.md)
