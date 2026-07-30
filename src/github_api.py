import requests
import logging
from datetime import datetime, timezone
from config import API_BASE, USER_AGENT, REQUEST_TIMEOUT, LOG_PATH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def fetch_trending_repos(language="python", since="daily"):
    url = f"{API_BASE}/search/repositories"
    params = {
        "q": f"language:{language} created:>{_date_threshold(since)}",
        "sort": "stars",
        "order": "desc",
        "per_page": 30,
    }
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": USER_AGENT}

    try:
        response = requests.get(
            url, params=params, headers=headers, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        data = response.json()
        logger.info(
            f"Fetched {data.get('total_count', 0)} repos for {language} ({since})"
        )
        return data.get("items", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        return []


def fetch_repo_details(owner, repo):
    url = f"{API_BASE}/repos/{owner}/{repo}"
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": USER_AGENT}

    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch details for {owner}/{repo}: {e}")
        return {}


def _date_threshold(since):
    days = {"daily": 7, "weekly": 30, "monthly": 90}.get(since, 7)
    return (
        datetime.now(timezone.utc) - __import__("datetime").timedelta(days=days)
    ).strftime("%Y-%m-%d")


def parse_repo(repo):
    return {
        "repo_id": repo.get("id"),
        "name": repo.get("full_name"),
        "description": (repo.get("description") or "")[:500],
        "language": repo.get("language"),
        "stars": repo.get("stargazers_count", 0),
        "forks": repo.get("forks_count", 0),
        "watchers": repo.get("watchers_count", 0),
        "open_issues": repo.get("open_issues_count", 0),
        "size_kb": repo.get("size", 0),
        "created_at": repo.get("created_at"),
        "updated_at": repo.get("updated_at"),
        "pushed_at": repo.get("pushed_at"),
        "owner": repo.get("owner", {}).get("login", ""),
        "topics": ",".join(repo.get("topics", [])),
        "has_wiki": repo.get("has_wiki", False),
        "archived": repo.get("archived", False),
        "license": (repo.get("license") or {}).get("name", "None"),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
