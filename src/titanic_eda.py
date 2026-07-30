import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set(style="whitegrid")

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "titanic.csv")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs")


def load_data():
    df = pd.read_csv(DATA_PATH)
    print("Dataset Shape:", df.shape)
    print("\nFirst 5 rows:")
    print(df.head())
    return df


def explore_data(df):
    print("\n" + "=" * 50)
    print("DATA EXPLORATION")
    print("=" * 50)
    print("\nColumn Info:")
    print(df.dtypes)
    print("\nMissing Values:")
    print(df.isnull().sum())
    print("\nBasic Statistics:")
    print(df.describe())


def clean_data(df):
    print("\n" + "=" * 50)
    print("DATA CLEANING")
    print("=" * 50)
    df_clean = df.copy()

    print(f"Original missing values:\n{df_clean.isnull().sum()}\n")

    df_clean["Age"] = df_clean["Age"].fillna(df_clean["Age"].median())
    df_clean["Embarked"] = df_clean["Embarked"].fillna(df_clean["Embarked"].mode()[0])
    df_clean.drop(columns=["Cabin"], inplace=True)

    print(f"After cleaning:\n{df_clean.isnull().sum()}")
    return df_clean


def survival_analysis(df):
    print("\n" + "=" * 50)
    print("SURVIVAL ANALYSIS")
    print("=" * 50)

    overall_survival = df["Survived"].mean() * 100
    print(f"\nOverall Survival Rate: {overall_survival:.2f}%")

    survival_by_sex = df.groupby("Sex")["Survived"].mean() * 100
    print(f"\nSurvival Rate by Sex:\n{survival_by_sex}")

    survival_by_class = df.groupby("Pclass")["Survived"].mean() * 100
    print(f"\nSurvival Rate by Class:\n{survival_by_class}")

    return df


def create_visualizations(df):
    print("\n" + "=" * 50)
    print("CREATING VISUALIZATIONS")
    print("=" * 50)

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    df["Survived"].value_counts().plot(
        kind="bar", ax=axes[0, 0], color=["#e74c3c", "#2ecc71"]
    )
    axes[0, 0].set_title("Survival Distribution")
    axes[0, 0].set_xlabel("Survived")
    axes[0, 0].set_ylabel("Count")

    pd.crosstab(df["Sex"], df["Survived"]).plot(
        kind="bar", ax=axes[0, 1], color=["#e74c3c", "#2ecc71"]
    )
    axes[0, 1].set_title("Survival by Sex")
    axes[0, 1].set_xlabel("Sex")
    axes[0, 1].tick_params(axis="x", rotation=0)

    pd.crosstab(df["Pclass"], df["Survived"]).plot(
        kind="bar", ax=axes[1, 0], color=["#e74c3c", "#2ecc71"]
    )
    axes[1, 0].set_title("Survival by Passenger Class")
    axes[1, 0].set_xlabel("Pclass")
    axes[1, 0].tick_params(axis="x", rotation=0)

    df.groupby("Sex")["Age"].hist(alpha=0.6, ax=axes[1, 1])
    axes[1, 1].set_title("Age Distribution by Sex")
    axes[1, 1].set_xlabel("Age")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_PATH, "titanic_analysis.png"), dpi=150)
    print(f"Saved visualization to {OUTPUT_PATH}/titanic_analysis.png")
    plt.close()

    plt.figure(figsize=(10, 6))
    sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="coolwarm", center=0)
    plt.title("Correlation Heatmap")
    plt.savefig(os.path.join(OUTPUT_PATH, "correlation_heatmap.png"), dpi=150)
    print(f"Saved correlation heatmap to {OUTPUT_PATH}/correlation_heatmap.png")
    plt.close()


def main():
    print("=" * 60)
    print("TITANIC DATASET EXPLORATORY DATA ANALYSIS")
    print("=" * 60)

    os.makedirs(OUTPUT_PATH, exist_ok=True)

    df = load_data()
    explore_data(df)
    df_clean = clean_data(df)
    df_clean = survival_analysis(df_clean)
    create_visualizations(df_clean)

    print("\n" + "=" * 50)
    print("ANALYSIS COMPLETE!")
    print("=" * 50)


if __name__ == "__main__":
    main()
