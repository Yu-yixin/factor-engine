# 分段真实工作负载基准（R12）

日期：2026-04-14

环境：
- Python：3.13.13
- Polars：1.39.3
- 源数据：`C:\Users\yuyix\Desktop\factor-engine\data\minute_2026_03.parquet`
- 输入形态：真实日内 parquet，归一化到 `time / code / open / close / volume`
- 工作负载构造：从真实分布中抽取每个 code 不均匀的样本长度，再打乱顺序以保留乱序输入特征

## 工作负载统计

| 档位 | 行数 | 代码数 | 最小分组长度 | 分组长度中位数 | 最大分组长度 |
| --- | ---: | ---: | ---: | ---: | ---: |
| S | 10,000 | 3 | 241 | 4457.0 | 5302 |
| M | 100,000 | 30 | 241 | 4097.0 | 5302 |
| L | 1,000,000 | 205 | 241 | 5302.0 | 5302 |

## 阶段拆解（`seg_mean/seg_sum/seg_count`，同 count x3 代表场景）

| 档位 | 排序（秒） | segmented 视图构造（秒） | 聚合加广播（秒） | 恢复顺序（秒） | 视图占比 |
| --- | ---: | ---: | ---: | ---: | ---: |
| S | 0.006457 | 0.003361 | 0.001558 | 0.001826 | 25.5% |
| M | 0.012324 | 0.013569 | 0.005660 | 0.003663 | 38.5% |
| L | 0.168069 | 0.168287 | 0.039079 | 0.029759 | 41.5% |

## 总耗时

| 档位 | 场景 | 均值（秒） | 最小值（秒） | 最大值（秒） | 重复次数 |
| --- | --- | ---: | ---: | ---: | ---: |
| S | evaluate(seg_mean(close, 3)) | 0.006687 | 0.006051 | 0.007402 | 5 |
| S | serial same-count x3 | 0.019987 | 0.018203 | 0.022379 | 5 |
| S | evaluate_many same-count x3 | 0.009025 | 0.008431 | 0.010326 | 5 |
| S | serial different-count x3 | 0.021233 | 0.020115 | 0.022231 | 5 |
| S | evaluate_many different-count x3 | 0.017059 | 0.015623 | 0.018363 | 5 |
| S | evaluate(ts_mean(close, 10) - seg_mean(close, 3)) | 0.006983 | 0.006590 | 0.007293 | 5 |
| S | evaluate(where(close > seg_mean(close, 3), close, open)) | 0.007162 | 0.006609 | 0.007782 | 5 |
| M | evaluate(seg_mean(close, 3)) | 0.031102 | 0.028541 | 0.033122 | 3 |
| M | serial same-count x3 | 0.090356 | 0.088383 | 0.092539 | 3 |
| M | evaluate_many same-count x3 | 0.030527 | 0.028848 | 0.033013 | 3 |
| M | serial different-count x3 | 0.119309 | 0.090488 | 0.175780 | 3 |
| M | evaluate_many different-count x3 | 0.067570 | 0.061824 | 0.076065 | 3 |
| M | evaluate(ts_mean(close, 10) - seg_mean(close, 3)) | 0.030817 | 0.029394 | 0.031552 | 3 |
| M | evaluate(where(close > seg_mean(close, 3), close, open)) | 0.029832 | 0.029102 | 0.031271 | 3 |
| L | evaluate(seg_mean(close, 3)) | 0.348675 | 0.348675 | 0.348675 | 1 |
| L | serial same-count x3 | 0.949186 | 0.949186 | 0.949186 | 1 |
| L | evaluate_many same-count x3 | 0.324839 | 0.324839 | 0.324839 | 1 |
| L | serial different-count x3 | 0.951346 | 0.951346 | 0.951346 | 1 |
| L | evaluate_many different-count x3 | 0.657541 | 0.657541 | 0.657541 | 1 |
| L | evaluate(ts_mean(close, 10) - seg_mean(close, 3)) | 0.416934 | 0.416934 | 0.416934 | 1 |
| L | evaluate(where(close > seg_mean(close, 3), close, open)) | 0.335718 | 0.335718 | 0.335718 | 1 |

## 问题 1 / 2 / 3 / 4

- Q1: 在 `L` 档真实 workload 里，segmented view 构造约占 stage benchmark 的 `41.5%`；这能直接判断 `segment_id` 和分段准备是否还是主要瓶颈。
- Q2: `L` 档里，`evaluate_many same-count x3 / serial same-count x3 = 0.34`。 这个比值越低，说明同一 `segment_count` 的 prepared view 复用越有真实价值。
- Q3: `L` 档里，`evaluate_many different-count x3 / evaluate_many same-count x3 = 2.02`。 如果不同 `segment_count` 明显更贵，后续优化就应该围绕跨 count 成本边界，而不是继续盲目扩函数。
- Q4: `L` 档里，`mixed(ts_mean - seg_mean) / single(seg_mean) = 1.20`。 这个比值用来判断 segmented 在 mixed workload 里的额外负担是否已经足够可控。
