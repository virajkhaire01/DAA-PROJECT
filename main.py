#!/usr/bin/env python3
"""
Smart Job Scheduler
====================================
Smart Job Scheduling Using Greedy, Dynamic Programming and Backtracking Techniques
main.py - CLI Entry Point & Comparison Engine

Run with:
    python main.py                          # run all algorithms and compare
    python main.py --algo greedy            # run Greedy algorithm
    python main.py --algo dp                # run Dynamic Programming
    python main.py --algo backtracking      # run Backtracking
    python main.py --compare                # side-by-side comparison
    python main.py --benchmark              # run 5, 8, 10, 12 jobs benchmark
    python main.py --add-task               # interactive task addition
"""

import argparse
import sys
import os

# Safe UTF-8 encoding configuration for Windows terminals
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Ensure src/ is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models import load_tasks, load_resources, validate_tasks, Task
from src.greedy_scheduler import GreedyScheduler
from src.dp_scheduler import DPScheduler
from src.backtracking_scheduler import BacktrackingScheduler
from src.priority_scheduler import PriorityQueueScheduler
from src.metrics import compute_kpis, compare_algorithms
from src.report_generator import (
    generate_schedule_csv, generate_text_report, generate_comparison_report
)
from src.benchmark import run_benchmarks, print_benchmark_table


# ─── ANSI colors ──────────────────────────────────────────────────────────────
class C:
    RESET   = '\033[0m'
    BOLD    = '\033[1m'
    CYAN    = '\033[96m'
    GREEN   = '\033[92m'
    YELLOW  = '\033[93m'
    RED     = '\033[91m'
    PURPLE  = '\033[95m'
    GREY    = '\033[90m'
    WHITE   = '\033[97m'

def color(text, *codes):
    return ''.join(codes) + str(text) + C.RESET

def print_banner():
    banner = f"""
{C.CYAN}{C.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                   SMART JOB SCHEDULER                        ║
║  Greedy vs Dynamic Programming vs Backtracking Techniques   ║
║             College DAA Algorithm Project                    ║
╚══════════════════════════════════════════════════════════════╝
{C.RESET}"""
    print(banner)

def print_kpis(summary: dict):
    kpi = compute_kpis(summary)
    print(f"\n  {color('ALGORITHM       :', C.GREY)} {color(kpi['algorithm'], C.CYAN, C.BOLD)}")
    print(f"  {'─'*64}")
    print(f"  {color('Total Tasks     :', C.GREY)} {color(kpi['total_tasks'], C.WHITE, C.BOLD)}")
    print(f"  {color('Scheduled       :', C.GREY)} {color(kpi['scheduled_count'], C.GREEN)}")
    print(f"  {color('On Time         :', C.GREY)} {color(kpi['on_time_count'], C.GREEN)} "
          f"  ({color(kpi['on_time_pct'], C.GREEN)}%)")
    print(f"  {color('Late Tasks      :', C.GREY)} {color(kpi['late_count'], C.YELLOW)}"
          f"  (total lateness: {color(kpi['total_lateness_h'], C.YELLOW)}h)")
    print(f"  {color('Missed          :', C.GREY)} {color(kpi['missed_count'], C.RED)}")
    print(f"  {color('Total Profit    :', C.GREY)} {color(kpi['total_profit'], C.PURPLE, C.BOLD)}"
          f"  ({color(kpi['profit_efficiency_pct'], C.PURPLE)}% efficiency)")
    print(f"  {color('Makespan        :', C.GREY)} {color(kpi['makespan'], C.CYAN)}h")
    print(f"  {color('Measured Time   :', C.GREY)} {color(str(kpi.get('execution_time_ms', 0.0)) + ' ms', C.WHITE, C.BOLD)}")
    print(f"  {color('Time Complexity :', C.GREY)} {color(kpi.get('time_complexity', 'N/A'), C.CYAN)} (Theoretical Big-O)")
    print(f"  {color('Space Complexity:', C.GREY)} {color(kpi.get('space_complexity', 'N/A'), C.CYAN)} (Theoretical Big-O)")
    if 'nodes_explored' in kpi:
        print(f"  {color('Search Nodes    :', C.GREY)} {color(kpi['nodes_explored'], C.YELLOW)} (Backtracking tree nodes)")

