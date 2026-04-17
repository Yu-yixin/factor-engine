from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import polars as pl

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from factor_engine.engine import FactorEngine  # noqa: E402


WINDOW_PAIRS = [
    (5, 5), (10, 10), (20, 20), (30, 20), (40, 20),
    (60, 20), (20, 5), (20, 10), (20, 30), (20, 40),
    (20, 60), (10, 20), (30, 30), (40, 40), (60, 60),
    (5, 20), (15, 15), (25, 25), (35, 20), (45, 20),
]


def build_expressions(count: int) -> list[tuple[str, str]]:
    expressions: list[tuple[str, str]] = []
    for index in range(count):
        inner, outer = WINDOW_PAIRS[index % len(WINDOW_PAIRS)]
        mode = "argmax" if index % 2 == 0 else "argmin"
        source = "fill_null(close, open)" if index % 3 == 0 else "close"
        expressions.append(
            (
                f"pos_{index + 1:02d}_{mode}_{inner}_{outer}",
                f"{mode}(ts_mean({source}, {inner}), {outer})",
            )
        )
    return expressions


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def summarize_phases(profile_dir: Path) -> dict[str, object]:
    run = json.loads((profile_dir / "latest_run.json").read_text(encoding="utf-8"))
    phases = read_jsonl(profile_dir / "latest_positional_phase_details.jsonl")
    total_to_list = sum(float(item["positional_to_list_time_ms"]) for item in phases)
    total_scan = sum(float(item["positional_group_scan_time_ms"]) for item in phases)
    total_attach = sum(float(item["result_attach_time_ms"]) for item in phases)
    total_child = sum(float(item["child_expr_time_ms"]) for item in phases)
    total_positional = sum(float(item["positional_total_time_ms"]) for item in phases)
    return {
        "expression_count": run["expression_count"],
        "row_count": run["row_count"],
        "group_count": run["group_count"],
        "total_time_sec": run["total_time_sec"],
        "peak_rss_mb": run["peak_rss_mb"],
        "peak_frame_col_count": run["peak_frame_col_count"],
        "phase_count": len(phases),
        "child_expr_total_ms": total_child,
        "positional_total_ms": total_positional,
        "positional_to_list_total_ms": total_to_list,
        "positional_group_scan_total_ms": total_scan,
        "result_attach_total_ms": total_attach,
        "python_kernel_used": any(bool(item["python_kernel_used"]) for item in phases),
        "native_kernel_used": any(bool(item["native_kernel_used"]) for item in phases),
        "native_low_copy_bridge_used": any(
            bool(item.get("native_low_copy_bridge_used", False)) for item in phases
        ),
        "python_object_bridge_used": any(
            bool(item.get("python_object_bridge_used", False)) for item in phases
        ),
        "native_parallel_used": any(bool(item.get("native_parallel_used", False)) for item in phases),
    }


def parse_counts(raw: str) -> list[int]:
    return [int(part.strip()) for part in raw.split(",") if part.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Profile positional argmax/argmin phase timings on real or synthetic data."
    )
    parser.add_argument("--data", type=Path, default=PROJECT_ROOT / "data" / "minute_2026_03.parquet")
    parser.add_argument("--rows", type=int, default=500_000, help="0 means full parquet.")
    parser.add_argument("--expr-counts", default="1,8,16,20")
    parser.add_argument("--code-col", default="ths_code")
    parser.add_argument("--time-col", default="time")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "benchmarks" / "positional_phases",
    )
    parser.add_argument("--lifecycle", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scan = pl.scan_parquet(str(args.data))
    if args.rows > 0:
        scan = scan.limit(args.rows)
    df = scan.collect()

    output_root = args.output
    shutil.rmtree(output_root, ignore_errors=True)
    output_root.mkdir(parents=True, exist_ok=True)

    summaries: list[dict[str, object]] = []
    for count in parse_counts(args.expr_counts):
        profile_dir = output_root / f"expr_{count}"
        FactorEngine(time_col=args.time_col, code_col=args.code_col).evaluate_many(
            build_expressions(count),
            df,
            profiling=True,
            lifecycle=args.lifecycle,
            profile_output_dir=profile_dir,
            benchmark_name=f"positional_phase_expr_{count}",
            dataset_name=args.data.name,
        )
        summaries.append(summarize_phases(profile_dir))

    lines = [
        "# Positional Phase Benchmark",
        "",
        f"- data: `{args.data}`",
        f"- rows: `{df.height}`",
        f"- lifecycle: `{args.lifecycle}`",
        "",
        "| exprs | total sec | peak rss mb | peak cols | child ms | bridge ms | positional ms | scan ms | attach ms | python | native | low-copy | parallel |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |",
    ]
    for item in summaries:
        lines.append(
            f"| {item['expression_count']} | {float(item['total_time_sec']):.6f} | "
            f"{float(item['peak_rss_mb']):.2f} | {item['peak_frame_col_count']} | "
            f"{float(item['child_expr_total_ms']):.3f} | "
            f"{float(item['positional_to_list_total_ms']):.3f} | "
            f"{float(item['positional_total_ms']):.3f} | "
            f"{float(item['positional_group_scan_total_ms']):.3f} | "
            f"{float(item['result_attach_total_ms']):.3f} | "
            f"{item['python_kernel_used']} | {item['native_kernel_used']} | "
            f"{item['native_low_copy_bridge_used']} | {item['native_parallel_used']} |"
        )
    report = "\n".join(lines) + "\n"
    (output_root / "positional_phase_report.md").write_text(report, encoding="utf-8")
    (output_root / "summary.json").write_text(
        json.dumps(summaries, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(report)


if __name__ == "__main__":
    main()
