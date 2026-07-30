import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_curve,
    auc,
)
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set(style="whitegrid")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs")
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "titanic.csv")


def load_and_prepare():
    df = pd.read_csv(DATA_PATH)

    df["Age"] = df["Age"].fillna(df["Age"].median())
    df["Embarked"] = df["Embarked"].fillna(df["Embarked"].mode()[0])
    df["Fare"] = df["Fare"].fillna(df["Fare"].median())

    df["Sex_encoded"] = (df["Sex"] == "female").astype(int)
    df["Embarked_encoded"] = df["Embarked"].map({"S": 0, "C": 1, "Q": 2})

    df["FamilySize"] = df["SibSp"] + df["Parch"] + 1
    df["IsAlone"] = (df["FamilySize"] == 1).astype(int)

    df["Title"] = df["Name"].str.extract(r" ([A-Za-z]+)\.", expand=False)
    title_mapping = {
        "Mr": "Mr",
        "Miss": "Miss",
        "Mrs": "Mrs",
        "Master": "Master",
        "Dr": "Rare",
        "Rev": "Rare",
        "Col": "Rare",
        "Major": "Rare",
        "Mlle": "Miss",
        "Countess": "Rare",
        "Ms": "Miss",
        "Lady": "Rare",
        "Jonkheer": "Rare",
        "Don": "Rare",
        "Dona": "Rare",
        "Mme": "Mrs",
        "Capt": "Rare",
        "Sir": "Rare",
    }
    df["Title"] = df["Title"].map(title_mapping)
    df["Title"] = df["Title"].fillna("Rare")
    df["Title_encoded"] = df["Title"].map(
        {"Mr": 0, "Miss": 1, "Mrs": 2, "Master": 3, "Rare": 4}
    )

    feature_cols = [
        "Pclass",
        "Sex_encoded",
        "Age",
        "Fare",
        "Embarked_encoded",
        "FamilySize",
        "IsAlone",
        "Title_encoded",
    ]

    X = df[feature_cols]
    y = df["Survived"]

    return X, y, feature_cols, df


def train_models(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    models = {
        "Logistic Regression": LogisticRegression(random_state=42, max_iter=1000),
        "Decision Tree": DecisionTreeClassifier(random_state=42, max_depth=5),
        "Random Forest": RandomForestClassifier(
            random_state=42, n_estimators=100, max_depth=5
        ),
    }

    results = {}
    for name, model in models.items():
        if "Logistic" in name:
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]

        accuracy = accuracy_score(y_test, y_pred)
        cv_scores = cross_val_score(model, X_train, y_train, cv=5)

        results[name] = {
            "model": model,
            "y_test": y_test,
            "y_pred": y_pred,
            "y_pred_proba": y_pred_proba,
            "accuracy": accuracy,
            "cv_mean": cv_scores.mean(),
            "cv_std": cv_scores.std(),
            "scaler": scaler if "Logistic" in name else None,
        }

    return results


def evaluate_models(results):
    print("=" * 60)
    print("MODEL EVALUATION")
    print("=" * 60)

    comparison = []
    for name, res in results.items():
        print(f"\n{name}:")
        print(f"  Accuracy: {res['accuracy']:.4f}")
        print(f"  CV Score: {res['cv_mean']:.4f} (+/- {res['cv_std']:.4f})")
        print("\n  Classification Report:")
        print(
            classification_report(
                res["y_test"], res["y_pred"], target_names=["Died", "Survived"]
            )
        )
        comparison.append(
            {
                "Model": name,
                "Test Accuracy": res["accuracy"],
                "CV Mean": res["cv_mean"],
                "CV Std": res["cv_std"],
            }
        )

    print("\n" + "=" * 60)
    print("MODEL COMPARISON")
    print("=" * 60)
    print(pd.DataFrame(comparison).to_string(index=False))

    return pd.DataFrame(comparison)


def feature_importance(results, feature_cols):
    rf = results["Random Forest"]["model"]
    importances = rf.feature_importances_
    fi_df = pd.DataFrame(
        {
            "Feature": feature_cols,
            "Importance": importances,
        }
    ).sort_values("Importance", ascending=False)

    print("\n" + "=" * 60)
    print("FEATURE IMPORTANCE (Random Forest)")
    print("=" * 60)
    print(fi_df.to_string(index=False))

    return fi_df


def plot_results(results, comparison_df, fi_df):
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    axes[0, 0].bar(
        comparison_df["Model"], comparison_df["Test Accuracy"], color="steelblue"
    )
    axes[0, 0].set_title("Model Accuracy Comparison")
    axes[0, 0].set_ylabel("Accuracy")
    axes[0, 0].set_ylim(0.7, 0.9)
    axes[0, 0].tick_params(axis="x", rotation=20)

    axes[0, 1].barh(fi_df["Feature"], fi_df["Importance"], color="coral")
    axes[0, 1].set_title("Feature Importance (Random Forest)")
    axes[0, 1].set_xlabel("Importance")

    best_model = results["Random Forest"]
    cm = confusion_matrix(best_model["y_test"], best_model["y_pred"])
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        ax=axes[1, 0],
        xticklabels=["Died", "Survived"],
        yticklabels=["Died", "Survived"],
    )
    axes[1, 0].set_title("Confusion Matrix (Random Forest)")
    axes[1, 0].set_xlabel("Predicted")
    axes[1, 0].set_ylabel("Actual")

    for name, res in results.items():
        fpr, tpr, _ = roc_curve(res["y_test"], res["y_pred_proba"])
        roc_auc = auc(fpr, tpr)
        axes[1, 1].plot(fpr, tpr, linewidth=2, label=f"{name} (AUC = {roc_auc:.3f})")
    axes[1, 1].plot([0, 1], [0, 1], "k--", alpha=0.5)
    axes[1, 1].set_title("ROC Curves")
    axes[1, 1].set_xlabel("False Positive Rate")
    axes[1, 1].set_ylabel("True Positive Rate")
    axes[1, 1].legend(loc="lower right")
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_PATH, "titanic_ml_results.png"), dpi=150)
    print(f"\nSaved: {OUTPUT_PATH}/titanic_ml_results.png")
    plt.close()


def main():
    print("=" * 60)
    print("TITANIC SURVIVAL - PREDICTIVE MODELING")
    print("=" * 60)

    X, y, feature_cols, _ = load_and_prepare()
    print(f"\nFeatures used: {feature_cols}")
    print(f"Dataset shape: {X.shape}")

    results = train_models(X, y)
    comparison_df = evaluate_models(results)
    fi_df = feature_importance(results, feature_cols)
    plot_results(results, comparison_df, fi_df)

    print("\n" + "=" * 60)
    print("MODELING COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
