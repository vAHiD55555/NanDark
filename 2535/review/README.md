# Daily Review Process

Automated process to keep 2535 organized.

## When to Run
- After completing any work session
- Before starting new project
- At end of day (automated via cron)

## Process Steps
1. **Organize** — Check all directories for new files
2. **Review** — Run self-review engine
3. **Summarize** — Generate daily summary
4. **Report** — Create status report

## Automation

### One-time run:
```bash
python3 2535/daily_organize.py
```

### Continuous (daily at 2 AM):
```bash
python3 2535/daily_organize.py --cron --interval 86400
```

### Manual self-review only:
```bash
python3 2535/self_review.py
```

## Review Checklist
- [ ] All new ideas documented
- [ ] All decisions recorded with rationale
- [ ] Project statuses updated
- [ ] Daily summary generated
- [ ] Knowledge base organized
- [ ] Patterns detected in decisions
- [ ] Recommendations generated

## Pattern Detection
The self-review engine looks for:
- Repeated decision patterns
- Idea implementation gaps
- Knowledge base completeness
- System health indicators

## Output
- `daily/YYYY-MM-DD.md` — Daily summary
- `daily/status_YYYY-MM-DD.md` — Status report
- `review/` — Review notes and recommendations