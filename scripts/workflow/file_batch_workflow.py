from __future__ import annotations

import argparse
import sys
import time
from dataclasses import replace

import polars as pl

from factor_engine.run_summary import persist_run_summary, render_run_summary
from factor_engine.workflow import (
    evaluate_expression_file_with_summary,
    evaluate_expression_file_report_with_summary,
    write_result,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a batch expression file against an input parquet.")
    parser.add_argument("input", help="Input parquet path")
    parser.add_argument("expressions", help="Expression batch file (.json/.yaml/.yml)")
    parser.add_argument("--output", help="Optional output path (.parquet/.csv)")
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Keep successful expressions and print a structured failure summary.",
    )
    args = parser.parse_args()

    df = pl.read_parquet(args.input)
    if args.continue_on_error:
        report_run = evaluate_expression_file_report_with_summary(
            args.expressions,
            df,
            data_path=args.input,
            output_path=args.output,
        )
        result = report_run.report.result_df
        for failure in report_run.report.failures:
            print(
                f"[{failure.stage}] {failure.error_type}"
                f" name={failure.name!r} expression={failure.expression!r}: {failure.message}"
            )
        summary = report_run.summary
    else:
        strict_run = evaluate_expression_file_with_summary(
            args.expressions,
            df,
            data_path=args.input,
            output_path=args.output,
        )
        result = strict_run.result_df
        summary = strict_run.summary

    if args.output:
        write_start = time.perf_counter()
        write_result(result, args.output)
        summary = replace(
            summary,
            write_time_seconds=time.perf_counter() - write_start,
        )
    else:
        print(result)

    print(render_run_summary(summary))
    try:
        persist_run_summary(summary)
    except Exception as exc:  # pragma: no cover - CLI warning path
        print(f"[run-summary-warning] failed to persist summary: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
