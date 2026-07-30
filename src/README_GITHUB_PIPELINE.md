# GitHub Trends Pipeline

Real-time data pipeline that fetches trending repositories from GitHub API, stores them in SQLite, and visualizes trends across programming languages.

## Problem

Track emerging technology trends by monitoring GitHub repository popularity across multiple programming languages. Identify rising stars, trending topics, and language adoption patterns.

## Approach

- Fetch trending repos weekly from GitHub API across 5 languages (Python, JavaScript, TypeScript, Go, Rust)
- Store in normalized SQLite schema with separate tables for repos, snapshots, and pipeline runs
- Auto-refresh every 30 minutes via scheduler
- Track star growth, topic frequency, and language distribution

## Architecture

```
GitHub API → Fetch → Parse → SQLite → Analysis → Visualization
                ↓
         Pipeline Logs
```

**Components:**
- `config.py` — Configuration and paths
- `github_api.py` — API client with error handling and logging
- `database.py` — SQLite schema, connection management
- `pipeline.py` — ETL orchestration
- `scheduler.py` — Scheduled execution with graceful shutdown
- `analyze_trends.py` — Trend analysis and visualization

## Database Schema

```sql
repos (repo_id, name, language, stars, forks, ...)
trending_snapshots (snapshot_id, repo_id, stars, rank, fetched_at)
pipeline_runs (run_id, started_at, status, repos_fetched, error_message)
```

## How to Run

```bash
# Single run
python src/pipeline.py

# Continuous scheduling
python src/scheduler.py

# Analyze trends
python src/analyze_trends.py
```

## Key Findings

- AI/LLM topics dominate (llm, codex, mcp, claude-code)
- Python leads in repo count with highest average stars
- Top trending topics: llm, codex, mcp, typescript, rust

## Technologies

Python, SQLite, Requests, Schedule, GitHub REST API