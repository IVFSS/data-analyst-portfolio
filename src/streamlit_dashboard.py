import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

st.set_page_config(
    page_title="Pharma Sales Analytics",
    page_icon="",
    layout="wide",
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "pharma_sales.csv")


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    return df


df = load_data()

st.title("Pharmaceutical Sales Analytics Dashboard")
st.markdown("**Interactive dashboard for pharma sales data analysis**")

st.sidebar.header("Filters")
selected_products = st.sidebar.multiselect(
    "Select Products",
    options=sorted(df["product_name"].unique()),
    default=sorted(df["product_name"].unique()),
)

selected_regions = st.sidebar.multiselect(
    "Select Regions",
    options=sorted(df["region"].unique()),
    default=sorted(df["region"].unique()),
)

selected_stores = st.sidebar.multiselect(
    "Select Stores",
    options=sorted(df["store_id"].unique()),
    default=sorted(df["store_id"].unique()),
)

date_range = st.sidebar.date_input(
    "Date Range",
    value=(df["date"].min(), df["date"].max()),
    min_value=df["date"].min(),
    max_value=df["date"].max(),
)

filtered_df = df[
    (df["product_name"].isin(selected_products))
    & (df["region"].isin(selected_regions))
    & (df["store_id"].isin(selected_stores))
    & (df["date"] >= pd.Timestamp(date_range[0]))
    & (df["date"] <= pd.Timestamp(date_range[1]))
]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Revenue", f"${filtered_df['revenue'].sum():,.0f}")
with col2:
    st.metric("Units Sold", f"{filtered_df['units_sold'].sum():,}")
with col3:
    st.metric("Avg Daily Revenue", f"${filtered_df['revenue'].mean():,.0f}")
with col4:
    st.metric("Records", f"{len(filtered_df):,}")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["Trends", "Products", "Regions", "Comparison"])

with tab1:
    st.subheader("Revenue Over Time")
    daily = filtered_df.groupby("date")["revenue"].sum().reset_index()
    fig = px.line(daily, x="date", y="revenue", title="Daily Revenue")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Monthly Revenue Trend")
    filtered_df["month"] = filtered_df["date"].dt.to_period("M").astype(str)
    monthly = filtered_df.groupby("month")["revenue"].sum().reset_index()
    fig = px.bar(monthly, x="month", y="revenue", title="Monthly Revenue")
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Revenue by Product")
        prod_revenue = (
            filtered_df.groupby("product_name")["revenue"].sum().reset_index()
        )
        fig = px.bar(
            prod_revenue.sort_values("revenue"),
            x="revenue",
            y="product_name",
            orientation="h",
            title="Total Revenue by Product",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Units Sold by Product")
        prod_units = (
            filtered_df.groupby("product_name")["units_sold"].sum().reset_index()
        )
        fig = px.pie(
            prod_units,
            values="units_sold",
            names="product_name",
            title="Units Sold Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Product Performance Heatmap")
    filtered_df["day_of_week"] = filtered_df["date"].dt.day_name()
    filtered_df["hour_bucket"] = pd.cut(
        filtered_df["date"].dt.hour
        if "hour" in filtered_df.columns
        else pd.Series([12] * len(filtered_df)),
        bins=4,
        labels=["Q1", "Q2", "Q3", "Q4"],
    )
    dow_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    heatmap_data = (
        filtered_df.groupby(["product_name", "day_of_week"])["revenue"]
        .mean()
        .reset_index()
    )
    heatmap_pivot = heatmap_data.pivot(
        index="product_name", columns="day_of_week", values="revenue"
    )
    heatmap_pivot = heatmap_pivot.reindex(columns=dow_order)
    fig = px.imshow(
        heatmap_pivot.values,
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        color_continuous_scale="Viridis",
        title="Average Revenue: Product vs Day of Week",
    )
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Revenue by Region")
        region_revenue = filtered_df.groupby("region")["revenue"].sum().reset_index()
        fig = px.bar(
            region_revenue.sort_values("revenue", ascending=False),
            x="region",
            y="revenue",
            title="Total Revenue by Region",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Region vs Product")
        region_product = (
            filtered_df.groupby(["region", "product_name"])["revenue"]
            .sum()
            .reset_index()
        )
        fig = px.bar(
            region_product,
            x="region",
            y="revenue",
            color="product_name",
            title="Revenue Breakdown by Region",
            barmode="stack",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Store Performance")
    store_stats = (
        filtered_df.groupby("store_id")
        .agg(
            total_revenue=("revenue", "sum"),
            total_units=("units_sold", "sum"),
            avg_revenue=("revenue", "mean"),
        )
        .reset_index()
    )
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=store_stats["store_id"],
            y=store_stats["total_revenue"],
            name="Total Revenue",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=store_stats["store_id"],
            y=store_stats["avg_revenue"],
            mode="lines+markers",
            name="Avg Daily Revenue",
            yaxis="y2",
        )
    )
    fig.update_layout(
        title="Store Performance Overview",
        yaxis=dict(title="Total Revenue"),
        yaxis2=dict(title="Avg Daily Revenue", overlaying="y", side="right"),
    )
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Promotion Impact Analysis")
    promo_impact = (
        filtered_df.groupby("promotion")
        .agg(
            avg_revenue=("revenue", "mean"),
            avg_units=("units_sold", "mean"),
            total_revenue=("revenue", "sum"),
        )
        .reset_index()
    )
    promo_impact["promotion_label"] = promo_impact["promotion"].map(
        {True: "With Promotion", False: "No Promotion"}
    )

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            promo_impact,
            x="promotion_label",
            y="avg_revenue",
            title="Average Revenue: Promotion vs No Promotion",
            color="promotion_label",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            promo_impact,
            x="promotion_label",
            y="avg_units",
            title="Average Units Sold: Promotion vs No Promotion",
            color="promotion_label",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Correlation Analysis")
    numeric_cols = ["units_sold", "revenue", "stock_level", "promotion"]
    corr = filtered_df[numeric_cols].corr()
    fig = px.imshow(
        corr.values,
        x=corr.columns,
        y=corr.columns,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        title="Correlation Matrix",
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown(
    "**Data Source:** Synthetic pharmaceutical sales data | **Tools:** Python, Pandas, Plotly, Streamlit"
)
