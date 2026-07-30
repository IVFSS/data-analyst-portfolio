import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
import os

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs")
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "amazon_reviews.csv")

sns.set(style="whitegrid")


def load_data():
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} reviews")
    print(f"Columns: {df.columns.tolist()}")
    print(f"\nLabel distribution:\n{df['label'].value_counts()}")
    print(f"\nSample review:")
    print(df.iloc[0]["content"][:200])
    return df


def vader_sentiment(text):
    positive_words = {
        "love",
        "great",
        "excellent",
        "amazing",
        "perfect",
        "best",
        "wonderful",
        "fantastic",
        "awesome",
        "good",
        "nice",
        "happy",
        "recommend",
        "beautiful",
        "impressive",
        "outstanding",
        "superb",
        "brilliant",
        "enjoy",
        "enjoyed",
        "favorite",
        "incredible",
        "satisfying",
        "comfortable",
        "durable",
        "quality",
    }
    negative_words = {
        "hate",
        "terrible",
        "awful",
        "worst",
        "bad",
        "poor",
        "disappointing",
        "broken",
        "useless",
        "waste",
        "horrible",
        "annoying",
        "frustrating",
        "defective",
        "failed",
        "cheap",
        "uncomfortable",
        "difficult",
        "sucks",
        "garbage",
        "disappointed",
        "regret",
        "avoid",
        "misleading",
        "wrong",
    }

    words = re.findall(r"\b[a-z]+\b", text.lower())
    pos_count = sum(1 for w in words if w in positive_words)
    neg_count = sum(1 for w in words if w in negative_words)

    if pos_count + neg_count == 0:
        return "neutral", 0.0
    elif pos_count > neg_count:
        score = pos_count / (pos_count + neg_count)
        return "positive", score
    else:
        score = -neg_count / (pos_count + neg_count)
        return "negative", score


def apply_vader(df):
    print("\n" + "=" * 60)
    print("APPLYING RULE-BASED SENTIMENT (lexicon-based)")
    print("=" * 60)

    sentiments = df["content"].apply(vader_sentiment)
    df["vader_sentiment"] = sentiments.apply(lambda x: x[0])
    df["vader_score"] = sentiments.apply(lambda x: x[1])

    print(f"\nSentiment distribution:\n{df['vader_sentiment'].value_counts()}")
    return df


def analyze_accuracy(df):
    print("\n" + "=" * 60)
    print("SENTIMENT vs ACTUAL LABEL ACCURACY")
    print("=" * 60)

    df["vader_predicted"] = df["vader_sentiment"].map({"positive": 1, "negative": 0})

    correct = (df["vader_predicted"] == df["label"]).sum()
    total = len(df)
    accuracy = correct / total * 100
    print(f"\nAccuracy: {accuracy:.2f}%")

    confusion = pd.crosstab(
        df["label"], df["vader_predicted"], rownames=["Actual"], colnames=["Predicted"]
    )
    print(f"\nConfusion Matrix:")
    print(confusion)

    return accuracy


def word_frequency_analysis(df, top_n=20):
    print("\n" + "=" * 60)
    print("WORD FREQUENCY ANALYSIS")
    print("=" * 60)

    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "as",
        "is",
        "was",
        "were",
        "are",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "shall",
        "can",
        "this",
        "that",
        "these",
        "those",
        "i",
        "you",
        "he",
        "she",
        "it",
        "we",
        "they",
        "them",
        "their",
        "there",
        "here",
        "what",
        "which",
        "who",
        "when",
        "where",
        "why",
        "how",
        "all",
        "any",
        "both",
        "each",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "nor",
        "not",
        "only",
        "own",
        "same",
        "so",
        "than",
        "too",
        "very",
        "s",
        "t",
        "just",
    }

    positive_words = []
    negative_words = []

    for _, row in df.iterrows():
        words = re.findall(r"\b[a-z]+\b", row["content"].lower())
        words = [w for w in words if len(w) > 3 and w not in stop_words]

        if row["label"] == 1:
            positive_words.extend(words)
        else:
            negative_words.extend(words)

    pos_freq = Counter(positive_words).most_common(top_n)
    neg_freq = Counter(negative_words).most_common(top_n)

    print(f"\nTop {top_n} words in POSITIVE reviews:")
    for word, count in pos_freq:
        print(f"  {word}: {count}")

    print(f"\nTop {top_n} words in NEGATIVE reviews:")
    for word, count in neg_freq:
        print(f"  {word}: {count}")

    return pos_freq, neg_freq


