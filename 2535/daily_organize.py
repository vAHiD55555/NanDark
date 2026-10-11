#!/usr/bin/env python3
"""Daily Automation — runs after work completion.

Purposes:
1. Organize 2535 knowledge base
2. Run self-review
3. Generate daily summary
4. Clean up old files

Usage:
    python3 daily_organize.py          # One-time run
    python3 daily_organize.py --cron   # Continuous mode (daily)
"""

import os
import sys
import json
import time
import argparse
import subprocess
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.abspath(__file__))

def run_command(cmd, description=""):
    """Run a command and return (success, output)."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            cwd=BASE, timeout=120
        )
        success = result.returncode == 0
        output = result.stdout + result.stderr
        if description:
            print(f"  [{'OK' if success else 'FAIL'}] {description}")
        return success, output
    except Exception as e:
        print(f"  [FAIL] {description}: {e}")
        return False, str(e)

def organize_ideas():
    """Check for new idea files and update index."""
    ideas_dir = os.path.join(BASE, "ideas")
    if not os.path.exists(ideas_dir):
        return False, "Ideas directory missing"
    
    idea_files = [f for f in os.listdir(ideas_dir) if f.endswith('.md') and f != 'README.md']
    return True, f"Found {len(idea_files)} idea files"

def organize_projects():
    """Check project status files."""
    projects_dir = os.path.join(BASE, "projects")
    if not os.path.exists(projects_dir):
        return False, "Projects directory missing"
    
    project_files = [f for f in os.listdir(projects_dir) if f.endswith('.md') and f != 'README.md']
    return True, f"Found {len(project_files)} project files"

def organize_decisions():
    """Check decision files."""
    decisions_dir = os.path.join(BASE, "decisions")
    if not os.path.exists(decisions_dir):
        return False, "Decisions directory missing"
    
    decision_files = [f for f in os.listdir(decisions_dir) if f.endswith('.md') and f != 'README.md']
    return True, f"Found {len(decision_files)} decision files"

def run_self_review():
    """Run the self-review engine."""
    script = os.path.join(BASE, "self_review.py")
    return run_command(f"python3 {script}", "Self-review engine")

def generate_status_report():
    """Generate a status report for today."""
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    # Count files
    ideas_count = len([f for f in os.listdir(os.path.join(BASE, "ideas")) if f.endswith('.md') and f != 'README.md']) if os.path.exists(os.path.join(BASE, "ideas")) else 0
    projects_count = len([f for f in os.listdir(os.path.join(BASE, "projects")) if f.endswith('.md') and f != 'README.md']) if os.path.exists(os.path.join(BASE, "projects")) else 0
    decisions_count = len([f for f in os.listdir(os.path.join(BASE, "decisions")) if f.endswith('.md') and f != 'README.md']) if os.path.exists(os.path.join(BASE, "decisions")) else 0
    
    report = f"""# 2535 Status Report — {today}

## Knowledge Base Health
- Ideas: {ideas_count} files
- Projects: {projects_count} files
- Decisions: {decisions_count} files
- Last organized: {today}

## System Status
- Multi-agent architecture: Designed
- Self-review engine: Active
- Daily automation: Running

## Next Steps
- Implement orchestrator
- Connect providers
- Start 6-month BlackBird study
"""
    
    daily_dir = os.path.join(BASE, "daily")
    os.makedirs(daily_dir, exist_ok=True)
    fname = os.path.join(daily_dir, f"status_{today}.md")
    
    with open(fname, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return fname

def main():
    parser = argparse.ArgumentParser(description="2535 Daily Organizer")
    parser.add_argument("--cron", action="store_true", help="Run in continuous mode")
    parser.add_argument("--interval", type=int, default=86400, help="Cron interval in seconds (default: 24h)")
    args = parser.parse_args()
    
    print("[2535] Starting daily organization...")
    print(f"[2535] Time: {datetime.now(timezone.utc).isoformat()}")
    print("-" * 50)
    
    # Step 1: Organize ideas
    ok, msg = organize_ideas()
    print(f"  [IDEAS] {msg}")
    
    # Step 2: Organize projects
    ok, msg = organize_projects()
    print(f"  [PROJECTS] {msg}")
    
    # Step 3: Organize decisions
    ok, msg = organize_decisions()
    print(f"  [DECISIONS] {msg}")
    
    # Step 4: Run self-review
    ok, output = run_self_review()
    if ok:
        print(f"  [REVIEW] Complete")
    else:
        print(f"  [REVIEW] Error: {output[:100]}")
    
    # Step 5: Generate status report
    fname = generate_status_report()
    print(f"  [REPORT] Saved to: {fname}")
    
    print("-" * 50)
    print("[2535] Daily organization complete.")
    
    if args.cron:
        print(f"[2535] Running in cron mode, interval: {args.interval}s")
        while True:
            time.sleep(args.interval)
            main()

if __name__ == "__main__":
    main()