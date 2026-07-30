import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs")
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "netflix.csv")


def load_data():
    df = pd.read_csv(DATA_PATH)
    print("Original Shape:", df.shape)
    print("\nColumn Names:")
    print(df.columns.tolist())
    print("\nFirst 5 rows:")
    print(df.head())
    return df


def explore_data_quality(df):
    print("\n" + "=" * 50)
    print("DATA QUALITY ASSESSMENT")
    print("=" * 50)
    print("\nMissing Values:")
    print(df.isnull().sum())
    print(f"\nMissing Percentage:")
    print((df.isnull().sum() / len(df) * 100).round(2))
    print("\nDuplicate Rows:", df.duplicated().sum())
    print("\nData Types:")
    print(df.dtypes)


def clean_data(df):
    print("\n" + "=" * 50)
    print("DATA CLEANING PROCESS")
    print("=" * 50)
    df_clean = df.copy()

    print(f"\n1. Removing duplicates: {df_clean.duplicated().sum()} found")
    df_clean = df_clean.drop_duplicates()
    print(f"   Shape after: {df_clean.shape}")

    print(
        f"\n2. Handling missing 'director': {df_clean['director'].isnull().sum()} nulls"
    )
    df_clean["director"] = df_clean["director"].fillna("Unknown")

    print(f"\n3. Handling missing 'cast': {df_clean['cast'].isnull().sum()} nulls")
    df_clean["cast"] = df_clean["cast"].fillna("Unknown")

    print(
        f"\n4. Handling missing 'country': {df_clean['country'].isnull().sum()} nulls"
    )
    df_clean["country"] = df_clean["country"].fillna(df_clean["country"].mode()[0])

    print(
        f"\n5. Handling missing 'date_added': {df_clean['date_added'].isnull().sum()} nulls"
    )
    df_clean = df_clean.dropna(subset=["date_added"])

    df_clean["date_added"] = pd.to_datetime(df_clean["date_added"].str.strip())

    print(f"\n6. Standardizing 'rating': {df_clean['rating'].isnull().sum()} nulls")
    df_clean["rating"] = df_clean["rating"].fillna(df_clean["rating"].mode()[0])

    print(f"\n7. Creating 'duration_minutes' from duration...")
    df_clean["duration_minutes"] = df_clean["duration"].apply(
        lambda x: int(x.split()[0]) if pd.notna(x) and "min" in str(x) else np.nan
    )

    print(f"\n8. Extracting 'release_year' as integer...")
    df_clean["release_year"] = df_clean["release_year"].astype(int)

    print(f"\n9. Creating 'country_main' (first country listed)...")
    df_clean["country_main"] = df_clean["country"].apply(
        lambda x: x.split(",")[0].strip() if pd.notna(x) else "Unknown"
    )

    print(f"\n10. Adding 'is_movie' and 'is_tv_show' flags...")
    df_clean["is_movie"] = df_clean["type"] == "Movie"
    df_clean["is_tv_show"] = df_clean["type"] == "TV Show"

    print(f"\nFinal shape: {df_clean.shape}")
    print("\nMissing Values After Cleaning:")
    print(df_clean.isnull().sum())

    return df_clean


def analyze_cleaned_data(df):
    print("\n" + "=" * 50)
    print("ANALYSIS OF CLEANED DATA")
    print("=" * 50)

    print("\nContent Type Distribution:")
    print(df["type"].value_counts())

    print("\nTop 10 Countries by Content:")
    print(df["country_main"].value_counts().head(10))

    print("\nRating Distribution:")
    print(df["rating"].value_counts())

    print("\nMovies vs TV Shows by Release Year:")
    movies_by_year = df[df["is_movie"]].groupby("release_year").size()
    tv_by_year = df[df["is_tv_show"]].groupby("release_year").size()
    print(f"Movies: {len(movies_by_year)} years, TV Shows: {len(tv_by_year)} years")

    print("\nAverage Duration by Rating (Movies):")
    movie_durations = df[df["is_movie"]].groupby("rating")["duration_minutes"].mean()
    print(movie_durations.sort_values(ascending=False).round(2))


def create_visualizations(df):
    print("\n" + "=" * 50)
    print("CREATING VISUALIZATIONS")
    print("=" * 50)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    df["type"].value_counts().plot(
        kind="bar", ax=axes[0, 0], color=["coral", "steelblue"]
    )
    axes[0, 0].set_title("Content Type Distribution")
    axes[0, 0].set_xlabel("Type")
    axes[0, 0].set_ylabel("Count")
    axes[0, 0].tick_params(axis="x", rotation=0)

    df["country_main"].value_counts().head(10).plot(
        kind="barh", ax=axes[0, 1], color="green"
    )
    axes[0, 1].set_title("Top 10 Countries by Content")
    axes[0, 1].set_xlabel("Count")

    df[df["is_movie"]]["release_year"].hist(
        bins=30, ax=axes[1, 0], alpha=0.6, label="Movies", color="coral"
    )
    df[df["is_tv_show"]]["release_year"].hist(
        bins=30, ax=axes[1, 0], alpha=0.6, label="TV Shows", color="steelblue"
    )
    axes[1, 0].set_title("Content Added by Year")
    axes[1, 0].set_xlabel("Year")
    axes[1, 0].set_ylabel("Count")
    axes[1, 0].legend()

    df["rating"].value_counts().plot(
        kind="bar", ax=axes[1, 1], color="purple", alpha=0.7
    )
    axes[1, 1].set_title("Rating Distribution")
    axes[1, 1].set_xlabel("Rating")
    axes[1, 1].set_ylabel("Count")
    axes[1, 1].tick_params(axis="x", rotation=45)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_PATH, "netflix_analysis.png"), dpi=150)
    print(f"Saved: {OUTPUT_PATH}/netflix_analysis.png")
    plt.close()


def save_cleaned_data(df):
    output_file = os.path.join(os.path.dirname(DATA_PATH), "netflix_cleaned.csv")
    df.to_csv(output_file, index=False)
    print(f"\nCleaned data saved to: {output_file}")


def main():
    print("=" * 60)
    print("NETFLIX DATASET - CLEANING & ANALYSIS")
    print("=" * 60)

    os.makedirs(OUTPUT_PATH, exist_ok=True)

    df = load_data()
    explore_data_quality(df)
    df_clean = clean_data(df)
    analyze_cleaned_data(df_clean)
    create_visualizations(df_clean)
    save_cleaned_data(df_clean)

    print("\n" + "=" * 50)
    print("CLEANING COMPLETE!")
    print("=" * 50)


if __name__ == "__main__":
    main()