def analyze_text_features(df):
    print("\n" + "=" * 60)
    print("TEXT FEATURES")
    print("=" * 60)

    df["content_length"] = df["content"].str.len()
    df["word_count"] = df["content"].str.split().str.len()
    df["title_length"] = df["title"].fillna("").str.len()
    df["has_title"] = df["title"].notna()

    print("\nReview length by sentiment:")
    length_stats = (
        df.groupby("label")
        .agg(
            avg_chars=("content_length", "mean"),
            avg_words=("word_count", "mean"),
            median_words=("word_count", "median"),
        )
        .round(2)
    )
    print(length_stats)

    print(f"\nReviews with title: {df['has_title'].sum()} / {len(df)}")
    return df


def create_visualizations(df, pos_freq, neg_freq):
    print("\n" + "=" * 60)
    print("CREATING VISUALIZATIONS")
    print("=" * 60)
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    label_counts = df["label"].value_counts()
    axes[0, 0].bar(
        ["Negative", "Positive"], label_counts.values, color=["coral", "steelblue"]
    )
    axes[0, 0].set_title("Label Distribution")
    axes[0, 0].set_ylabel("Count")

    sentiment_counts = df["vader_sentiment"].value_counts()
    axes[0, 1].bar(
        sentiment_counts.index,
        sentiment_counts.values,
        color=["coral", "gray", "steelblue"],
    )
    axes[0, 1].set_title("Predicted Sentiment Distribution")
    axes[0, 1].set_ylabel("Count")

    pos_words, pos_counts = zip(*pos_freq[:15])
    axes[1, 0].barh(pos_words, pos_counts, color="steelblue")
    axes[1, 0].set_title("Top Words in Positive Reviews")
    axes[1, 0].set_xlabel("Count")

    neg_words, neg_counts = zip(*neg_freq[:15])
    axes[1, 1].barh(neg_words, neg_counts, color="coral")
    axes[1, 1].set_title("Top Words in Negative Reviews")
    axes[1, 1].set_xlabel("Count")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_PATH, "amazon_sentiment_analysis.png"), dpi=150)
    print(f"Saved: {OUTPUT_PATH}/amazon_sentiment_analysis.png")
    plt.close()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for label, color, name in [(0, "coral", "Negative"), (1, "steelblue", "Positive")]:
        subset = df[df["label"] == label]["word_count"]
        axes[0].hist(subset, bins=30, alpha=0.6, color=color, label=name)
    axes[0].set_title("Word Count Distribution by Sentiment")
    axes[0].set_xlabel("Word Count")
    axes[0].set_ylabel("Frequency")
    axes[0].legend()
    axes[0].set_xlim(0, 200)

    axes[1].scatter(
        df["word_count"], df["vader_score"], alpha=0.3, c=df["label"], cmap="RdBu"
    )
    axes[1].set_title("Word Count vs Sentiment Score")
    axes[1].set_xlabel("Word Count")
    axes[1].set_ylabel("VADER Score")
    axes[1].axhline(y=0, color="r", linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_PATH, "amazon_text_features.png"), dpi=150)
    print(f"Saved: {OUTPUT_PATH}/amazon_text_features.png")
    plt.close()


def generate_insights(df, accuracy):
    print("\n" + "=" * 60)
    print("KEY INSIGHTS")
    print("=" * 60)

    total = len(df)
    positive_pct = (df["label"] == 1).sum() / total * 100
    negative_pct = (df["label"] == 0).sum() / total * 100
    avg_len_pos = df[df["label"] == 1]["word_count"].mean()
    avg_len_neg = df[df["label"] == 0]["word_count"].mean()

    print(f"\nDataset Overview:")
    print(f"  Total reviews analyzed: {total:,}")
    print(f"  Positive reviews: {positive_pct:.1f}%")
    print(f"  Negative reviews: {negative_pct:.1f}%")
    print(f"\nReview Length:")
    print(f"  Positive avg words: {avg_len_pos:.1f}")
    print(f"  Negative avg words: {avg_len_neg:.1f}")
    print(f"  Difference: {abs(avg_len_pos - avg_len_neg):.1f} words")
    print(f"\nModel Performance:")
    print(f"  Lexicon-based accuracy: {accuracy:.2f}%")


def main():
    print("=" * 60)
    print("AMAZON REVIEWS - SENTIMENT ANALYSIS")
    print("=" * 60)

    df = load_data()
    df = apply_vader(df)
    accuracy = analyze_accuracy(df)
    pos_freq, neg_freq = word_frequency_analysis(df)
    df = analyze_text_features(df)
    create_visualizations(df, pos_freq, neg_freq)
    generate_insights(df, accuracy)

    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