def print_gantt(summary: dict, horizon: int = 72):
    """Print ASCII Gantt chart to terminal."""
    scheduled = sorted(summary.get('scheduled', []), key=lambda t: t.start_h or 0)

    if not scheduled:
        print(f"\n  {color('No scheduled tasks to display.', C.RED)}")
        return

    from collections import defaultdict
    res_tasks = defaultdict(list)
    for t in scheduled:
        res_tasks[t.assigned_resource].append(t)

    max_time = min(max(t.end_h for t in scheduled) + 4, 72)

    print(f"\n  {color('GANTT CHART (ASCII)', C.CYAN, C.BOLD)}  [each block ~ 1h]")
    print(f"  {'─'*70}")

    ruler = '  {:>8}  '.format('Resource')
    for h in range(0, max_time + 1, 8):
        ruler += f'{h:<8}'
    print(color(ruler, C.GREY))

    for rid, tasks in sorted(res_tasks.items()):
        row = ['.'] * max_time
        for t in tasks:
            s, e = t.start_h, min(t.end_h, max_time)
            char = '#' if not t.is_late else '='
            for i in range(s, e):
                if i < max_time:
                    row[i] = char
            tid_chars = list(t.task_id)
            for j, ch in enumerate(tid_chars):
                pos = s + j
                if pos < max_time:
                    row[pos] = ch

        row_str = ''.join(row)
        colored_row = ''
        i = 0
        while i < len(row_str):
            if row_str[i] == '#':
                colored_row += color('#', C.GREEN)
            elif row_str[i] == '=':
                colored_row += color('=', C.YELLOW)
            else:
                colored_row += color(row_str[i], C.GREY)
            i += 1

        print(f"  {color(rid+' ', C.CYAN, C.BOLD):>10}  {colored_row}")

    print(f"\n  {color('# On Time', C.GREEN)}   {color('= Late', C.YELLOW)}")

    if summary.get('missed'):
        print(f"\n  {color('! MISSED TASKS:', C.RED, C.BOLD)}")
        for t in summary['missed']:
            print(f"    {color(t.task_id, C.RED)} -- deadline {t.deadline_h}h, priority {t.priority}, skill {t.skill}, profit {t.profit}")

def print_task_table(summary: dict):
    """Print detailed task execution table."""
    print(f"\n  {color('TASK EXECUTION DETAILS', C.CYAN, C.BOLD)}")
    print(f"  {'─'*92}")
    header = f"  {'Task':<8} {'Res':<5} {'Skill':<10} {'Prio':>5} {'Dur':>5} {'Ddl':>5} {'Start':>6} {'End':>6} {'Late':>6} {'Profit':>7} {'Status':<10}"
    print(color(header, C.GREY))
    print(f"  {'─'*92}")

    all_tasks = sorted(summary.get('scheduled', []), key=lambda t: t.start_h or 0)
    all_tasks += summary.get('missed', [])

    for t in all_tasks:
        if t.is_missed:
            status = color('MISSED', C.RED)
            row = f"  {color(t.task_id, C.RED):<8} {'N/A':<5} {t.skill:<10} {t.priority:>5} {t.duration_h:>5}h {t.deadline_h:>4}h {'N/A':>6} {'N/A':>6} {'N/A':>6} {color(str(t.profit), C.PURPLE):>7} {status}"
        elif t.is_late:
            status = color('LATE', C.YELLOW)
            row = f"  {color(t.task_id, C.YELLOW):<8} {color(t.assigned_resource, C.CYAN):<5} {t.skill:<10} {t.priority:>5} {t.duration_h:>5}h {t.deadline_h:>4}h {t.start_h:>5}h {t.end_h:>5}h {color(str(t.lateness_h), C.YELLOW):>5}h {color(str(t.profit), C.PURPLE):>7} {status}"
        else:
            status = color('OK', C.GREEN)
            row = f"  {color(t.task_id, C.GREEN):<8} {color(t.assigned_resource, C.CYAN):<5} {t.skill:<10} {t.priority:>5} {t.duration_h:>5}h {t.deadline_h:>4}h {t.start_h:>5}h {t.end_h:>5}h {'0':>5}h {color(str(t.profit), C.PURPLE):>7} {status}"
        print(row)

