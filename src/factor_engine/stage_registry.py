from __future__ import annotations

from dataclasses import dataclass

import polars as pl

from factor_engine.profiling import StageDetail, StageEvent, StageLifecycleProfiler, current_rss_mb


@dataclass
class StageRecord:
    stage_id: str
    expr_key: str
    column_name: str
    stage_kind: str
    producer_route: str
    source_expression: str | None
    created_order_index: int
    consumer_count_total: int = 0
    consumer_count_remaining: int = 0
    last_use_order_index: int | None = None
    is_output_backed: bool = False
    is_alive: bool = True
    is_dropped: bool = False
    frame_col_count_at_create: int = 0
    frame_col_count_at_last_use: int | None = None
    rss_at_create_mb: float = 0.0
    rss_at_last_use_mb: float | None = None
    planned_consumer_count_total: int = 0
    planned_last_use_order_index: int | None = None
    actual_consume_count: int = 0
    recomputed_after_drop: bool = False
    kept_alive_for_planned_reuse: bool = False
    dropped_after_planned_last_use: bool = False


class StageRegistry:
    def __init__(
        self,
        *,
        batch_id: str,
        profiler: StageLifecycleProfiler | None = None,
    ) -> None:
        self.batch_id = batch_id
        self.profiler = profiler
        self.records: dict[str, StageRecord] = {}
        self.column_to_stage_id: dict[str, str] = {}
        self.cache_key_to_stage_id: dict[tuple, str] = {}
        self.order_index = 0
        self.peak_live_stage_count = 0
        self.dropped_stage_count = 0
        self.recomputed_stage_count = 0
        self.avoided_recomputation_count = 0
        self._dropped_cache_keys: set[tuple] = set()

    def next_order_index(self) -> int:
        self.order_index += 1
        return self.order_index

    def register_stage(
        self,
        *,
        expr_key: object,
        column_name: str,
        stage_kind: str,
        producer_route: str,
        frame_col_count: int,
        source_expression: str | None = None,
        cache_key: tuple | None = None,
    ) -> str:
        existing = self.column_to_stage_id.get(column_name)
        if existing is not None:
            return existing

        order_index = self.next_order_index()
        stage_id = f"{self.batch_id}:stage:{len(self.records) + 1}"
        rss = current_rss_mb()
        record = StageRecord(
            stage_id=stage_id,
            expr_key=repr(expr_key),
            column_name=column_name,
            stage_kind=stage_kind,
            producer_route=producer_route,
            source_expression=source_expression,
            created_order_index=order_index,
            frame_col_count_at_create=frame_col_count,
            rss_at_create_mb=rss,
        )
        self.records[stage_id] = record
        self.column_to_stage_id[column_name] = stage_id
        if cache_key is not None:
            self.cache_key_to_stage_id[cache_key] = stage_id
            if cache_key in self._dropped_cache_keys:
                record.recomputed_after_drop = True
                self.recomputed_stage_count += 1
                if self.profiler is not None:
                    self.profiler.add_event(
                        StageEvent(
                            event_type="recomputed_stage_detected",
                            stage_id=stage_id,
                            batch_id=self.batch_id,
                            order_index=order_index,
                            stage_kind=stage_kind,
                            expr_key=record.expr_key,
                            frame_col_count=frame_col_count,
                            rss_mb=rss,
                            recomputed_after_drop=True,
                        )
                    )
        self._observe_live_count()

        if self.profiler is not None:
            self.profiler.add_event(
                StageEvent(
                    event_type="stage_created",
                    stage_id=stage_id,
                    batch_id=self.batch_id,
                    order_index=order_index,
                    stage_kind=stage_kind,
                    expr_key=record.expr_key,
                    frame_col_count=frame_col_count,
                    rss_mb=rss,
                )
            )
        return stage_id

    def record_consume(
        self,
        column_name: str,
        *,
        consumer_kind: str,
        frame_col_count: int,
    ) -> None:
        stage_id = self.column_to_stage_id.get(column_name)
        if stage_id is None:
            return

        record = self.records[stage_id]
        order_index = self.next_order_index()
        rss = current_rss_mb()
        if record.consumer_count_total == 0:
            record.consumer_count_total = 1
        if record.consumer_count_remaining > 0:
            record.consumer_count_remaining -= 1
        record.actual_consume_count += 1
        if record.planned_consumer_count_total > 1 and record.consumer_count_remaining > 0:
            record.kept_alive_for_planned_reuse = True
        if record.planned_consumer_count_total > 1 and record.actual_consume_count > 1:
            self.avoided_recomputation_count += 1
        record.last_use_order_index = order_index
        record.frame_col_count_at_last_use = frame_col_count
        record.rss_at_last_use_mb = rss

        if self.profiler is not None:
            self.profiler.add_event(
                StageEvent(
                    event_type="stage_consumed",
                    stage_id=stage_id,
                    batch_id=self.batch_id,
                    order_index=order_index,
                    stage_kind=record.stage_kind,
                    expr_key=record.expr_key,
                    frame_col_count=frame_col_count,
                    rss_mb=rss,
                    consumer_kind=consumer_kind,
                    planned_consumer_count_total=record.planned_consumer_count_total,
                    planned_consumer_count_remaining=record.consumer_count_remaining,
                    actual_consume_count=record.actual_consume_count,
                    planned_last_use_order_index=record.planned_last_use_order_index,
                    kept_alive_for_planned_reuse=record.kept_alive_for_planned_reuse,
                )
            )
            if record.planned_consumer_count_total > 1 and record.actual_consume_count > 1:
                self.profiler.add_event(
                    StageEvent(
                        event_type="planned_stage_reused",
                        stage_id=stage_id,
                        batch_id=self.batch_id,
                        order_index=order_index,
                        stage_kind=record.stage_kind,
                        expr_key=record.expr_key,
                        frame_col_count=frame_col_count,
                        rss_mb=rss,
                        consumer_kind=consumer_kind,
                        planned_consumer_count_total=record.planned_consumer_count_total,
                        planned_consumer_count_remaining=record.consumer_count_remaining,
                        actual_consume_count=record.actual_consume_count,
                        kept_alive_for_planned_reuse=record.kept_alive_for_planned_reuse,
                    )
                )
            if record.planned_consumer_count_total > 0 and record.consumer_count_remaining == 0:
                record.planned_last_use_order_index = order_index
                self.profiler.add_event(
                    StageEvent(
                        event_type="planned_last_use_reached",
                        stage_id=stage_id,
                        batch_id=self.batch_id,
                        order_index=order_index,
                        stage_kind=record.stage_kind,
                        expr_key=record.expr_key,
                        frame_col_count=frame_col_count,
                        rss_mb=rss,
                        consumer_kind=consumer_kind,
                        planned_consumer_count_total=record.planned_consumer_count_total,
                        planned_consumer_count_remaining=record.consumer_count_remaining,
                        actual_consume_count=record.actual_consume_count,
                        planned_last_use_order_index=record.planned_last_use_order_index,
                    )
                )

    def mark_output_backed(self, column_name: str) -> None:
        stage_id = self.column_to_stage_id.get(column_name)
        if stage_id is not None:
            self.records[stage_id].is_output_backed = True

    def set_expected_consumers(self, column_name: str, count: int) -> None:
        if count < 0:
            raise ValueError("expected consumer count must be non-negative")
        stage_id = self.column_to_stage_id.get(column_name)
        if stage_id is None:
            return
        record = self.records[stage_id]
        record.consumer_count_total = count
        record.consumer_count_remaining = count
        record.planned_consumer_count_total = count
        if count > 0 and self.profiler is not None:
            self.profiler.add_event(
                StageEvent(
                    event_type="planned_stage_registered",
                    stage_id=stage_id,
                    batch_id=self.batch_id,
                    order_index=self.next_order_index(),
                    stage_kind=record.stage_kind,
                    expr_key=record.expr_key,
                    frame_col_count=record.frame_col_count_at_create,
                    rss_mb=current_rss_mb(),
                    planned_consumer_count_total=count,
                    planned_consumer_count_remaining=count,
                    actual_consume_count=record.actual_consume_count,
                )
            )

    def sweep_drop_candidates(
        self,
        frame: pl.DataFrame,
        *,
        stage_cache: dict[tuple, str],
        output_names: set[str],
        enabled: bool,
    ) -> pl.DataFrame:
        if not enabled:
            return frame

        drop_columns: list[str] = []
        for record in self.records.values():
            if not self.can_drop(record, output_names=output_names):
                continue
            drop_columns.append(record.column_name)
            record.is_alive = False
            record.is_dropped = True
            record.dropped_after_planned_last_use = (
                record.planned_consumer_count_total == 0
                or record.consumer_count_remaining == 0
            )
            self.dropped_stage_count += 1
            if self.profiler is not None:
                self.profiler.add_event(
                    StageEvent(
                        event_type="stage_dropped",
                        stage_id=record.stage_id,
                        batch_id=self.batch_id,
                        order_index=self.next_order_index(),
                        stage_kind=record.stage_kind,
                        expr_key=record.expr_key,
                        frame_col_count=frame.width,
                        rss_mb=current_rss_mb(),
                        planned_consumer_count_total=record.planned_consumer_count_total,
                        planned_consumer_count_remaining=record.consumer_count_remaining,
                        actual_consume_count=record.actual_consume_count,
                        planned_last_use_order_index=record.planned_last_use_order_index,
                        kept_alive_for_planned_reuse=record.kept_alive_for_planned_reuse,
                        dropped_after_planned_last_use=record.dropped_after_planned_last_use,
                    )
                )

        if not drop_columns:
            return frame

        for cache_key, column_name in list(stage_cache.items()):
            if column_name in drop_columns:
                stage_cache.pop(cache_key, None)
                self._dropped_cache_keys.add(cache_key)
        for cache_key, stage_id in list(self.cache_key_to_stage_id.items()):
            if self.records[stage_id].column_name in drop_columns:
                self.cache_key_to_stage_id.pop(cache_key, None)
                self._dropped_cache_keys.add(cache_key)

        return frame.drop(drop_columns)

    def can_drop(self, record: StageRecord, *, output_names: set[str]) -> bool:
        return (
            record.is_alive
            and not record.is_output_backed
            and record.column_name not in output_names
            and record.consumer_count_remaining == 0
        )

    def snapshot_batch_end(
        self,
        *,
        frame_col_count: int,
        output_names: set[str],
    ) -> list[StageDetail]:
        details: list[StageDetail] = []
        for record in self.records.values():
            is_drop_candidate = self.can_drop(record, output_names=output_names)
            if self.profiler is not None:
                self.profiler.add_event(
                    StageEvent(
                        event_type="batch_end_stage_snapshot",
                        stage_id=record.stage_id,
                        batch_id=self.batch_id,
                        order_index=self.next_order_index(),
                        stage_kind=record.stage_kind,
                        expr_key=record.expr_key,
                        frame_col_count=frame_col_count,
                        rss_mb=current_rss_mb(),
                        alive_at_batch_end=record.is_alive,
                        is_drop_candidate_at_batch_end=is_drop_candidate,
                        planned_consumer_count_total=record.planned_consumer_count_total,
                        planned_consumer_count_remaining=record.consumer_count_remaining,
                        actual_consume_count=record.actual_consume_count,
                        planned_last_use_order_index=record.planned_last_use_order_index,
                        kept_alive_for_planned_reuse=record.kept_alive_for_planned_reuse,
                        dropped_after_planned_last_use=record.dropped_after_planned_last_use,
                        recomputed_after_drop=record.recomputed_after_drop,
                    )
                )
            detail = StageDetail(
                stage_id=record.stage_id,
                batch_id=self.batch_id,
                expr_key=record.expr_key,
                stage_kind=record.stage_kind,
                producer_route=record.producer_route,
                created_order_index=record.created_order_index,
                consumer_count_total_estimate=record.consumer_count_total,
                last_use_order_index_estimate=record.last_use_order_index,
                alive_at_batch_end=record.is_alive,
                column_name=record.column_name,
                frame_col_count_at_create=record.frame_col_count_at_create,
                frame_col_count_at_last_use_estimate=record.frame_col_count_at_last_use,
                rss_at_create_mb=record.rss_at_create_mb,
                rss_at_last_use_estimate_mb=record.rss_at_last_use_mb,
                is_short_lived_candidate=record.consumer_count_total <= 1,
                is_drop_candidate_at_batch_end=is_drop_candidate,
                dropped=record.is_dropped,
                planned_consumer_count_total=record.planned_consumer_count_total,
                planned_last_use_order_index=record.planned_last_use_order_index,
                actual_consume_count=record.actual_consume_count,
                recomputed_after_drop=record.recomputed_after_drop,
                kept_alive_for_planned_reuse=record.kept_alive_for_planned_reuse,
                dropped_after_planned_last_use=record.dropped_after_planned_last_use,
            )
            details.append(detail)
            if self.profiler is not None:
                self.profiler.add_stage(detail)
        return details

    def live_stage_count(self) -> int:
        return sum(1 for item in self.records.values() if item.is_alive)

    def _observe_live_count(self) -> None:
        self.peak_live_stage_count = max(self.peak_live_stage_count, self.live_stage_count())
