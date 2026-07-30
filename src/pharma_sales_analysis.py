import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set(style="whitegrid")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs")
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data")


def generate_pharma_data():
    np.random.seed(42)
    dates = pd.date_range("2023-01-01", "2024-12-31", freq="D")

    data = {
        "date": dates,
        "store_id": np.random.choice(
            ["S001", "S002", "S003", "S004", "S005"], len(dates)
        ),
        "product_name": np.random.choice(
            [
                "Aspirin",
                "Ibuprofen",
                "Paracetamol",
                "Vitamin C",
                "Vitamin D",
                "Omega-3",
                "Magnesium",
            ],
            len(dates),
        ),
        "units_sold": np.random.randint(10, 200, len(dates)),
        "revenue": np.random.uniform(50, 2000, len(dates)).round(2),
        "stock_level": np.random.randint(0, 500, len(dates)),
        "promotion": np.random.choice([True, False], len(dates), p=[0.2, 0.8]),
        "region": np.random.choice(["North", "South", "East", "West"], len(dates)),
    }

    df = pd.DataFrame(data)
    df["day_of_week"] = df["date"].dt.day_name()
    df["month"] = df["date"].dt.month
    df["quarter"] = df["date"].dt.quarter
    df["year"] = df["date"].dt.year

    return df


def load_or_generate_data():
    csv_path = os.path.join(DATA_PATH, "pharma_sales.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, parse_dates=["date"])
        print(f"Loaded data from {csv_path}")
    else:
        df = generate_pharma_data()
        df.to_csv(csv_path, index=False)
        print(f"Generated and saved data to {csv_path}")
    print(f"Dataset Shape: {df.shape}")
    print("\nFirst 5 rows:")
    print(df.head())
    return df


def explore_data(df):
    print("\n" + "=" * 50)
    print("DATA EXPLORATION")
    print("=" * 50)
    print("\nMissing Values:")
    print(df.isnull().sum())
    print("\nBasic Statistics:")
    print(df.describe())


def analyze_sales(df):
    print("\n" + "=" * 50)
    print("SALES ANALYSIS")
    print("=" * 50)

    print("\n1. Overall Metrics:")
    print(f"   Total Revenue: ${df['revenue'].sum():,.2f}")
    print(f"   Total Units Sold: {df['units_sold'].sum():,}")
    print(f"   Average Daily Revenue: ${df['revenue'].mean():,.2f}")

    print("\n2. Sales by Product:")
    product_sales = (
        df.groupby("product_name")
        .agg({"units_sold": "sum", "revenue": "sum"})
        .sort_values("revenue", ascending=False)
    )
    print(product_sales)

    print("\n3. Sales by Region:")
    region_sales = (
        df.groupby("region")
        .agg({"units_sold": "sum", "revenue": "sum"})
        .sort_values("revenue", ascending=False)
    )
    print(region_sales)

    print("\n4. Sales by Store:")
    store_sales = (
        df.groupby("store_id")
        .agg({"units_sold": "sum", "revenue": "sum"})
        .sort_values("revenue", ascending=False)
    )
    print(store_sales)

    print("\n5. Promotion Impact:")
    promo_impact = df.groupby("promotion")[["units_sold", "revenue"]].mean()
    print(promo_impact)

    print("\n6. Day of Week Analysis:")
    dow_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    dow_sales = df.groupby("day_of_week")[["units_sold", "revenue"]].mean()
    print(dow_sales.reindex(dow_order))

    print("\n7. Monthly Trend:")
    monthly = df.groupby([df["date"].dt.to_period("M")])["revenue"].sum()
    print(monthly)


def create_visualizations(df):
    print("\n" + "=" * 50)
    print("CREATING VISUALIZATIONS")
    print("=" * 50)

    fig, axes = plt.subplots(3, 2, figsize=(15, 12))

    product_revenue = (
        df.groupby("product_name")["revenue"].sum().sort_values(ascending=True)
    )
    product_revenue.plot(kind="barh", ax=axes[0, 0], color="steelblue")
    axes[0, 0].set_title("Revenue by Product")
    axes[0, 0].set_xlabel("Revenue ($)")

    region_revenue = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
    region_revenue.plot(kind="bar", ax=axes[0, 1], color="coral")
    axes[0, 1].set_title("Revenue by Region")
    axes[0, 1].set_xlabel("Region")
    axes[0, 1].set_ylabel("Revenue ($)")
    axes[0, 1].tick_params(axis="x", rotation=0)

    df.set_index("date")["revenue"].resample("W").sum().plot(
        ax=axes[1, 0], linewidth=1.5, color="green"
    )
    axes[1, 0].set_title("Weekly Revenue Trend")
    axes[1, 0].set_xlabel("Date")
    axes[1, 0].set_ylabel("Revenue ($)")

    dow_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    dow_revenue = df.groupby("day_of_week")["revenue"].mean().reindex(dow_order)
    dow_revenue.plot(kind="bar", ax=axes[1, 1], color="purple", alpha=0.7)
    axes[1, 1].set_title("Average Revenue by Day of Week")
    axes[1, 1].set_xlabel("Day of Week")
    axes[1, 1].set_ylabel("Average Revenue ($)")
    axes[1, 1].tick_params(axis="x", rotation=45)

    promo_data = df.groupby("promotion")["revenue"].mean()
    promo_data.plot(kind="bar", ax=axes[2, 0], color=["green", "orange"])
    axes[2, 0].set_title("Revenue: Promotion vs No Promotion")
    axes[2, 0].set_xlabel("Has Promotion")
    axes[2, 0].set_ylabel("Average Revenue ($)")
    axes[2, 0].tick_params(axis="x", rotation=0)

    df.boxplot(column="revenue", by="product_name", ax=axes[2, 1])
    axes[2, 1].set_title("Revenue Distribution by Product")
    axes[2, 1].set_xlabel("Product")
    axes[2, 1].set_ylabel("Revenue ($)")
    axes[2, 1].tick_params(axis="x", rotation=45)
    plt.suptitle("")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_PATH, "pharma_sales_analysis.png"), dpi=150)
    print(f"Saved: {OUTPUT_PATH}/pharma_sales_analysis.png")
    plt.close()

    plt.figure(figsize=(12, 8))
    monthly_pivot = df.pivot_table(
        values="revenue", index="month", columns="product_name", aggfunc="sum"
    )
    monthly_pivot.plot(kind="line", marker="o", linewidth=2)
    plt.title("Monthly Revenue by Product")
    plt.xlabel("Month")
    plt.ylabel("Revenue ($)")
    plt.legend(title="Product", bbox_to_anchor=(1.05, 1))
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_PATH, "pharma_monthly_trends.png"), dpi=150)
    print(f"Saved: {OUTPUT_PATH}/pharma_monthly_trends.png")
    plt.close()


def main():
    print("=" * 60)
    print("PHARMACEUTICAL SALES DATA ANALYSIS")
    print("=" * 60)

    os.makedirs(OUTPUT_PATH, exist_ok=True)

    df = load_or_generate_data()
    explore_data(df)
    analyze_sales(df)
    create_visualizations(df)

    print("\n" + "=" * 50)
    print("ANALYSIS COMPLETE!")
    print("=" * 50)


if __name__ == "__main__":
    main()