def print_comparison(comp: dict):
    """Print side-by-side algorithm comparison with execution times and theoretical complexities."""
    print(f"\n  {color('ALGORITHM COMPARISON MATRIX (SIDE-BY-SIDE)', C.CYAN, C.BOLD)}")
    print(f"  {'─'*98}")
    header = f"  {'Algorithm':<36} {'OnTime%':>8} {'Profit':>7} {'Late':>6} {'Miss':>5} {'Time(ms)':>9} {'Time Complexity':<18}"
    print(color(header, C.GREY))
    print(f"  {'─'*98}")

    results = comp['comparison']
    max_profit = max(r['total_profit'] for r in results)
    max_ontime = max(float(r['on_time_pct']) for r in results)
    min_late = min(r['total_lateness_h'] for r in results)
    min_time = min(r['execution_time_ms'] for r in results)

    for r in results:
        algo = r['algorithm'][:35]
        profit_c = C.GREEN if r['total_profit'] == max_profit else C.WHITE
        ontime_c = C.GREEN if float(r['on_time_pct']) == max_ontime else C.WHITE
        late_c = C.GREEN if r['total_lateness_h'] == min_late else C.YELLOW
        miss_c = C.GREEN if r['missed_count'] == 0 else C.RED
        time_c = C.GREEN if r['execution_time_ms'] == min_time else C.WHITE

        time_val = r.get("execution_time_ms", 0.0)
        time_str = f"{time_val:.2f}ms"
        print(f"  {color(algo, C.WHITE):<36} "
              f"{color(r['on_time_pct'], ontime_c):>7}% "
              f"{color(r['total_profit'], profit_c):>7} "
              f"{color(r['total_lateness_h'], late_c):>5}h "
              f"{color(r['missed_count'], miss_c):>5} "
              f"{color(time_str, time_c):>9} "
              f"{color(r.get('time_complexity', 'N/A'), C.CYAN):<18}")


    print(f"\n  {color('Best Profit    :', C.GREY)} {color(comp['best_profit_algo'], C.GREEN)}")
    print(f"  {color('Best On-Time   :', C.GREY)} {color(comp['best_ontime_algo'], C.GREEN)}")
    print(f"  {color('Least Lateness :', C.GREY)} {color(comp['best_lateness_algo'], C.GREEN)}")
    print(f"  {color('Fastest Exec   :', C.GREY)} {color(comp.get('fastest_algo', 'N/A'), C.GREEN)}")

