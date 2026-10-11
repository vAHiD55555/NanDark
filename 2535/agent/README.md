# Agent Architecture

Multi-agent system for intelligent, autonomous operation.

## Design Principles
1. **Modularity** — Each agent has a single responsibility
2. **Decoupling** — Agents communicate through messages, not direct calls
3. **Observability** — All decisions are logged and reviewable
4. **Safety** — No action without explicit approval for real-world changes

## Components

### Orchestrator (`orchestrator.py`)
- Task routing between agents
- Conflict resolution
- Lifecycle management
- Status reporting

### Memory Agent (`memory.py`)
- Read/write to 2535 knowledge base
- Semantic search across all knowledge
- Context retrieval for current task

### Planner Agent (`planner.py`)
- Goal decomposition
- Step sequencing
- Dependency management
- Progress tracking

### Self-Review Agent (`self_review.py`)
- Daily review of all activities
- Pattern detection in decisions
- Improvement recommendations
- Knowledge consolidation

### Tool Registry (`tool_registry.py`)
- Register available tools
- Validate tool safety
- Execute tools with logging

### Providers (`providers/`)
- DeepSeek — fast, free, analytical
- Claude — deep reasoning, design
- GPT — content generation, structured output
- Nemotron — complex problem-solving

## Message Format
```json
{
  "from": "agent_name",
  "to": "agent_name",
  "type": "request|response|notification",
  "content": "...",
  "timestamp": "ISO8601",
  "context": {}
}
```

## Current State
- Architecture: Designed
- Implementation: Pending
- Providers: Available (via Kilo Gateway)