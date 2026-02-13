#!/usr/bin/env python3
"""
Tock Time Summary Tool

A command-line utility to summarize time spent on projects and tasks
from the ~/.tock.txt file.

Usage:
    python tock_summary.py [-s START_DATE] [-e END_DATE]
    
    Dates should be in YYYY-MM-DD format
    If -e/--end is not specified, today's date is used
    If -s/--start is not specified, the most recent Monday relative to the end date is used
"""

import sys
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Dict, Tuple, Optional


def get_most_recent_monday(reference_date: datetime) -> datetime:
    """Get the most recent Monday relative to the reference date."""
    days_since_monday = reference_date.weekday()
    return reference_date - timedelta(days=days_since_monday)


def get_week_dates(week_str: str) -> Tuple[datetime, datetime]:
    """
    Get start (Monday) and end (Sunday) dates for an ISO week number.
    Denmark uses ISO 8601 week dates where week 1 is the first week with a Thursday.
    
    Args:
        week_str: Week number in format 'YYYY-WW' or just 'WW' (uses current year)
    
    Returns:
        Tuple of (start_date, end_date) for the week
    """
    current_year = datetime.now().year
    
    # Parse week string
    if '-' in week_str:
        year_str, week_num_str = week_str.split('-')
        year = int(year_str)
        week = int(week_num_str)
    else:
        year = current_year
        week = int(week_str)
    
    # Validate week number
    if week < 1 or week > 53:
        raise ValueError(f"Invalid week number: {week}. Must be between 1 and 53")
    
    # Get the Monday of the specified ISO week
    # ISO week 1 is the first week with a Thursday
    jan_4 = datetime(year, 1, 4)  # Jan 4 is always in week 1
    week_1_monday = jan_4 - timedelta(days=jan_4.weekday())
    
    # Calculate the Monday of the target week
    start_date = week_1_monday + timedelta(weeks=week - 1)
    end_date = start_date + timedelta(days=6)  # Sunday
    
    return (start_date, end_date)


def parse_date(date_str: str) -> datetime:
    """Parse a date string in YYYY-MM-DD format."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")


def parse_tock_line(line: str) -> Optional[Tuple[datetime, Optional[datetime], str, str]]:
    """
    Parse a line from the tock file.
    
    Returns:
        Tuple of (start_time, end_time, project, task) or None if line is invalid
    """
    line = line.strip()
    if not line:
        return None
    
    # Pattern for lines with both start and end times
    pattern_full = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}) - (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) \| ([^|]+) \| (.+)$'
    # Pattern for lines with only start time (no end time)
    pattern_start_only = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}) \| ([^|]+) \| (.+)$'
    
    match_full = re.match(pattern_full, line)
    if match_full:
        start_str, end_str, project, task = match_full.groups()
        start_time = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
        end_time = datetime.strptime(end_str, "%Y-%m-%d %H:%M")
        return (start_time, end_time, project.strip(), task.strip())
    
    match_start = re.match(pattern_start_only, line)
    if match_start:
        start_str, project, task = match_start.groups()
        start_time = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
        return (start_time, None, project.strip(), task.strip())
    
    return None


def calculate_duration(start_time: datetime, end_time: Optional[datetime]) -> float:
    """Calculate duration in hours. Returns 0 if end_time is None."""
    if end_time is None:
        return 0.0
    return (end_time - start_time).total_seconds() / 3600


def format_hours(hours: float) -> str:
    """Format hours as HH:MM."""
    total_minutes = int(hours * 60)
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{h:3d}:{m:02d}"


def summarize_tock_file(tock_path: Path, start_date: datetime, end_date: datetime) -> Dict:
    """
    Summarize time entries from the tock file within the date range.
    
    Returns:
        Dictionary with project and task summaries
    """
    project_hours = defaultdict(float)
    task_hours = defaultdict(lambda: defaultdict(float))
    total_hours = 0.0
    
    with open(tock_path, 'r', encoding='utf-8') as f:
        for line in f:
            parsed = parse_tock_line(line)
            if parsed is None:
                continue
            
            start_time, end_time, project, task = parsed
            
            # Check if the entry falls within the date range
            if start_time.date() < start_date.date() or start_time.date() > end_date.date():
                continue
            
            duration = calculate_duration(start_time, end_time)
            
            project_hours[project] += duration
            task_hours[project][task] += duration
            total_hours += duration
    
    return {
        'project_hours': dict(project_hours),
        'task_hours': {p: dict(t) for p, t in task_hours.items()},
        'total_hours': total_hours
    }


def print_summary(summary: Dict, start_date: datetime, end_date: datetime):
    """Print the summary in a formatted way."""
    print(f"\n{'='*60}")
    print(f"Time Summary: {start_date.date()} to {end_date.date()}")
    print(f"{'='*60}\n")
    
    project_hours = summary['project_hours']
    task_hours = summary['task_hours']
    total_hours = summary['total_hours']
    
    if not project_hours:
        print("No entries found in the specified date range.")
        return
    
    # Sort projects by total hours (descending)
    sorted_projects = sorted(project_hours.items(), key=lambda x: x[1], reverse=True)
    
    for project, hours in sorted_projects:
        print(f"{project:30s} {format_hours(hours)}")
        
        # Print tasks for this project
        if project in task_hours:
            sorted_tasks = sorted(task_hours[project].items(), key=lambda x: x[1], reverse=True)
            for task, task_hour in sorted_tasks:
                print(f"  └─ {task:26s} {format_hours(task_hour)}")
        print()
    
    print(f"{'─'*60}")
    print(f"{'TOTAL':30s} {format_hours(total_hours)}")
    print(f"{'='*60}\n")


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description='Summarize time spent on projects and tasks from ~/.tock.txt',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Most recent Monday to today
  %(prog)s -s 2026-02-03            # From Feb 3 to today
  %(prog)s -e 2026-02-09            # Most recent Monday to Feb 9
  %(prog)s -s 2026-02-05 -e 2026-02-09  # Feb 5 to Feb 9
  %(prog)s -w 6                     # Week 6 of current year
  %(prog)s -w 2026-06               # Week 6 of 2026
        """
    )
    
    parser.add_argument(
        '-s', '--start',
        type=str,
        metavar='YYYY-MM-DD',
        help='Start date (default: most recent Monday relative to end date)'
    )
    
    parser.add_argument(
        '-e', '--end',
        type=str,
        metavar='YYYY-MM-DD',
        help='End date (default: today)'
    )
    
    parser.add_argument(
        '-w', '--week',
        type=str,
        metavar='[YYYY-]WW',
        help='ISO week number (e.g., "6" for week 6 of current year, or "2026-06" for week 6 of 2026). Overrides -s and -e.'
    )
    
    args = parser.parse_args()
    
    # Determine start and end dates
    today = datetime.now()
    
    # If week is specified, it overrides start and end dates
    if args.week:
        start_date, end_date = get_week_dates(args.week)
    else:
        # Determine end date first
        if args.end:
            end_date = parse_date(args.end)
        else:
            end_date = today
        
        # Determine start date relative to end date
        if args.start:
            start_date = parse_date(args.start)
        else:
            start_date = get_most_recent_monday(end_date)
    
    # Get tock file path
    tock_path = Path.home() / '.tock.txt'
    
    if not tock_path.exists():
        print(f"Error: Tock file not found at {tock_path}", file=sys.stderr)
        sys.exit(1)
    
    # Generate and print summary
    try:
        summary = summarize_tock_file(tock_path, start_date, end_date)
        print_summary(summary, start_date, end_date)
    except Exception as e:
        print(f"Error processing tock file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
