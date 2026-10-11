# Decisions Index

Key decisions with rationale and impact.

## 2026-10-11

### Real Data Only
- **Decision**: No synthetic market data. quality=FAIL → NO_TRADE.
- **Rationale**: Prevent false confidence from fabricated data. Accuracy over speed.
- **Impact**: System waits for real API data before any action.

### Paper Trading Before Real
- **Decision**: All trades are paper until explicit user approval.
- **Rationale**: Per AGENTS.md principle — real trades only after paper verification.
- **Impact**: Zero financial risk during study period.

### Two Observers
- **Decision**: Conservative + Aggressive observers for comparative study.
- **Rationale**: Different assumptions → discover which patterns are actually predictive.
- **Impact**: 6-month data set for analysis.

### Multi-Agent Architecture
- **Decision**: Build orchestrator + memory + planner + self-review.
- **Rationale**: Single-file Python is insufficient for intelligent behavior.
- **Impact**: Scalable foundation for future AI capabilities.

### 2535 Knowledge Base
- **Decision**: Consolidate all knowledge in one structured location.
- **Rationale**: Prevent information scattering. Enable daily review.
- **Impact**: Single source of truth for all ideas and decisions.