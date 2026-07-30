import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta
import random
import matplotlib.pyplot as plt

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs")


def create_sample_database():
    db_path = os.path.join(DATA_PATH, "sales_data.db")

    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            city TEXT NOT NULL,
            join_date DATE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product_id INTEGER,
            quantity INTEGER NOT NULL,
            order_date DATE NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)

    products = [
        ("Laptop", "Electronics", 999.99),
        ("Mouse", "Electronics", 29.99),
        ("Keyboard", "Electronics", 79.99),
        ("Monitor", "Electronics", 299.99),
        ("Headphones", "Electronics", 149.99),
        ("Desk Chair", "Furniture", 249.99),
        ("Desk", "Furniture", 399.99),
        ("Lamp", "Furniture", 49.99),
        ("Notebook", "Stationery", 4.99),
        ("Pen Set", "Stationery", 12.99),
    ]
    cursor.executemany("INSERT INTO products VALUES (NULL, ?, ?, ?)", products)

    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
    customers = []
    for i in range(1, 21):
        name = f"Customer {i}"
        email = f"customer{i}@example.com"
        city = random.choice(cities)
        join_date = (datetime.now() - timedelta(days=random.randint(30, 365))).strftime(
            "%Y-%m-%d"
        )
        customers.append((name, email, city, join_date))
    cursor.executemany("INSERT INTO customers VALUES (NULL, ?, ?, ?, ?)", customers)

    orders = []
    for i in range(1, 101):
        customer_id = random.randint(1, 20)
        product_id = random.randint(1, 10)
        quantity = random.randint(1, 5)
        order_date = (datetime.now() - timedelta(days=random.randint(0, 180))).strftime(
            "%Y-%m-%d"
        )
        orders.append((customer_id, product_id, quantity, order_date))
    cursor.executemany("INSERT INTO orders VALUES (NULL, ?, ?, ?, ?)", orders)

    conn.commit()
    conn.close()
    print(f"Created database: {db_path}")
    return db_path


def query_database(db_path):
    conn = sqlite3.connect(db_path)

    print("\n" + "=" * 50)
    print("SQL QUERIES")
    print("=" * 50)

    print("\n1. Total Revenue by Product:")
    query1 = """
        SELECT p.product_name, SUM(o.quantity * p.price) as total_revenue
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        GROUP BY p.product_name
        ORDER BY total_revenue DESC
    """
    result1 = pd.read_sql_query(query1, conn)
    print(result1.to_string(index=False))

    print("\n2. Customer Order Summary:")
    query2 = """
        SELECT c.customer_name, c.city, COUNT(o.order_id) as total_orders, 
               SUM(o.quantity * p.price) as total_spent
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN products p ON o.product_id = p.product_id
        GROUP BY c.customer_id
        ORDER BY total_spent DESC
        LIMIT 10
    """
    result2 = pd.read_sql_query(query2, conn)
    print(result2.to_string(index=False))

    print("\n3. Sales by Category:")
    query3 = """
        SELECT p.category, COUNT(o.order_id) as total_orders, 
               SUM(o.quantity) as total_items,
               SUM(o.quantity * p.price) as total_revenue
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        GROUP BY p.category
    """
    result3 = pd.read_sql_query(query3, conn)
    print(result3.to_string(index=False))

    print("\n4. Monthly Sales Trend:")
    query4 = """
        SELECT strftime('%Y-%m', o.order_date) as month,
               COUNT(DISTINCT o.order_id) as orders,
               SUM(o.quantity * p.price) as revenue
        FROM orders o
        JOIN products p ON o.product_id = p.product_id
        GROUP BY month
        ORDER BY month
    """
    result4 = pd.read_sql_query(query4, conn)
    print(result4.to_string(index=False))

    print("\n5. Top Customers by City:")
    query5 = """
        SELECT c.city, COUNT(DISTINCT c.customer_id) as customers,
               SUM(o.quantity * p.price) as total_revenue
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN products p ON o.product_id = p.product_id
        GROUP BY c.city
        ORDER BY total_revenue DESC
    """
    result5 = pd.read_sql_query(query5, conn)
    print(result5.to_string(index=False))

    conn.close()
    return result1, result2, result3, result4, result5


def create_visualizations(results):
    result1, result2, result3, result4, result5 = results

    os.makedirs(OUTPUT_PATH, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    axes[0, 0].barh(
        result1["product_name"], result1["total_revenue"], color="steelblue"
    )
    axes[0, 0].set_title("Revenue by Product")
    axes[0, 0].set_xlabel("Revenue ($)")

    axes[0, 1].bar(result3["category"], result3["total_revenue"], color="coral")
    axes[0, 1].set_title("Revenue by Category")
    axes[0, 1].set_xlabel("Category")
    axes[0, 1].set_ylabel("Revenue ($)")
    axes[0, 1].tick_params(axis="x", rotation=45)

    axes[1, 0].plot(
        result4["month"], result4["revenue"], marker="o", linewidth=2, color="green"
    )
    axes[1, 0].set_title("Monthly Revenue Trend")
    axes[1, 0].set_xlabel("Month")
    axes[1, 0].set_ylabel("Revenue ($)")
    axes[1, 0].tick_params(axis="x", rotation=45)

    axes[1, 1].bar(result5["city"], result5["total_revenue"], color="purple", alpha=0.7)
    axes[1, 1].set_title("Revenue by City")
    axes[1, 1].set_xlabel("City")
    axes[1, 1].set_ylabel("Revenue ($)")
    axes[1, 1].tick_params(axis="x", rotation=45)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_PATH, "sql_analysis.png"), dpi=150)
    print(f"\nSaved visualization: {OUTPUT_PATH}/sql_analysis.png")
    plt.close()


def main():
    print("=" * 60)
    print("SQL & PYTHON - SALES DATABASE ANALYSIS")
    print("=" * 60)

    db_path = create_sample_database()
    results = query_database(db_path)
    create_visualizations(results)

    print("\n" + "=" * 50)
    print("ANALYSIS COMPLETE!")
    print("=" * 50)


if __name__ == "__main__":
    main()
