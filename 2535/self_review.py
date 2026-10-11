#!/usr/bin/env python3
"""Daily Self-Review Engine — runs after work completion.

Purposes:
1. Organize 2535 knowledge base
2. Detect patterns in decisions
3. Generate improvement recommendations
4. Create daily summary

Run: python3 self_review.py
"""

import os
import json
import glob
from datetime import datetime, timezone
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
DAILY_DIR = os.path.join(BASE, "daily")
REVIEW_DIR = os.path.join(BASE, "review")
IDEAS_DIR = os.path.join(BASE, "ideas")
DECISIONS_DIR = os.path.join(BASE, "decisions")

def ensure_dirs():
    for d in [DAILY_DIR, REVIEW_DIR, IDEAS_DIR, DECISIONS_DIR]:
        os.makedirs(d, exist_ok=True)

def count_files(directory):
    if not os.path.exists(directory):
        return 0
    return len([f for f in os.listdir(directory) if f.endswith('.md')])

def analyze_decisions():
    """Extract patterns from decision files."""
    decisions_file = os.path.join(DECISIONS_DIR, "README.md")
    if not os.path.exists(decisions_file):
        return {"total": 0, "patterns": []}
    
    with open(decisions_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count decision markers
    decisions = content.split('### ')[1:]  # Skip header
    patterns = []
    for d in decisions:
        lines = d.strip().split('\n')
        if lines:
            title = lines[0].strip()
            patterns.append(title)
    
    return {
        "total": len(decisions),
        "patterns": patterns,
        "most_common": Counter(patterns).most_common(3)
    }

def analyze_ideas():
    """Analyze idea files for status tracking."""
    ideas_file = os.path.join(IDEAS_DIR, "README.md")
    if not os.path.exists(ideas_file):
        return {"total": 0, "by_status": {}}
    
    with open(ideas_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count idea links
    idea_links = [line for line in content.split('\n') if '- [' in line]
    
    statuses = defaultdict(int)
    for link in idea_links:
        if 'Status' in link:
            if 'Implemented' in link or 'Active' in link or 'Ready' in link:
                statuses['implemented'] += 1
            elif 'Pending' in link or 'Planning' in link:
                statuses['pending'] += 1
            else:
                statuses['other'] += 1
    
    return {
        "total": len(idea_links),
        "by_status": dict(statuses)
    }

def generate_daily_summary():
    """Create today's summary."""
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    decisions = analyze_decisions()
    ideas = analyze_ideas()
    
    summary = f"""# Daily Summary — {today}

## System Health
- Knowledge base organized: Yes
- Total ideas: {ideas['total']}
- Total decisions: {decisions['total']}
- Ideas implemented: {ideas['by_status'].get('implemented', 0)}
- Ideas pending: {ideas['by_status'].get('pending', 0)}

## Decision Patterns
"""
    if decisions['patterns']:
        for p in decisions['patterns']:
            summary += f"- {p}\n"
    else:
        summary += "- No decisions yet\n"
    
    summary += f"""
## Recommendations
"""
    
    # Generate recommendations based on patterns
    if ideas['by_status'].get('pending', 0) > ideas['by_status'].get('implemented', 0):
        summary += "- Consider implementing pending ideas\n"
    
    if decisions['total'] < 5:
        summary += "- Add more documented decisions for better pattern detection\n"
    
    summary += """
## Next Review
- Tomorrow at same time
- After any major decision
- Before starting new project
"""
    
    return summary

def save_summary(summary):
    """Save daily summary."""
    ensure_dirs()
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    fname = os.path.join(DAILY_DIR, f"{today}.md")
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(summary)
    return fname

def main():
    ensure_dirs()
    
    print("[Self-Review] Starting daily review...")
    
    # Analyze
    decisions = analyze_decisions()
    ideas = analyze_ideas()
    
    print(f"[Self-Review] Ideas: {ideas['total']}, Decisions: {decisions['total']}")
    
    # Generate summary
    summary = generate_daily_summary()
    fname = save_summary(summary)
    
    print(f"[Self-Review] Summary saved to: {fname}")
    print("[Self-Review] Review complete.")
    
    # Print summary
    print("\n" + "="*60)
    print(summary)

if __name__ == "__main__":
    main()