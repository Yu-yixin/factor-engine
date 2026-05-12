# Rolling Operator Semantics Matrix

Status values:

- `FROZEN`
- `PARTIAL`
- `UNKNOWN`
- `DO_NOT_NATIVE_YET`
- `READY_FOR_NATIVE_PROTOTYPE`

| operator | window argument | min_samples | ddof | null behavior | NaN behavior | group boundary | row restore | current backend | golden test status | native-ready status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ts_mean` | integer `n` | Polars default/current engine contract | n/a | rolling null behavior | Polars floating behavior | `code` | ordered frame restores caller order | Polars | existing unit coverage, not frozen in matrix | `PARTIAL` |
| `ts_sum` | integer `n` | Polars default/current engine contract | n/a | rolling null behavior | Polars floating behavior | `code` | ordered frame restores caller order | Polars | existing unit coverage, not frozen in matrix | `PARTIAL` |
| `ts_std` | integer `n` | Polars default/current engine contract | Polars default | rolling null behavior | Polars floating behavior | `code` | ordered frame restores caller order | Polars | existing unit coverage, not frozen in matrix | `PARTIAL` |
| `ts_min` | integer `n` | Polars default/current engine contract | n/a | rolling null behavior | Polars floating behavior | `code` | ordered frame restores caller order | Polars | existing unit coverage, not frozen in matrix | `PARTIAL` |
| `ts_max` | integer `n` | Polars default/current engine contract | n/a | rolling null behavior | Polars floating behavior | `code` | ordered frame restores caller order | Polars | existing unit coverage, not frozen in matrix | `PARTIAL` |
| `ts_rank` | integer `n` | current engine contract | n/a | current engine contract | current engine contract | `code` | ordered frame restores caller order | Python/Polars path | not frozen here | `DO_NOT_NATIVE_YET` |
| `corr` | integer `n >= 2` | `2` | `1` | pairwise valid pairs; fewer than two pairs -> null | `NaN` remains `NaN`, not null | `code` | restored after sorted execution | Polars; native prototype opt-in | `tests/unit/test_corr_cov_golden.py` | `READY_FOR_NATIVE_PROTOTYPE` |
| `cov` | integer `n >= 2` | `2` | `1` | pairwise valid pairs; fewer than two pairs -> null | `NaN` remains `NaN`, not null | `code` | restored after sorted execution | Polars; native prototype opt-in | `tests/unit/test_corr_cov_golden.py` | `READY_FOR_NATIVE_PROTOTYPE` |
| `skew` | integer `n` | current engine contract | current engine contract | current engine contract | current engine contract | `code` | ordered frame restores caller order | Polars | `tests/unit/test_skew.py` | `PARTIAL` |
| `kurt` | integer `n` | current engine contract | current engine contract | current engine contract | current engine contract | `code` | ordered frame restores caller order | Polars | `tests/unit/test_kurt.py` | `PARTIAL` |
| `argmax` | integer `n` | first valid candidate | n/a | nulls ignored; null if no candidate | current positional contract | `code` | ordered frame restores caller order | Python plus optional native positional kernel | `tests/unit/test_execution_positional.py` | `PARTIAL` |
| `argmin` | integer `n` | first valid candidate | n/a | nulls ignored; null if no candidate | current positional contract | `code` | ordered frame restores caller order | Python plus optional native positional kernel | `tests/unit/test_execution_positional.py` | `PARTIAL` |

`corr` and `cov` are the only operators marked ready for the native prototype from this registry. The others need dedicated golden files before full native rollout.
