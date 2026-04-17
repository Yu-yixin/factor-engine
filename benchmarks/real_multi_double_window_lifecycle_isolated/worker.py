import argparse
import json
import time
from pathlib import Path

import polars as pl
from factor_engine.engine import FactorEngine

WINDOW_PAIRS = [
    (5, 5),
    (10, 10),
    (20, 20),
    (30, 20),
    (40, 20),
    (60, 20),
    (20, 5),
    (20, 10),
    (20, 30),
    (20, 40),
    (20, 60),
    (10, 20),
    (30, 30),
    (40, 40),
    (60, 60),
    (5, 20),
]

def build_expressions(count: int) -> list[tuple[str, str]]:
    expressions = []
    index = 0
    while len(expressions) < count:
        w1, w2 = WINDOW_PAIRS[index % len(WINDOW_PAIRS)]
        mode = "argmax" if index % 2 == 0 else "argmin"
        source = "close" if index % 3 else "fill_null(close, open)"
        expr = f"{mode}(ts_mean({source}, {w1}), {w2})"
        expressions.append((f"dw_{index + 1:02d}_{mode}_{w1}_{w2}", expr))
        index += 1
    return expressions

def load_summary(path: Path) -> dict[str, object]:
    return json.loads((path / "latest_run.json").read_text(encoding="utf-8"))

def checksum_frame(df: pl.DataFrame, output_cols: list[str]) -> int:
    # Stable enough for V1/V2 equality guard without writing full result parquet.
    total = 0
    for column in output_cols:
        value = df.select(pl.col(column).sum()).item()
        if value is not None:
            total += int(value)
    return total

parser = argparse.ArgumentParser()
parser.add_argument("--data", required=True)
parser.add_argument("--rows", type=int, default=0)
parser.add_argument("--out", required=True)
parser.add_argument("--expr-count", type=int, required=True)
parser.add_argument("--lifecycle", action="store_true")
parser.add_argument("--label", required=True)
args = parser.parse_args()

data = Path(args.data)
out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)

scan = pl.scan_parquet(str(data))
if args.rows > 0:
    scan = scan.limit(args.rows)
df = scan.collect()

expressions = build_expressions(args.expr_count)
output_cols = [name for name, _expr in expressions]

engine = FactorEngine(time_col="time", code_col="ths_code")

start = time.perf_counter()
result = engine.evaluate_many(
    expressions,
    df,
    profiling=True,
    lifecycle=args.lifecycle,
    profile_output_dir=out,
    benchmark_name=f"multi_double_window_{args.expr_count}_{args.label}",
    dataset_name=data.name,
)
elapsed = time.perf_counter() - start

summary = load_summary(out)
summary["driver_elapsed_sec"] = elapsed
summary["result_checksum"] = checksum_frame(result, output_cols)
summary["expression_names"] = output_cols
summary["expressions"] = expressions

(out / "driver_summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print(json.dumps(summary, ensure_ascii=False, indent=2))