def interactive_add_task(tasks):
    """Interactively add a new task."""
    print(f"\n  {color('ADD NEW TASK', C.CYAN, C.BOLD)}")
    print(f"  {'─'*40}")
    tid = input(f"  {color('Task ID:', C.GREY)} ").strip()
    if not tid:
        print(color("  Cancelled.", C.RED))
        return tasks
    dur = int(input(f"  {color('Duration (hours):', C.GREY)} ") or 3)
    ddl = int(input(f"  {color('Deadline (hours):', C.GREY)} ") or 48)
    prio = int(input(f"  {color('Priority (1-5):', C.GREY)} ") or 3)
    skill = input(f"  {color('Skill (backend/frontend/qa):', C.GREY)} ").strip() or 'backend'
    profit = int(input(f"  {color('Profit score:', C.GREY)} ") or 100)
    deps_raw = input(f"  {color('Dependencies (e.g. T1|T2, blank for none):', C.GREY)} ").strip()
    deps = [d.strip() for d in deps_raw.split('|') if d.strip()]

    tasks.append(Task(
        task_id=tid, duration_h=dur, deadline_h=ddl, priority=prio,
        skill=skill, depends_on=deps, profit=profit
    ))
    print(f"  {color(f'Task {tid} added successfully!', C.GREEN)}")
    return tasks


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Smart Job Scheduler - Greedy, DP, Backtracking Techniques'
    )
    parser.add_argument('--algo', choices=['greedy', 'dp', 'backtracking', 'pq', 'all'], default='all',
                        help='Algorithm to run (default: all)')
    parser.add_argument('--horizon', type=int, default=72, help='Planning horizon in hours (default: 72)')
    parser.add_argument('--compare', action='store_true', help='Compare all algorithms side-by-side')
    parser.add_argument('--benchmark', action='store_true', help='Run benchmark comparing 5, 8, 10, 12 jobs')
    parser.add_argument('--add-task', action='store_true', help='Interactively add a task')
    parser.add_argument('--no-report', action='store_true', help='Skip file report generation')
    parser.add_argument('--tasks', default='data/tasks.csv', help='Tasks CSV file path')
    parser.add_argument('--resources', default='data/resources.csv', help='Resources CSV file path')
    args = parser.parse_args()

    print_banner()

    # Benchmark mode
    if args.benchmark:
        print(f"  {color('Running performance benchmark suite across job sizes...', C.CYAN)}")
        b_res = run_benchmarks([5, 8, 10, 12], args.horizon)
        print_benchmark_table(b_res)
        return

    # Load data
    print(f"  {color('Loading tasks from', C.GREY)} {color(args.tasks, C.CYAN)}")
    tasks = load_tasks(args.tasks)
    resources = load_resources(args.resources)

    # Validate tasks
    is_valid, errors = validate_tasks(tasks)
    if not is_valid:
        print(f"\n  {color('Input Validation Warnings:', C.YELLOW, C.BOLD)}")
        for err in errors:
            print(f"    - {err}")
    else:
        print(f"  {color('✓ Input validation passed (no errors)', C.GREEN)}")

    print(f"  {color(f'Loaded {len(tasks)} tasks, {len(resources)} resources', C.GREEN)}\n")

    # Interactive add
    if args.add_task:
        tasks = interactive_add_task(tasks)

    summaries = []

    # 1. Greedy Algorithm
    if args.algo in ('greedy', 'all') or args.compare:
        print(f"\n{color('  ► Running Greedy Scheduler (EDF + Priority + TopoSort)...', C.CYAN)}")
        s = GreedyScheduler(tasks, resources, args.horizon).get_summary()
        summaries.append(s)
        print_kpis(s)
        print_gantt(s, args.horizon)
        print_task_table(s)
        if not args.no_report:
            csv_path = generate_schedule_csv(s, 'schedule_greedy.csv')
            txt_path = generate_text_report(s)
            print(f"\n  {color('Reports saved:', C.GREY)} {color(csv_path, C.CYAN)}, {color(txt_path, C.CYAN)}")

    # 2. Dynamic Programming
    if args.algo in ('dp', 'all') or args.compare:
        print(f"\n{color('  ► Running Dynamic Programming Scheduler (Weighted Job Scheduling)...', C.GREEN)}")
        s = DPScheduler(tasks, resources, args.horizon).get_summary()
        summaries.append(s)
        print_kpis(s)
        if args.algo == 'dp':
            print_gantt(s, args.horizon)
            print_task_table(s)
        if not args.no_report:
            generate_schedule_csv(s, 'schedule_dp.csv')
            generate_text_report(s)

    # 3. Backtracking Algorithm
    if args.algo in ('backtracking', 'all') or args.compare:
        print(f"\n{color('  ► Running Backtracking Scheduler (Recursive Branch & Bound)...', C.PURPLE)}")
        if len(tasks) > 15:
            print(f"    {color('Notice:', C.YELLOW)} Backtracking is exponential O((M+1)^N). Running on {len(tasks)} tasks...")
        s = BacktrackingScheduler(tasks, resources, args.horizon).get_summary()
        summaries.append(s)
        print_kpis(s)
        if args.algo == 'backtracking':
            print_gantt(s, args.horizon)
            print_task_table(s)
        if not args.no_report:
            generate_schedule_csv(s, 'schedule_backtracking.csv')
            generate_text_report(s)

    # 4. Priority Queue (Heap)
    if args.algo == 'pq':
        print(f"\n{color('  ► Running Priority Queue (Min-Heap) Scheduler...', C.YELLOW)}")
        s = PriorityQueueScheduler(tasks, resources, args.horizon).get_summary()
        summaries.append(s)
        print_kpis(s)
        print_gantt(s, args.horizon)
        print_task_table(s)
        if not args.no_report:
            generate_schedule_csv(s, 'schedule_pq.csv')
            generate_text_report(s)

    # Comparison
    if (args.compare or args.algo == 'all') and len(summaries) > 1:
        comp = compare_algorithms(summaries)
        print_comparison(comp)
        if not args.no_report:
            generate_comparison_report(comp)
            print(f"\n  {color('Comparison report saved to outputs/comparison_report.txt', C.CYAN)}")

    print(f"\n  {color('✓ Execution complete! Open dashboard.html in your browser for the interactive UI.', C.GREEN, C.BOLD)}\n")


if __name__ == '__main__':
    main()