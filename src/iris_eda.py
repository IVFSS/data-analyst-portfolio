import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import load_iris
import os

sns.set(style="whitegrid")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs")


def load_iris_data():
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df["species"] = pd.Categorical.from_codes(iris.target, iris.target_names)
    print("Dataset Shape:", df.shape)
    print("\nFirst 5 rows:")
    print(df.head())
    return df


def explore_data(df):
    print("\n" + "=" * 50)
    print("DATA EXPLORATION")
    print("=" * 50)
    print("\nColumn Types:")
    print(df.dtypes)
    print("\nMissing Values:")
    print(df.isnull().sum())
    print("\nBasic Statistics:")
    print(df.describe())
    print("\nSpecies Distribution:")
    print(df["species"].value_counts())


def analyze_species(df):
    print("\n" + "=" * 50)
    print("SPECIES ANALYSIS")
    print("=" * 50)

    numeric_cols = df.columns[:-1]
    species_stats = df.groupby("species")[numeric_cols].agg(
        ["mean", "std", "min", "max"]
    )
    print("\nSpecies Statistics:")
    print(species_stats)

    print("\nMean Sepal Length by Species:")
    print(df.groupby("species")["sepal length (cm)"].mean())

    print("\nMean Petal Width by Species:")
    print(df.groupby("species")["petal width (cm)"].mean())


def create_visualizations(df):
    print("\n" + "=" * 50)
    print("CREATING VISUALIZATIONS")
    print("=" * 50)

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    for i, species in enumerate(df["species"].unique()):
        subset = df[df["species"] == species]
        axes[0, 0].scatter(
            subset["sepal length (cm)"],
            subset["sepal width (cm)"],
            label=species,
            alpha=0.7,
            s=50,
        )
    axes[0, 0].set_title("Sepal Length vs Width by Species")
    axes[0, 0].set_xlabel("Sepal Length (cm)")
    axes[0, 0].set_ylabel("Sepal Width (cm)")
    axes[0, 0].legend()

    for i, species in enumerate(df["species"].unique()):
        subset = df[df["species"] == species]
        axes[0, 1].scatter(
            subset["petal length (cm)"],
            subset["petal width (cm)"],
            label=species,
            alpha=0.7,
            s=50,
        )
    axes[0, 1].set_title("Petal Length vs Width by Species")
    axes[0, 1].set_xlabel("Petal Length (cm)")
    axes[0, 1].set_ylabel("Petal Width (cm)")
    axes[0, 1].legend()

    df.boxplot(column="sepal length (cm)", by="species", ax=axes[0, 2])
    axes[0, 2].set_title("Sepal Length by Species")
    axes[0, 2].set_xlabel("Species")
    axes[0, 2].set_ylabel("Sepal Length (cm)")
    plt.suptitle("")

    df.boxplot(column="petal length (cm)", by="species", ax=axes[1, 0])
    axes[1, 0].set_title("Petal Length by Species")
    axes[1, 0].set_xlabel("Species")
    axes[1, 0].set_ylabel("Petal Length (cm)")
    plt.suptitle("")

    df.hist(
        column="sepal length (cm)",
        by="species",
        ax=axes[1, 1],
        bins=15,
        edgecolor="black",
    )

    corr_matrix = df.drop(columns=["species"]).corr()
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", ax=axes[1, 2], fmt=".2f")
    axes[1, 2].set_title("Feature Correlation Matrix")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_PATH, "iris_analysis.png"), dpi=150)
    print(f"Saved: {OUTPUT_PATH}/iris_analysis.png")
    plt.close()

    fig, ax = plt.subplots(figsize=(10, 8))
    pd.plotting.parallel_coordinates(df, "species", colormap="viridis", ax=ax)
    ax.set_title("Parallel Coordinates Plot - Iris Species")
    ax.set_xlabel("Features")
    ax.set_ylabel("Value (cm)")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_PATH, "iris_parallel_coordinates.png"), dpi=150)
    print(f"Saved: {OUTPUT_PATH}/iris_parallel_coordinates.png")
    plt.close()


def main():
    print("=" * 60)
    print("IRIS DATASET EXPLORATORY DATA ANALYSIS")
    print("=" * 60)

    os.makedirs(OUTPUT_PATH, exist_ok=True)

    df = load_iris_data()
    explore_data(df)
    analyze_species(df)
    create_visualizations(df)

    print("\n" + "=" * 50)
    print("ANALYSIS COMPLETE!")
    print("=" * 50)


if __name__ == "__main__":
    main()
