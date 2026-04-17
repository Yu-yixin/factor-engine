import argparse
import json
import time
from pathlib import Path

import polars as pl
from factor_engine.engine import FactorEngine

parser = argparse.ArgumentParser()
parser.add_argument("--data", required=True)
parser.add_argument("--rows", type=int, default=0)
parser.add_argument("--out", required=True)
parser.add_argument("--lifecycle", action="store_true")
parser.add_argument("--label", required=True)
args = parser.parse_args()

data = Path(args.data)
out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)

exprs = [
    ("double_window_argmax", "argmax(ts_mean(fill_null(close, open), 20), 20)"),
]

scan = pl.scan_parquet(str(data))
if args.rows > 0:
    scan = scan.limit(args.rows)
df = scan.collect()

engine = FactorEngine(time_col="time", code_col="ths_code")

start = time.perf_counter()
result = engine.evaluate_many(
    exprs,
    df,
    profiling=True,
    lifecycle=args.lifecycle,
    profile_output_dir=out,
    benchmark_name=f"isolated_double_window_{args.label}",
    dataset_name=data.name,
)
elapsed = time.perf_counter() - start

summary = json.loads((out / "latest_run.json").read_text(encoding="utf-8"))
summary["driver_elapsed_sec"] = elapsed
summary["result_checksum"] = result.select(pl.col("double_window_argmax").sum()).item()
(out / "driver_summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print(json.dumps(summary, ensure_ascii=False, indent=2))
