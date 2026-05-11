# Real Double-Window Lifecycle Benchmark

- data: `data\minute_2026_03.parquet`
- rows: `29048679`
- groups: `5495`
- expression: `argmax(ts_mean(fill_null(close, open), 20), 20)`
- results_equal: `True`

| metric | V1 baseline | V2 lifecycle | delta V2-V1 |
| --- | ---: | ---: | ---: |
| total_time_sec | 16.974941 | 16.261483 | -0.713458 |
| driver_elapsed_sec | 17.606065 | 17.011829 | -0.594235 |
| peak_rss_mb | 5708.406250 | 10876.554688 | 5168.148438 |
| peak_frame_col_count | 12 | 12 | 0 |
| peak_live_stage_count_estimate | 2 | 2 | 0 |
| alive_stage_at_batch_end_count | 2 | 0 | -2 |
| dropped_stage_count | 0 | 2 | 2 |
| total_stage_count | 2 | 2 | 0 |
