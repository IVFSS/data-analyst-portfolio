import logging
from datetime import datetime, timezone
from github_api import fetch_trending_repos, parse_repo
from database import (
    init_database,
    insert_repos,
    insert_snapshot,
    log_run_start,
    log_run_end,
    get_recent_runs,
    get_top_repos,
)

logger = logging.getLogger(__name__)

LANGUAGES = ["python", "javascript", "typescript", "go", "rust"]


def run_pipeline():
    run_id = log_run_start()
    logger.info(f"Pipeline run {run_id} started")

    total_fetched = 0
    total_stored = 0
    all_repos = []

    try:
        for lang in LANGUAGES:
            repos = fetch_trending_repos(language=lang, since="weekly")
            total_fetched += len(repos)

            for rank, repo in enumerate(repos, start=1):
                parsed = parse_repo(repo)
                all_repos.append(parsed)

        unique_repos = {r["repo_id"]: r for r in all_repos}
        total_stored = insert_repos(list(unique_repos.values()))

        now = datetime.now(timezone.utc).isoformat()
        for rank, repo in enumerate(all_repos, start=1):
            insert_snapshot(repo["repo_id"], repo["stars"], repo["forks"], rank, now)

        log_run_end(run_id, total_fetched, total_stored)
        logger.info(
            f"Pipeline complete: fetched {total_fetched}, stored {total_stored} unique repos"
        )
        return total_fetched, total_stored

    except Exception as e:
        log_run_end(run_id, total_fetched, total_stored, status="failed", error=str(e))
        logger.error(f"Pipeline failed: {e}")
        raise


def print_status():
    print("\n" + "=" * 60)
    print("RECENT PIPELINE RUNS")
    print("=" * 60)

    runs = get_recent_runs(5)
    for run in runs:
        print(
            f"Run #{run['run_id']}: {run['status']} - "
            f"Fetched: {run['repos_fetched']}, Stored: {run['repos_stored']}"
        )
        print(f"  Started: {run['started_at']}, Finished: {run['finished_at']}")

    print("\n" + "=" * 60)
    print("TOP REPOSITORIES (ALL LANGUAGES)")
    print("=" * 60)

    top = get_top_repos(limit=10)
    for i, repo in enumerate(top, start=1):
        print(
            f"{i}. {repo['name']} ({repo['language']}) - "
            f"{repo['stars']:,} stars, {repo['forks']:,} forks"
        )


if __name__ == "__main__":
    init_database()
    run_pipeline()
    print_status()
