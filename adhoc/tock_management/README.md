# Tock Time Summary Tool

A command-line utility to summarize time spent on projects and tasks from your `~/.tock.txt` file.

## Features

- Parses time entries in the format: `YYYY-MM-DD HH:MM - YYYY-MM-DD HH:MM | project | task`
- Supports entries with only start times (no end time)
- Filters entries by date range
- Summarizes time by project and task
- Displays results in a hierarchical, easy-to-read format

## Usage

```bash
python3 tock_summary.py [-s START_DATE] [-e END_DATE] [-w WEEK]
```

### Arguments

- `-s, --start YYYY-MM-DD` (optional): Start date
  - If omitted, defaults to the most recent Monday relative to the end date
- `-e, --end YYYY-MM-DD` (optional): End date
  - If omitted, defaults to today's date
- `-w, --week [YYYY-]WW` (optional): ISO week number (as used in Denmark)
  - Format: `WW` for current year or `YYYY-WW` for specific year
  - Overrides `-s` and `-e` parameters
  - Week 1 is the first week containing a Thursday (ISO 8601 standard)

### Examples

**Summarize time from a specific date range:**

```bash
python3 tock_summary.py -s 2026-02-05 -e 2026-02-09
```

**Summarize time from a specific start date to today:**

```bash
python3 tock_summary.py -s 2026-02-03
```

**Summarize time from the most recent Monday to a specific end date:**

```bash
python3 tock_summary.py -e 2026-02-09
```

**Summarize time from the most recent Monday to today:**

```bash
python3 tock_summary.py
```

**Summarize time for a specific week (current year):**

```bash
python3 tock_summary.py -w 6
```

**Summarize time for a specific week and year:**

```bash
python3 tock_summary.py -w 2026-06
```

**Get help:**

```bash
python3 tock_summary.py --help
```

## Output Format

The tool displays:

1. A header showing the date range
2. Projects sorted by total time (descending)
3. Tasks under each project, also sorted by time
4. A total summary at the bottom

Example output:

```text
============================================================
Time Summary: 2026-02-05 to 2026-02-09
============================================================

ny.ordnet.dk                    15:13
  └─ hugo                        15:13

ddo                              9:11
  └─ euralex                      6:33
  └─ møde                         1:46
  └─ nedbrud                      0:32
  └─ administration               0:20

dsl                              1:34
  └─ læge                         1:34

benchmark                        1:11
  └─ møde                         0:44
  └─ ai-arena                     0:27

────────────────────────────────────────────────────────────
TOTAL                           27:08
============================================================
```

## File Format

The tool expects `~/.tock.txt` to contain entries in one of these formats:

**With end time:**

```text
2026-02-05 09:06 - 2026-02-05 09:26 | ddo | administration
```

**Without end time (ongoing or incomplete):**

```text
2026-02-13 08:39 | dsl | administration
```

Entries without end times are counted as 0 hours in the summary.

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only standard library)
