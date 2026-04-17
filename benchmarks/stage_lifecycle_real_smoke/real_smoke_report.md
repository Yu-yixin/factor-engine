# Real Data Stage Lifecycle Smoke

- dataset: `data\minute_2026_03.parquet`
- rows: `500000`
- groups: `5470`
- expressions: `5`
- results_equal: `True`

| metric | V1 profiling only | V2 lifecycle | delta V2-V1 |
| --- | ---: | ---: | ---: |
| peak_rss_mb | 266.621094 | 379.769531 | 113.148438 |
| peak_frame_col_count | 25 | 17 | -8 |
| peak_live_stage_count_estimate | 11 | 3 | -8 |
| alive_stage_at_batch_end_count | 11 | 0 | -11 |
| dropped_stage_count | 0 | 13 | 13 |
| total_time_sec | 0.834113 | 0.789077 | -0.045036 |
