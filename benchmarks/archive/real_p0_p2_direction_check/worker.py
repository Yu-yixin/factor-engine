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
    (15, 15),
    (25, 25),
    (35, 20),
    (45, 20),
]

def build_expressions(count: int) -> list[tuple[str, str]]:
    expressions = []
    for index in range(count):
        inner, outer = WINDOW_PAIRS[index % len(WINDOW_PAIRS)]
        mode = "argmax" if index % 2 == 0 else "argmin"
        source = "fill_null(close, open)" if index % 3 == 0 else "close"
        expr = f"{mode}(ts_mean({source}, {inner}), {outer})"
        expressions.append((f"pos_{index + 1:02d}_{mode}_{inner}_{outer}", expr))
    return expressions

def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

def checksum_frame(df: pl.DataFrame, output_cols: list[str]) -> int:
    total = 0
    for column in output_cols:
        value = df.select(pl.col(column).sum()).item()
        if value is not None:
            total += int(value)
    return total

def summarize_phases(profile_dir: Path) -> dict:
    phases = read_jsonl(profile_dir / "latest_positional_phase_details.jsonl")
    return {
        "phase_count": len(phases),
        "child_expr_total_ms": sum(float(x["child_expr_time_ms"]) for x in phases),
        "positional_total_ms": sum(float(x["positional_total_time_ms"]) for x in phases),
        "positional_to_list_total_ms": sum(float(x["positional_to_list_time_ms"]) for x in phases),
        "positional_group_scan_total_ms": sum(float(x["positional_group_scan_time_ms"]) for x in phases),
        "result_attach_total_ms": sum(float(x["result_attach_time_ms"]) for x in phases),
        "python_kernel_used": any(bool(x["python_kernel_used"]) for x in phases),
        "max_group_size": max([int(x["max_group_size"]) for x in phases], default=0),
        "avg_group_size": (
            sum(float(x["avg_group_size"]) for x in phases) / len(phases)
            if phases else 0.0
        ),
    }

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
    benchmark_name=f"direction_check_{args.expr_count}_{args.label}",
    dataset_name=data.name,
)
driver_elapsed = time.perf_counter() - start

summary = read_json(out / "latest_run.json")
phase_summary = summarize_phases(out)

summary["driver_elapsed_sec"] = driver_elapsed
summary["result_checksum"] = checksum_frame(result, output_cols)
summary["phase_summary"] = phase_summary
summary["expression_names"] = output_cols
summary["expressions"] = expressions

(out / "driver_summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print(json.dumps(summary, ensure_ascii=False, indent=2))
