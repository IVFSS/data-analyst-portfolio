import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data")
DB_PATH = os.path.join(DATA_PATH, "github_trends.db")
LOG_PATH = os.path.join(DATA_PATH, "pipeline.log")

FETCH_INTERVAL_MINUTES = 30
REQUEST_TIMEOUT = 30
USER_AGENT = "data-analyst-portfolio"
API_BASE = "https://api.github.com"


def ensure_dirs():
    os.makedirs(DATA_PATH, exist_ok=True)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
