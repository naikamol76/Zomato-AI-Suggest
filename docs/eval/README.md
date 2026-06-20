# Phase Evaluation Guides

Each implementation phase has an **`eval.md`** with **pass/fail criteria**, **automated checks**, **manual checks**, and **edge cases** to verify before moving on.

| Phase | Document | Focus |
|-------|----------|--------|
| 0 | [phase-0/eval.md](./phase-0/eval.md) | Monorepo, health, tooling |
| 1 | [phase-1/eval.md](./phase-1/eval.md) | Ingest, Parquet, repository |
| 2 | [phase-2/eval.md](./phase-2/eval.md) | Filter service |
| 3 | [phase-3/eval.md](./phase-3/eval.md) | LLM, parser, validator |
| 4 | [phase-4/eval.md](./phase-4/eval.md) | Orchestrator |
| 5 | [phase-5/eval.md](./phase-5/eval.md) | REST API, CORS |
| 6 | [phase-6/eval.md](./phase-6/eval.md) | React UI |
| 7 | [phase-7/eval.md](./phase-7/eval.md) | Full MVP sign-off |

**Edge case catalog:** [`../edgecase.md`](../edgecase.md)

**Implementation plan:** [`../implementationPlan.md`](../implementationPlan.md)

---

## Evaluation workflow

1. Complete all tasks for phase N in the implementation plan.  
2. Run **automated** checks in `phase-N/eval.md`.  
3. Complete **manual** checklist (record date + pass/fail).  
4. Verify **edge cases** listed for that phase in `edgecase.md`.  
5. Mark phase done in implementation plan checklist.  
6. Proceed to phase N+1.
