# 分段基准 v1

日期：2026-04-14

环境：
- Python：3.13.13
- Polars：1.39.3
- 输入形态：带乱序行顺序的合成不均匀多 code 数据集

数据集档位：
- `S`：目标约 10,000 行
- `M`：目标约 100,000 行
- `L`：目标约 1,000,000 行

## 阶段拆解（`seg_mean(close, 3)`）

| 档位 | 行数 | 排序（秒） | `segment_id` 构造（秒） | 聚合加广播（秒） | 分段占比 |
| --- | ---: | ---: | ---: | ---: | ---: |
| S | 10,000 | 0.000971 | 0.004911 | 0.001782 | 64.1% |
| M | 100,000 | 0.004031 | 0.012639 | 0.003364 | 63.1% |
| L | 1,000,000 | 0.031060 | 0.088192 | 0.022896 | 62.0% |

## 总耗时

| 档位 | 行数 | 场景 | 均值（秒） | 最小值（秒） | 最大值（秒） | 重复次数 |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| S | 10,000 | evaluate(seg_mean(close, 3)) | 0.005667 | 0.005079 | 0.006028 | 5 |
| S | 10,000 | serial same-count x3 | 0.017409 | 0.015817 | 0.019840 | 5 |
| S | 10,000 | evaluate_many same-count x3 | 0.006379 | 0.006046 | 0.007119 | 5 |
| S | 10,000 | serial different-count x2 | 0.011705 | 0.010562 | 0.013349 | 5 |
| S | 10,000 | evaluate_many different-count x2 | 0.010832 | 0.009819 | 0.011598 | 5 |
| S | 10,000 | evaluate(where(close > seg_mean(close, 3), close, open)) | 0.006288 | 0.005343 | 0.007402 | 5 |
| S | 10,000 | evaluate(ts_mean(close, 5) - seg_mean(close, 3)) | 0.006463 | 0.005834 | 0.006990 | 5 |
| M | 100,000 | evaluate(seg_mean(close, 3)) | 0.020688 | 0.017780 | 0.023026 | 3 |
| M | 100,000 | serial same-count x3 | 0.058555 | 0.058128 | 0.059359 | 3 |
| M | 100,000 | evaluate_many same-count x3 | 0.036636 | 0.018506 | 0.071764 | 3 |
| M | 100,000 | serial different-count x2 | 0.038207 | 0.034864 | 0.040517 | 3 |
| M | 100,000 | evaluate_many different-count x2 | 0.032495 | 0.031116 | 0.033739 | 3 |
| M | 100,000 | evaluate(where(close > seg_mean(close, 3), close, open)) | 0.017541 | 0.017216 | 0.017971 | 3 |
| M | 100,000 | evaluate(ts_mean(close, 5) - seg_mean(close, 3)) | 0.019038 | 0.017770 | 0.019858 | 3 |
| L | 1,000,000 | evaluate(seg_mean(close, 3)) | 0.154044 | 0.154044 | 0.154044 | 1 |
| L | 1,000,000 | serial same-count x3 | 0.484041 | 0.484041 | 0.484041 | 1 |
| L | 1,000,000 | evaluate_many same-count x3 | 0.140860 | 0.140860 | 0.140860 | 1 |
| L | 1,000,000 | serial different-count x2 | 0.367104 | 0.367104 | 0.367104 | 1 |
| L | 1,000,000 | evaluate_many different-count x2 | 0.272283 | 0.272283 | 0.272283 | 1 |
| L | 1,000,000 | evaluate(where(close > seg_mean(close, 3), close, open)) | 0.166341 | 0.166341 | 0.166341 | 1 |
| L | 1,000,000 | evaluate(ts_mean(close, 5) - seg_mean(close, 3)) | 0.224661 | 0.224661 | 0.224661 | 1 |

## 问题 1 / 2 / 3

- Q1: 在 `L` 档里，`segment_id` 构造约占 stage benchmark 的 `62.0%`；当前结果说明 segmented v1 的主瓶颈已经更偏向 `segment_id` 预处理，而不是排序本身。
- Q2: `L` 档里，`evaluate_many same-count x3 / serial same-count x3 = 0.29`。如果该比值接近 1，说明同一 `segment_count` 下重复预处理仍然明显，没有得到有效复用。
- Q3: `L` 档里，`evaluate_many different-count x2 / single = 1.77`。如果不同 `segment_count` 场景明显高于单表达式且没有同-count 优势，就说明后续需要按 `segment_count` 做 prepared view 复用。
