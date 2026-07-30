import sqlite3
import logging
from contextlib import contextmanager
from config import DB_PATH

logger = logging.getLogger(__name__)


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database():
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repos (
                repo_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                language TEXT,
                stars INTEGER,
                forks INTEGER,
                watchers INTEGER,
                open_issues INTEGER,
                size_kb INTEGER,
                created_at TEXT,
                updated_at TEXT,
                pushed_at TEXT,
                owner TEXT,
                topics TEXT,
                has_wiki BOOLEAN,
                archived BOOLEAN,
                license TEXT,
                fetched_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                status TEXT,
                repos_fetched INTEGER DEFAULT 0,
                repos_stored INTEGER DEFAULT 0,
                error_message TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trending_snapshots (
                snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_id INTEGER NOT NULL,
                stars INTEGER,
                forks INTEGER,
                rank INTEGER,
                fetched_at TEXT NOT NULL,
                FOREIGN KEY (repo_id) REFERENCES repos(repo_id)
            )
        """)

        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_repos_language ON repos(language)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_repos_stars ON repos(stars DESC)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_snapshots_repo ON trending_snapshots(repo_id)"
        )

    logger.info(f"Database initialized at {DB_PATH}")


def insert_repos(repos):
    with get_connection() as conn:
        cursor = conn.cursor()
        stored = 0
        for repo in repos:
            try:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO repos
                    VALUES (:repo_id, :name, :description, :language, :stars, :forks,
                            :watchers, :open_issues, :size_kb, :created_at, :updated_at,
                            :pushed_at, :owner, :topics, :has_wiki, :archived, :license, :fetched_at)
                """,
                    repo,
                )
                stored += 1
            except sqlite3.Error as e:
                logger.error(f"Failed to insert {repo.get('name')}: {e}")
        return stored


def insert_snapshot(repo_id, stars, forks, rank, fetched_at):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO trending_snapshots (repo_id, stars, forks, rank, fetched_at)
            VALUES (?, ?, ?, ?, ?)
        """,
            (repo_id, stars, forks, rank, fetched_at),
        )


def log_run_start():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pipeline_runs (started_at, status) VALUES (datetime('now'), 'running')"
        )
        return cursor.lastrowid


def log_run_end(run_id, repos_fetched, repos_stored, status="success", error=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE pipeline_runs
            SET finished_at = datetime('now'), status = ?, repos_fetched = ?,
                repos_stored = ?, error_message = ?
            WHERE run_id = ?
        """,
            (status, repos_fetched, repos_stored, error, run_id),
        )


def get_recent_runs(limit=10):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM pipeline_runs ORDER BY run_id DESC LIMIT ?
        """,
            (limit,),
        )
        return [dict(row) for row in cursor.fetchall()]


def get_top_repos(limit=20, language=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        if language:
            cursor.execute(
                """
                SELECT * FROM repos WHERE language = ? ORDER BY stars DESC LIMIT ?
            """,
                (language, limit),
            )
        else:
            cursor.execute("SELECT * FROM repos ORDER BY stars DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]
