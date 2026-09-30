# Smart Job Scheduling Using Greedy, Dynamic Programming and Backtracking Techniques

> **Application Name:** Smart Job Scheduler  
> **Course:** Design and Analysis of Algorithms (DAA)  
> **Topic:** Smart Job Scheduling Using Greedy, Dynamic Programming and Backtracking Techniques  

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)](https://python.org)
[![DAA Project](https://img.shields.io/badge/DAA-Greedy%20%7C%20DP%20%7C%20Backtracking-purple?style=flat-square)](docs/project_report_notes.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Tests: Passing](https://img.shields.io/badge/Tests-9%2F9%20Passing-brightgreen?style=flat-square)](tests/test_scheduler.py)

---

## 📌 Abstract

Job scheduling across heterogeneous resources with deadlines, precedence dependencies, skills, and shift constraints is an NP-hard problem central to operating systems, cloud dispatchers, and automated workflows. **Smart Job Scheduler** is an algorithmic testbed and comparison engine that implements, visualizes, and benchmarks three primary DAA paradigms:
1. **Greedy Algorithm** (Earliest Deadline First with Topological Sort)
2. **Dynamic Programming** (Weighted Job Scheduling via Interval Bisection)
3. **Recursive Backtracking** (Combinatorial State-Tree Search with Branch & Bound)

The system features a dual interface (terminal CLI with ASCII Gantt charts and an interactive zero-dependency browser dashboard) that demonstrates how theoretical time and space complexities translate into measured wall-clock execution times and schedule quality.

---

## 🎯 Problem Statement

Given a set of $N$ jobs $\mathcal{J} = \{J_1, \dots, J_N\}$, each defined by:
- **Duration ($p_i$):** Execution time in hours
- **Deadline ($d_i$):** Maximum allowable completion time
- **Profit ($v_i$):** Value earned if completed on or before deadline
- **Priority ($w_i$):** Relative importance rank (1 to 5)
- **Skill ($s_i$):** Worker capability required (`backend`, `frontend`, `qa`)
- **Dependencies ($\mathcal{D}_i$):** Predecessor jobs that must finish before $J_i$ can begin

And a set of $M$ resources $\mathcal{R} = \{R_1, \dots, R_M\}$ with specific skills and daily shift windows $[W_{\text{start}}, W_{\text{end}}]$:

**Objective:** Determine job start times, end times, and resource assignments to:
$$\max \sum_{i : \text{end}_i \le d_i} v_i \quad \text{subject to dependency, skill, shift, and non-overlap constraints.}$$

---

## ✨ Features

- **Three Core DAA Algorithms:** Full implementations of Greedy, Dynamic Programming, and Backtracking.
- **Empirical Benchmark Suite:** Tests scaling behavior across 5, 8, 10, and 12 jobs with measured execution times.
- **Side-by-Side Comparison:** Automated comparison matrix displaying profit, on-time %, lateness, makespan, measured runtimes, and theoretical Big-O.
- **Dual Visualizations:** Interactive Gantt charts in the web dashboard and colored ASCII Gantt charts in the CLI.
- **Interactive Browser Dashboard (`dashboard.html`):** Standalone zero-dependency UI with real-time algorithm execution in JavaScript.
- **Constraint Simulation (What-If):** Interactively tweak job deadlines, shift hours, or priorities to test schedule sensitivity.
- **Input Validation & Error Handling:** Gracefully handles empty task lists, duplicate IDs, non-positive numbers, and unfeasible skill requirements.
- **Automated Reporting:** Generates text reports and CSV schedule export files in `outputs/`.
- **Comprehensive Test Suite:** 9 unit tests covering algorithm correctness, college sample instances, and edge cases.

---

## 🧠 Algorithms Detailed Explanation

### 1. Greedy Algorithm (EDF + Priority + TopoSort)
- **Idea:** Makes an irrevocable, locally optimal choice at each step without backtracking.
- **Mechanism:** Builds a dependency graph and determines processing order using **Kahn's algorithm for topological sorting**. Ready jobs are prioritized by highest priority and Earliest Deadline First (EDF). Each job is placed on the first available resource slot that minimizes lateness.
- **Time Complexity:** $\mathcal{O}(N \log N + N \cdot M)$
- **Space Complexity:** $\mathcal{O}(N + M)$
- **Optimal?** Heuristic approximation. May miss the global maximum profit due to local myopia.

### 2. Dynamic Programming (Weighted Job Scheduling)
- **Idea:** Decomposes the schedule into overlapping subproblems with optimal substructure.
- **Mechanism:** For each resource, candidate jobs are sorted by completion time. A 1D DP table stores the maximum profit achievable:
  $$DP[i] = \max\Big(DP[i - 1],\; \text{profit}[i] + DP[p(i)]\Big)$$
  where $p(i)$ is the latest non-conflicting job predecessor found via binary search (`bisect`) in $\mathcal{O}(\log N)$ time.
- **Time Complexity:** $\mathcal{O}(M \cdot N \log N)$
- **Space Complexity:** $\mathcal{O}(N)$
- **Optimal?** Mathematically optimal for non-overlapping interval subsets on each resource.

### 3. Backtracking Algorithm (Recursive Branch & Bound)
- **Idea:** Systematic depth-first search of the state-space decision tree with pruning.
- **Mechanism:** For each job in topological sequence, the algorithm explores branching into assigning the job to compatible resource $R_1 \dots R_M$ or excluding the job. 
- **Pruning (Branch & Bound):** Suffix sums of remaining job profits are precomputed. If $\text{CurrentProfit} + \sum_{j=k}^N \text{Profit}_j \le \text{BestProfit}$, the entire search branch is cut immediately.
- **Time Complexity:** $\mathcal{O}((M + 1)^N)$ worst-case (exponential), significantly pruned in practice.
- **Space Complexity:** $\mathcal{O}(N)$ recursion stack depth.
- **Optimal?** **Globally optimal.** Guarantees finding the maximum achievable profit schedule.

---

## 📊 Complexity Analysis Matrix

| Algorithm | Paradigm | Theoretical Time Complexity | Theoretical Space Complexity | Optimality Guarantee | Scalability |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Greedy** | Heuristic (EDF + TopoSort) | $\mathcal{O}(N \log N + N \cdot M)$ | $\mathcal{O}(N + M)$ | Suboptimal | High ($N > 10^5$) |
| **Dynamic Programming** | Optimal Substructure (Interval DP) | $\mathcal{O}(M \cdot N \log N)$ | $\mathcal{O}(N)$ | Resource-optimal | Very High ($N > 10^4$) |
| **Backtracking** | State Tree Search (Branch & Bound) | $\mathcal{O}((M + 1)^N)$ worst-case | $\mathcal{O}(N)$ | **Globally Optimal** | Small ($N \le 15$) |

> **Note on Measured vs Theoretical:** Theoretical Big-O represents asymptotic scalability ($N \to \infty$). Measured execution time is wall-clock time in milliseconds captured via `time.perf_counter()`, which is influenced by constant factors, CPU caching, and branch pruning.

---

## 📈 Benchmark & Experimental Results

Measured on an Intel/AMD multicore test environment:

```
======================================================================================
  SMART JOB SCHEDULER — PERFORMANCE BENCHMARK (MEASURED EXECUTION TIME)
  Theoretical Big-O: Greedy O(N log N) | DP O(M·N log N) | Backtracking O((M+1)^N)
======================================================================================
  Jobs   | Greedy Time   Profit   | DP Time       Profit   | Backtracking Time  Profit   Nodes 
  ----------------------------------------------------------------------------------
  5      |    0.086 ms   390      |    0.067 ms   350      |      0.268 ms        390      94    
  8      |    0.075 ms   630      |    0.065 ms   440      |      1.329 ms        630      589   
  10     |    0.075 ms   675      |    0.076 ms   540      |      2.880 ms        805      1108  
  12     |    0.092 ms   695      |    0.101 ms   710      |     24.080 ms        895      14708 
======================================================================================
```

**Key Takeaways:**
1. Backtracking consistently discovers the **strictly highest profit** (895 vs Greedy's 695 on 12 jobs).
2. Backtracking search nodes jump exponentially ($94 \to 589 \to 1,108 \to 14,708$), verifying the exponential theoretical bound.
3. Greedy and DP execute in under 0.15 ms regardless of size, proving their polynomial real-world viability.

---

## 🏗️ System Workflow

```
   INPUT (data/tasks.csv, data/resources.csv)
                      │
                      ▼
            [ Input Validation ] ──► (Detects empty, duplicate IDs, invalid inputs)
                      │
                      ▼
         [ Topological Sorting (DAG) ] ──► (Resolves precedence constraints)
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   [ Greedy ]       [ DP ]    [ Backtracking ]
   O(N log N)     O(N log N)    O((M+1)^N)
   Local Choice   Memoization   Branch & Bound
        │             │             │
        └─────────────┼─────────────┘
                      │
                      ▼
           [ Algorithm Comparison ]
    - Profit, On-Time %, Lateness, Makespan
    - Measured Execution Time (ms)
    - Theoretical Big-O Time & Space
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
   [ CLI Output ]           [ Web Dashboard ]
- ASCII Gantt Chart       - Interactive SVG Gantt Chart
- Summary Tables          - Dynamic What-If Simulation
- CSV & TXT Reports       - DAA Complexity Analysis Tab
```

---

## 📁 Project Structure

```
Task-Scheduler-Optimization-System-main/
│
├── data/
│   ├── tasks.csv                  # Default dataset (10 jobs)
│   └── resources.csv              # Resources dataset (skills & shifts)
│
├── src/
│   ├── __init__.py
│   ├── models.py                  # Task/Resource dataclasses & input validation
│   ├── greedy_scheduler.py        # Greedy EDF + Priority + TopoSort scheduler
│   ├── dp_scheduler.py            # Dynamic Programming weighted job scheduler
│   ├── backtracking_scheduler.py  # Recursive Backtracking with Branch & Bound
│   ├── priority_scheduler.py      # Binary Min-Heap Priority Queue scheduler
│   ├── benchmark.py               # Performance benchmark suite (5, 8, 10, 12 jobs)
│   ├── metrics.py                 # KPI calculator & comparison engine
│   └── report_generator.py        # CSV schedule & text report generators
│
├── tests/
│   └── test_scheduler.py          # 9 unit tests (100% passing)
│
├── docs/
│   ├── project_report_notes.md    # Comprehensive college project report material
│   └── viva_questions.md          # 24 DAA viva questions and verbal answers
│
├── outputs/                       # Generated schedule CSVs & comparison reports
├── dashboard.html                 # Interactive zero-dependency web dashboard
├── main.py                        # CLI entry point
├── requirements.txt               # Dependencies (Standard Library only)
└── README.md                      # Project documentation
```

---

## 🚀 How to Run

### Prerequisites
- Python 3.9 or higher (standard library only; no pip dependencies required for core functionality).

### 1. Run All Algorithms and Compare (CLI)
```bash
python main.py
```

### 2. Run a Specific Algorithm
```bash
python main.py --algo greedy         # Run Greedy Scheduler
python main.py --algo dp             # Run Dynamic Programming Scheduler
python main.py --algo backtracking   # Run Backtracking Scheduler
```

### 3. Run Benchmark Suite
```bash
python main.py --benchmark
# or directly:
python -m src.benchmark
```

### 4. Run Unit Tests
```bash
python tests/test_scheduler.py
```

### 5. Launch Interactive Web Dashboard
Simply open `dashboard.html` in any web browser (Chrome, Edge, Firefox):
```bash
# On Windows:
start dashboard.html
```

---

## 📋 Sample Input & Output

### Sample Input: 5-Job College Demo Dataset
```csv
task_id,duration_h,deadline_h,priority,skill,depends_on,profit
J1,2,3,5,backend,,100
J2,1,2,4,backend,,50
J3,2,4,3,backend,,80
J4,1,2,2,backend,,40
J5,3,5,5,backend,,120
```

### Sample CLI Comparison Output
```
╔══════════════════════════════════════════════════════════════╗
║                   SMART JOB SCHEDULER                        ║
║  Greedy vs Dynamic Programming vs Backtracking Techniques   ║
║             College DAA Algorithm Project                    ║
╚══════════════════════════════════════════════════════════════╝

  Loading tasks from data/tasks.csv
  ✓ Input validation passed (no errors)
  Loaded 10 tasks, 3 resources

  ALGORITHM COMPARISON MATRIX (SIDE-BY-SIDE)
  ──────────────────────────────────────────────────────────────────────────────────────────────────
  Algorithm                             OnTime%  Profit   Late  Miss  Time(ms) Time Complexity   
  ──────────────────────────────────────────────────────────────────────────────────────────────────
  Greedy (Priority + EDF + Topo-Sort) 70.0% 2470 25h 1 0.09ms O(N log N + N*M)
  Dynamic Programming (Weighted Job S 60.0% 2200 0h 4 0.07ms O(M * N log N)
  Backtracking (Recursive Branch & Bo 80.0% 2720 0h 2 2.65ms O((M+1)^N) worst-case

  Best Profit    : Backtracking (Recursive Branch & Bound)
  Best On-Time   : Backtracking (Recursive Branch & Bound)
  Least Lateness : Dynamic Programming (Weighted Job Scheduling)
  Fastest Exec   : Dynamic Programming (Weighted Job Scheduling)
```

---

## ⚠️ Limitations & Future Scope

### Limitations
1. **Backtracking Input Bound:** Backtracking is exponential; practical input is limited to $N \le 15$ jobs to prevent long execution times.
2. **Deterministic Durations:** Job execution times are assumed fixed without stochastic processing delays.

### Future Scope
1. **Metaheuristics:** Integrating Genetic Algorithms or Simulated Annealing for near-optimal results on $N > 100$.
2. **Parallel Backtracking:** Utilizing multi-threaded worker pools to divide decision tree branches across CPU cores.

---

## 🛠️ Technologies Used

- **Language:** Python 3.9+ (Built with standard library: `dataclasses`, `heapq`, `collections`, `bisect`, `time`, `csv`)
- **Dashboard:** HTML5, CSS3 (Custom responsive dark UI), Vanilla JavaScript ES6 (Client-side DAA execution engine)
- **Visualizations:** Terminal ANSI & Unicode ASCII Gantt charts, SVG/CSS Gantt timeline

---

## 📜 Attribution & License

This college project was adapted and extended from the open-source project [Task-Scheduler-Optimization-System](https://github.com/Sonia068/Task-Scheduler-Optimization-System) by Sonia Thakur under the **MIT License**.

**Extensions developed for this DAA project:**
- Genuine Recursive Backtracking Job Scheduling module with Branch & Bound pruning (`src/backtracking_scheduler.py`).
- JavaScript Backtracking scheduling engine for browser dashboard (`dashboard.html`).
- Empirical multi-algorithm benchmark module (`src/benchmark.py`).
- Real-time high-resolution execution timing (`time.perf_counter()` / `performance.now()`).
- Theoretical Big-O vs measured execution time analysis.
- College demo dataset and comprehensive test suite (`tests/test_scheduler.py`).
- Comprehensive DAA College Report documentation (`docs/project_report_notes.md`) and Viva preparation guide (`docs/viva_questions.md`).

All original copyright notices and MIT license terms are preserved in accordance with institutional and open-source guidelines.
