import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_curve,
    auc,
)
import os

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs")
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "amazon_reviews.csv")

sns.set(style="whitegrid")


def load_and_prepare():
    df = pd.read_csv(DATA_PATH)
    df["text"] = (df["title"].fillna("") + " " + df["content"].fillna("")).str.strip()
    print(f"Loaded {len(df)} reviews")
    print(f"Label distribution:\n{df['label'].value_counts()}")
    return df


def vectorize_text(X_train, X_test):
    vectorizer = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True,
        stop_words="english",
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    print(f"TF-IDF features: {X_train_tfidf.shape[1]:,}")
    return X_train_tfidf, X_test_tfidf, vectorizer


def train_models(X_train, X_test, y_train, y_test):
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Naive Bayes": MultinomialNB(),
        "Linear SVC": LinearSVC(random_state=42, max_iter=2000),
        "Random Forest": RandomForestClassifier(
            n_estimators=100, random_state=42, n_jobs=-1
        ),
    }

    results = {}
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        if hasattr(model, "predict_proba"):
            y_proba = model.predict_proba(X_test)[:, 1]
        else:
            decision = model.decision_function(X_test)
            y_proba = 1 / (1 + np.exp(-decision))

        accuracy = accuracy_score(y_test, y_pred)
        cv_scores = cross_val_score(model, X_train, y_train, cv=3, scoring="accuracy")

        results[name] = {
            "model": model,
            "y_pred": y_pred,
            "y_proba": y_proba,
            "accuracy": accuracy,
            "cv_mean": cv_scores.mean(),
            "cv_std": cv_scores.std(),
        }

        print(
            f"  Accuracy: {accuracy:.4f}, CV: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})"
        )

    return results


def evaluate_models(results, y_test):
    print("\n" + "=" * 60)
    print("DETAILED EVALUATION")
    print("=" * 60)

    comparison = []
    for name, res in results.items():
        print(f"\n{name}:")
        print(
            classification_report(
                y_test, res["y_pred"], target_names=["Negative", "Positive"]
            )
        )
        comparison.append(
            {
                "Model": name,
                "Accuracy": res["accuracy"],
                "CV Mean": res["cv_mean"],
                "CV Std": res["cv_std"],
            }
        )

    return pd.DataFrame(comparison)


def feature_importance(vectorizer, models):
    print("\n" + "=" * 60)
    print("TOP FEATURES (Logistic Regression)")
    print("=" * 60)

    lr = models["Logistic Regression"]["model"]
    feature_names = vectorizer.get_feature_names_out()
    coef = lr.coef_[0]

    top_pos = np.argsort(coef)[-20:][::-1]
    top_neg = np.argsort(coef)[:20]

    print("\nTop 20 Positive Indicators:")
    for idx in top_pos:
        print(f"  {feature_names[idx]}: {coef[idx]:.3f}")

    print("\nTop 20 Negative Indicators:")
    for idx in top_neg:
        print(f"  {feature_names[idx]}: {coef[idx]:.3f}")

    return top_pos, top_neg, feature_names


def plot_results(results, comparison_df, top_pos, top_neg, feature_names, y_test):
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    axes[0, 0].bar(comparison_df["Model"], comparison_df["Accuracy"], color="steelblue")
    axes[0, 0].set_title("Model Accuracy Comparison")
    axes[0, 0].set_ylabel("Accuracy")
    axes[0, 0].set_ylim(0.7, 1.0)
    axes[0, 0].tick_params(axis="x", rotation=20)

    pos_features = [feature_names[i] for i in top_pos[:15]]
    pos_scores = [
        results["Logistic Regression"]["model"].coef_[0][i] for i in top_pos[:15]
    ]
    axes[0, 1].barh(pos_features, pos_scores, color="steelblue")
    axes[0, 1].set_title("Top Positive Features")
    axes[0, 1].set_xlabel("Coefficient")

    best_model_name = comparison_df.loc[comparison_df["Accuracy"].idxmax(), "Model"]
    best = results[best_model_name]
    cm = confusion_matrix(y_test, best["y_pred"])
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        ax=axes[1, 0],
        xticklabels=["Negative", "Positive"],
        yticklabels=["Negative", "Positive"],
    )
    axes[1, 0].set_title(f"Confusion Matrix ({best_model_name})")
    axes[1, 0].set_xlabel("Predicted")
    axes[1, 0].set_ylabel("Actual")

    for name, res in results.items():
        fpr, tpr, _ = roc_curve(y_test, res["y_proba"])
        roc_auc = auc(fpr, tpr)
        axes[1, 1].plot(fpr, tpr, linewidth=2, label=f"{name} (AUC={roc_auc:.3f})")
    axes[1, 1].plot([0, 1], [0, 1], "k--", alpha=0.5)
    axes[1, 1].set_title("ROC Curves")
    axes[1, 1].set_xlabel("False Positive Rate")
    axes[1, 1].set_ylabel("True Positive Rate")
    axes[1, 1].legend(loc="lower right")
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_PATH, "amazon_ml_results.png"), dpi=150)
    print(f"\nSaved: {OUTPUT_PATH}/amazon_ml_results.png")
    plt.close()


def main():
    print("=" * 60)
    print("AMAZON REVIEWS - ML SENTIMENT CLASSIFIER")
    print("=" * 60)

    df = load_and_prepare()
    X = df["text"]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\nTrain: {len(X_train)}, Test: {len(X_test)}")

    X_train_tfidf, X_test_tfidf, vectorizer = vectorize_text(X_train, X_test)

    results = train_models(X_train_tfidf, X_test_tfidf, y_train, y_test)
    comparison_df = evaluate_models(results, y_test)
    top_pos, top_neg, feature_names = feature_importance(vectorizer, results)
    plot_results(results, comparison_df, top_pos, top_neg, feature_names, y_test)

    print("\n" + "=" * 60)
    print("MODEL COMPARISON SUMMARY")
    print("=" * 60)
    print(comparison_df.to_string(index=False))
    print("\n" + "=" * 60)
    print("ML ANALYSIS COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
