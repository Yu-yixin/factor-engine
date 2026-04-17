from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PhysicalProperties:
    partition_by: tuple[str, ...] = ()
    order_by: tuple[str, ...] = ()
    segment: str | None = None

    def is_plain(self) -> bool:
        return not self.partition_by and not self.order_by and self.segment is None


@dataclass(frozen=True)
class OperatorContract:
    requires: PhysicalProperties
    produces_mode: str = "same_as_requires"
    produces: PhysicalProperties | None = None
    accepts_materialized_input: bool = True
    is_single_input_ordered_root: bool = False

    def produced_properties(self) -> PhysicalProperties:
        if self.produces_mode == "same_as_requires":
            return self.requires
        if self.produces is None:
            raise ValueError("custom produces_mode requires explicit produced properties")
        return self.produces


MATERIALIZATION_EFFECT = PhysicalProperties()


def satisfies(child: PhysicalProperties, parent: PhysicalProperties) -> bool:
    if parent.is_plain():
        return True

    if child.is_plain():
        return True

    if parent.partition_by != child.partition_by:
        return False

    if parent.order_by and child.order_by[: len(parent.order_by)] != parent.order_by:
        return False

    if parent.segment is not None and parent.segment != child.segment:
        return False

    return True
