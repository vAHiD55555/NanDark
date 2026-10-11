# 2026-10-11 — Multi-Agent Architecture

## Context
Single-file Python (main.py) is insufficient for intelligent agent behavior.
Need a system that can:
- Plan tasks autonomously
- Use multiple AI models
- Learn from feedback
- Self-review and improve

## Proposed Architecture

```
agent/
├── orchestrator.py    # Coordinates all agents
├── memory.py          # Long-term memory (2535 knowledge base)
├── planner.py         # Breaks tasks into executable steps
├── self_review.py     # Daily review and improvement
├── tool_registry.py   # Manages available tools
└── providers/         # AI model connectors
    ├── deepseek.py
    ├── claude.py
    ├── gpt.py
    └── nemotron.py
```

## Agent Roles
1. **Orchestrator** — Task routing, conflict resolution
2. **Memory Agent** — Read/write to 2535 knowledge base
3. **Planner Agent** — Decompose goals into steps
4. **Review Agent** — Quality check, pattern detection
5. **Provider Agents** — Execute specific AI model calls

## Open Questions
- How to handle provider failures?
- What memory format for cross-agent communication?
- How to measure agent effectiveness?

## Status
Architecture designed. Implementation pending.