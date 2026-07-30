import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
from config import DB_PATH

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs")


def load_recent_snapshots(days=7):
    conn = sqlite3.connect(DB_PATH)
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()

    query = """
        SELECT r.repo_id, r.name, r.language, r.owner, r.description,
               s.stars, s.forks, s.rank, s.fetched_at
        FROM trending_snapshots s
        JOIN repos r ON s.repo_id = r.repo_id
        WHERE s.fetched_at > ?
        ORDER BY s.fetched_at DESC, s.rank ASC
    """
    df = pd.read_sql_query(query, conn, params=(cutoff,))
    conn.close()
    return df


def analyze_languages(df):
    print("\n" + "=" * 60)
    print("LANGUAGE DISTRIBUTION")
    print("=" * 60)

    lang_counts = df["language"].value_counts()
    print(lang_counts)

    lang_stats = (
        df.groupby("language")
        .agg(
            repos=("name", "count"),
            avg_stars=("stars", "mean"),
            max_stars=("stars", "max"),
            avg_rank=("rank", "mean"),
        )
        .round(2)
        .sort_values("repos", ascending=False)
    )
    print("\nLanguage Statistics:")
    print(lang_stats)

    return lang_stats


def analyze_top_movers(df):
    print("\n" + "=" * 60)
    print("STAR GROWTH ANALYSIS")
    print("=" * 60)

    df["fetched_date"] = pd.to_datetime(df["fetched_at"]).dt.date
    growth = (
        df.groupby(["name", "language"])
        .agg(
            first_stars=("stars", "first"),
            last_stars=("stars", "last"),
            snapshots=("fetched_at", "count"),
        )
        .reset_index()
    )
    growth["growth"] = growth["last_stars"] - growth["first_stars"]
    growth["growth_pct"] = (growth["growth"] / growth["first_stars"] * 100).round(2)

    top_movers = growth.sort_values("growth", ascending=False).head(10)
    print("\nTop 10 Star Growth:")
    print(
        top_movers[
            ["name", "language", "first_stars", "last_stars", "growth", "growth_pct"]
        ].to_string(index=False)
    )

    return top_movers


def analyze_topics(df):
    print("\n" + "=" * 60)
    print("TOP TOPICS")
    print("=" * 60)

    all_topics = []
    conn = sqlite3.connect(DB_PATH)
    topics_df = pd.read_sql_query("SELECT topics FROM repos WHERE topics != ''", conn)
    conn.close()

    for topics_str in topics_df["topics"].dropna():
        if topics_str:
            all_topics.extend([t.strip() for t in topics_str.split(",") if t.strip()])

    topic_counts = pd.Series(all_topics).value_counts().head(15)
    print(topic_counts)

    return topic_counts


def create_dashboard(df, lang_stats, top_movers, topic_counts):
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))

    top_langs = lang_stats.head(10)
    axes[0, 0].barh(top_langs.index, top_langs["repos"], color="steelblue")
    axes[0, 0].set_title("Repositories by Language")
    axes[0, 0].set_xlabel("Count")

    lang_colors = ["#3572A5", "#F1E05A", "#2B7489", "#00ADD8", "#DEA584"]
    lang_pie = df["language"].value_counts().head(5)
    axes[0, 1].pie(
        lang_pie.values, labels=lang_pie.index, autopct="%1.1f%%", colors=lang_colors
    )
    axes[0, 1].set_title("Language Share (Top 5)")

    axes[1, 0].barh(
        top_movers["name"].head(10),
        top_movers["growth"].head(10),
        color="coral",
    )
    axes[1, 0].set_title("Top 10 Star Growth")
    axes[1, 0].set_xlabel("Stars Gained")

    axes[1, 1].barh(
        topic_counts.head(10).index, topic_counts.head(10).values, color="green"
    )
    axes[1, 1].set_title("Top Trending Topics")
    axes[1, 1].set_xlabel("Count")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_PATH, "github_trends_analysis.png"), dpi=150)
    print(f"\nSaved: {OUTPUT_PATH}/github_trends_analysis.png")
    plt.close()


def main():
    print("=" * 60)
    print("GITHUB TRENDS ANALYSIS")
    print("=" * 60)

    df = load_recent_snapshots(days=7)
    print(f"\nLoaded {len(df)} snapshot records")

    if len(df) == 0:
        print("No data found. Run the pipeline first: python pipeline.py")
        return

    lang_stats = analyze_languages(df)
    top_movers = analyze_top_movers(df)
    topic_counts = analyze_topics(df)
    create_dashboard(df, lang_stats, top_movers, topic_counts)

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
