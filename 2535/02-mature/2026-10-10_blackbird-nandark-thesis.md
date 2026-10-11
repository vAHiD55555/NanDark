# 2026-10-10_blackbird-nandark-thesis.md

- **Status**: Mature
- **Date**: 2026-10-10
- **Domain**: Strategy / Architecture / Commerce

## Problem

How to build financial independence and a reusable AI ecosystem under severe resource constraints (Android-only, no credit card, no paid VPS).

## Hypothesis

A small, honest core (BlackBird) that observes, records, and learns can generate reusable value that compounds into a larger intelligence platform (NanDark). Revenue is not guaranteed; the value is in durable assets (data, decisions, code, methods).

## Evidence

Documented in `BlackBird_NanDark_Execution_Scenario_FA.md` and the conceptual thesis. Baseline: `BlackBird-Core-v0.1` produced `WAIT` with a market-price field — observational only, no trading engine.

## Risks

- No proven profitability.
- Free data sources may be unreliable or restricted.
- Scope creep from architecture planning into execution.
- Token leakage in git remote URL (see security note below).

## Next step

Phase 0: build the smallest runnable observer on Android/Termux with real (free) market data, SQLite journal, and safe default `WAIT`/`NO_TRADE`.

## Decision / Outcome

Pending execution.

---

## Core principles extracted from the thesis

1. **Truth over presentation** — what is not implemented must not be presented as implemented.
2. **Quality over speed** — a reliable capability beats many named agents.
3. **Start small, grow capable** — the core must be real and extensible.
4. **Risk must have an off-switch** — no single decision-maker may bypass vital limits.
5. **Separate data, interpretation, and decision** — this separation is the basis of audit and learning.
6. **Every failure must produce information** — an unrecorded error is a recurring cost; an analyzed error can become knowledge.
7. **Reduce dependency** — the architecture must be modular, allowing model, data source, or tool substitution.
8. **Measure revenue by real demand** — technical appeal does not replace customers, evidence, or the ability to receive payment.
9. **Authority proportional to responsibility** — each tool should hold only the permissions its role requires.
10. **Progress must be provable** — every capability should have a success criterion, a test method, and a change history.

## Conceptual roles (not implementation claims)

- **Scout** — data collection and monitoring.
- **Economic Council** — analytical perspectives.
- **Commander** — final decision within rules.
- **Watchdog / Dolphin** — independent risk oversight with hard veto.
- **Risk Guardian** — independent veto power; can force `WAIT` or `NO_TRADE`.

## Memory layers

1. **Identity and principles** — why the project exists, what constraints must not change.
2. **Decision and knowledge** — what was chosen, why, and what assumptions stood behind it.
3. **Event and outcome** — what happened, which tests ran, what errors occurred, what the result was.

## Open tensions

- Fast income vs. long-term build.
- Trading vs. digital commerce.
- Autonomy vs. control.
- Rich memory vs. trustworthy memory.
- Free vs. stable.

## Security note

The git remote URL contains a plaintext GitHub token. This is a real risk. The token should be rotated via the GitHub settings page and the remote reconfigured to use a credential helper or SSH key.