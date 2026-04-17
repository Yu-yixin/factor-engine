# Factor Engine Development Strategy

This folder is the strategic guide for future engine development. It is not a
shopping list of missing functions. It defines which capability families are
worth building next, why they matter, and what system-level conditions must be
true before they can be accepted.

## Current Baseline

The current engine has crossed several important lines:

- M1 observability exists: profiling, run summaries, route inspection, memory
  and execution attribution are available.
- M2 lifecycle is frozen: non-native node-store drop and helper-column first
  wave plus pure nested second wave are stable boundaries.
- M3 materialization experiments have been exhausted for the current cycle.
- M4 is frozen under the strong-success path: localized CSE expansion and
  minimal unary-chain fusion were accepted; wider structural candidates are
  deferred.
- Native positional execution and low-copy bridge work exist for the current
  accepted positional family.
- Group-level CPU parallelism exists, but future parallelism must be tied to
  planner-visible execution regions and memory residency constraints.

The strategic implication is simple:

> Future features must be nativeable, DAG/CSE-compatible, lifecycle-auditable,
> and benchmark-decidable before they become normal engine capabilities.

## Strategy Documents

- [Future Operator Roadmap](future_operator_roadmap.md)
  Defines operator families that are valuable but should not be added as
  ordinary functions yet.

- [Native Runtime Strategy](native_runtime_strategy.md)
  Defines how future Rust/C++ kernels should be shaped, including state layout,
  buffer ownership, and ABI expectations.

- [Memory And Lifecycle Strategy](memory_and_lifecycle_strategy.md)
  Defines how future operators must interact with node-store, helper columns,
  native buffers, materialization, and frame width discipline.

- [Parallel Execution Strategy](parallel_execution_strategy.md)
  Defines the safe path from current group-level parallelism toward richer
  planner-aware parallel execution.

- [Capability Upgrade Protocol](capability_upgrade_protocol.md)
  Defines what must be updated whenever system capability changes.

## Non-Negotiable Development Rules

1. No Python object-level execution for new core operators.
2. No new route without a planner design, ordered/contract audit, and tests.
3. No alias implementation may duplicate executor logic.
4. No native-heavy family may be added as a one-off special case.
5. No lifecycle expansion may be hidden inside an operator implementation.
6. No M4 structural expansion may be slipped into operator work.
7. Every accepted capability must have a benchmarkable A/B or a clear semantic
   test boundary.
8. Every capability upgrade must update this folder and
   `docs/operator_addition_guide.md`.

## Strategic Definition Of A Future Operator

A future operator is not merely a function name that appears in Alpha101 or a
research paper. It is a capability that can satisfy all of the following:

- has a clear Rust/C++ or backend-native execution target;
- can be represented in registry, validator, physical contract, planner, and
  DAG identity;
- has a route-sensitive canonical identity for CSE;
- has an explainable materialization policy;
- has known node-store/helper/native-buffer lifecycle behavior;
- can be benchmarked without weakening M1/M2/M3/M4 frozen semantics.

Anything that cannot meet this standard belongs in the roadmap, not in the
ordinary operator batch.

