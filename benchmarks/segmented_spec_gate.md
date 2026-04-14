# 分段规格闸门基准（R13.5-B）

日期：2026-04-14

环境：
- Python：3.13.13
- Polars：1.39.3
- 源数据：`C:\Users\yuyix\Desktop\factor-engine\data\minute_2026_03.parquet`
- 输入形态：真实日内 parquet，归一化到 `time / code / open / close / volume`
- 工作负载构造：先为每个选中 code 截取前 `8` 行，再复制成带后缀的 code id，既保证 PoC 长度规格合法，也保留乱序输入特征
- R13.5 备注：`[3,5,2]`、`[2,2,2,2]` 这类长度规格要求完整覆盖分组，所以这个闸门测试从设计上就使用较短的每 code 切片

## 工作负载统计

| 档位 | 行数 | 代码数 | 最小分组长度 | 分组长度中位数 | 最大分组长度 |
| --- | ---: | ---: | ---: | ---: | ---: |
| S | 10,000 | 1,260 | 4 | 8.0 | 8 |
| M | 100,000 | 12,544 | 6 | 8.0 | 8 |
| L | 500,000 | 62,528 | 7 | 8.0 | 8 |

## 场景指标

| 档位 | 场景 | 总均值（秒） | 视图构造（秒） | 聚合（秒） | 缓存命中率 | prepare 调用次数 | 视图请求次数 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S | evaluate(seg_mean(close, 3)) | 0.012893 | 0.007369 | 0.002066 | 0.00 | 1 | 1 |
| S | evaluate(seglen_mean(close, [3,5,2])) | 0.010599 | 0.005341 | 0.001737 | 0.00 | 1 | 1 |
| S | evaluate_many same-length x3 | 0.012939 | 0.004195 | 0.003755 | 0.67 | 1 | 3 |
| S | evaluate_many different-length x3 | 0.027005 | 0.014113 | 0.005029 | 0.00 | 3 | 3 |
| S | evaluate_many mixed count+length | 0.018214 | 0.009819 | 0.003259 | 0.00 | 2 | 2 |
| S | diversity sweep (1 unique spec) | 0.019258 | 0.016934 | 0.002564 | 0.00 | 1 | 1 |
| S | diversity sweep (2 unique specs) | 0.019022 | 0.008758 | 0.003801 | 0.00 | 2 | 2 |
| S | diversity sweep (4 unique specs) | 0.033965 | 0.020248 | 0.008681 | 0.00 | 4 | 4 |
| S | diversity sweep (8 unique specs) | 0.065258 | 0.039705 | 0.015220 | 0.00 | 8 | 8 |
| M | evaluate(seg_mean(close, 3)) | 0.057235 | 0.021078 | 0.010634 | 0.00 | 1 | 1 |
| M | evaluate(seglen_mean(close, [3,5,2])) | 0.051511 | 0.021843 | 0.008153 | 0.00 | 1 | 1 |
| M | evaluate_many same-length x3 | 0.085242 | 0.020251 | 0.012888 | 0.67 | 1 | 3 |
| M | evaluate_many different-length x3 | 0.136070 | 0.072539 | 0.039263 | 0.00 | 3 | 3 |
| M | evaluate_many mixed count+length | 0.097446 | 0.042986 | 0.025976 | 0.00 | 2 | 2 |
| M | diversity sweep (1 unique spec) | 0.073032 | 0.019371 | 0.009066 | 0.00 | 1 | 1 |
| M | diversity sweep (2 unique specs) | 0.093735 | 0.054563 | 0.027144 | 0.00 | 2 | 2 |
| M | diversity sweep (4 unique specs) | 0.169110 | 0.109468 | 0.093570 | 0.00 | 4 | 4 |
| M | diversity sweep (8 unique specs) | 0.356511 | 0.183097 | 0.101107 | 0.00 | 8 | 8 |
| L | evaluate(seg_mean(close, 3)) | 0.315605 | 0.134188 | 0.065679 | 0.00 | 1 | 1 |
| L | evaluate(seglen_mean(close, [3,5,2])) | 0.297955 | 0.105549 | 0.047022 | 0.00 | 1 | 1 |
| L | evaluate_many same-length x3 | 0.356934 | 0.111392 | 0.062631 | 0.67 | 1 | 3 |
| L | evaluate_many different-length x3 | 0.696985 | 0.321879 | 0.152756 | 0.00 | 3 | 3 |
| L | evaluate_many mixed count+length | 0.352534 | 0.171279 | 0.071961 | 0.00 | 2 | 2 |
| L | diversity sweep (1 unique spec) | 0.215805 | 0.091905 | 0.031884 | 0.00 | 1 | 1 |
| L | diversity sweep (2 unique specs) | 0.348312 | 0.168652 | 0.095510 | 0.00 | 2 | 2 |
| L | diversity sweep (4 unique specs) | 0.586813 | 0.348561 | 0.147061 | 0.00 | 4 | 4 |
| L | diversity sweep (8 unique specs) | 1.263931 | 0.719547 | 0.326791 | 0.00 | 8 | 8 |

## 闸门问题

- Q1：在最大档位上，`single(length) / single(count) = 0.94`。
- Q2：在最大档位上，`diversity(8) / (diversity(1) * 8) = 0.73`。
- Q3：在最大档位上，`mixed(count+length) / (single(count) + single(length)) = 0.57`。

## 闸门结论

- 结论：`GOOD`
- 下一步：`seglen` 家族可以进入 Phase 7 扩展。
