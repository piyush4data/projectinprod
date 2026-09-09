"""
E-commerce Sales & Inventory Analytics Suite
ETL Pipeline: Extract (CSV) -> Transform (Pandas) -> Load (SQLite) -> Export (JSON for dashboard)

Run:  python etl_pipeline.py
"""
import pandas as pd
import sqlite3
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SQL_DIR = BASE_DIR / "sql"
DB_PATH = DATA_DIR / "ecommerce.db"
EXPORT_PATH = BASE_DIR / "dashboard" / "dashboard_data.json"


def extract():
    print("[EXTRACT] Reading source CSVs...")
    products = pd.read_csv(DATA_DIR / "products.csv")
    orders = pd.read_csv(DATA_DIR / "orders.csv", parse_dates=["order_date"])
    print(f"  products: {products.shape}, orders: {orders.shape}")
    return products, orders


def transform(products: pd.DataFrame, orders: pd.DataFrame):
    print("[TRANSFORM] Cleaning & validating...")
    # Drop duplicates / nulls
    orders = orders.drop_duplicates(subset="order_id").dropna(subset=["order_id", "product_id"])
    products = products.drop_duplicates(subset="product_id")

    # Type enforcement
    orders["quantity"] = orders["quantity"].astype(int)
    orders["returned"] = orders["returned"].astype(int)

    # Re-derive revenue/profit to guarantee consistency (data quality rule)
    orders = orders.merge(products[["product_id", "unit_cost"]], on="product_id", how="left", suffixes=("", "_ref"))
    orders["cost"] = (orders["unit_cost"] * orders["quantity"]).round(2)
    orders["revenue"] = (orders["unit_price"] * orders["quantity"] * (1 - orders["discount_pct"])).round(2)
    orders["profit"] = (orders["revenue"] - orders["cost"]).round(2)
    orders.drop(columns=["unit_cost"], inplace=True)

    orders["order_date"] = orders["order_date"].dt.strftime("%Y-%m-%d")
    print(f"  Final orders after cleaning: {orders.shape[0]} rows")
    return products, orders


def load(products: pd.DataFrame, orders: pd.DataFrame):
    print("[LOAD] Writing to SQLite database...")
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    with open(SQL_DIR / "schema.sql") as f:
        schema_sql = f.read().split("-- =====")[0]  # only DDL part before queries block re-split below
    # Execute full file's CREATE statements (ignore commented query examples)
    conn.executescript("".join(l for l in open(SQL_DIR / "schema.sql") if not l.strip().startswith("--")))
    products.to_sql("dim_products", conn, if_exists="replace", index=False)
    orders.to_sql("fact_orders", conn, if_exists="replace", index=False)
    conn.commit()
    print(f"  Loaded into {DB_PATH}")
    return conn


def build_aggregates(conn):
    print("[EXPORT] Building aggregate views for dashboard...")

    def q(sql):
        return pd.read_sql(sql, conn)

    kpis = q("""
        SELECT ROUND(SUM(revenue),2) AS total_revenue,
               ROUND(SUM(profit),2) AS total_profit,
               COUNT(*) AS total_orders,
               COUNT(DISTINCT customer_id) AS total_customers,
               ROUND(100.0*SUM(returned)/COUNT(*),2) AS return_rate_pct,
               ROUND(SUM(revenue)*1.0/COUNT(*),2) AS avg_order_value
        FROM fact_orders
    """).iloc[0].to_dict()

    monthly = q("""
        SELECT strftime('%Y-%m', order_date) AS month,
               ROUND(SUM(revenue),2) AS revenue, ROUND(SUM(profit),2) AS profit,
               COUNT(*) AS orders
        FROM fact_orders GROUP BY 1 ORDER BY 1
    """).to_dict(orient="records")

    by_category = q("""
        SELECT p.category, ROUND(SUM(o.revenue),2) AS revenue, ROUND(SUM(o.profit),2) AS profit,
               SUM(o.quantity) AS units_sold
        FROM fact_orders o JOIN dim_products p ON o.product_id = p.product_id
        GROUP BY p.category ORDER BY revenue DESC
    """).to_dict(orient="records")

    top_products = q("""
        SELECT p.product_name, p.category, ROUND(SUM(o.revenue),2) AS revenue,
               SUM(o.quantity) AS units_sold
        FROM fact_orders o JOIN dim_products p ON o.product_id = p.product_id
        GROUP BY p.product_name ORDER BY revenue DESC LIMIT 10
    """).to_dict(orient="records")

    by_channel = q("""
        SELECT channel, ROUND(SUM(revenue),2) AS revenue, COUNT(*) AS orders,
               ROUND(100.0*SUM(returned)/COUNT(*),2) AS return_rate_pct
        FROM fact_orders GROUP BY channel ORDER BY revenue DESC
    """).to_dict(orient="records")

    by_region = q("""
        SELECT region, ROUND(SUM(revenue),2) AS revenue, ROUND(SUM(profit),2) AS profit,
               COUNT(DISTINCT customer_id) AS customers
        FROM fact_orders GROUP BY region ORDER BY revenue DESC
    """).to_dict(orient="records")

    return_by_category = q("""
        SELECT p.category, ROUND(100.0*SUM(o.returned)/COUNT(*),2) AS return_rate_pct
        FROM fact_orders o JOIN dim_products p ON o.product_id = p.product_id
        GROUP BY p.category ORDER BY return_rate_pct DESC
    """).to_dict(orient="records")

    payload = {
        "kpis": kpis,
        "monthly": monthly,
        "by_category": by_category,
        "top_products": top_products,
        "by_channel": by_channel,
        "by_region": by_region,
        "return_by_category": return_by_category,
    }

    os.makedirs(EXPORT_PATH.parent, exist_ok=True)
    with open(EXPORT_PATH, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"  Exported dashboard data -> {EXPORT_PATH}")
    return payload


def run():
    products, orders = extract()
    products, orders = transform(products, orders)
    conn = load(products, orders)
    build_aggregates(conn)
    conn.close()
    print("[DONE] ETL pipeline completed successfully.")


if __name__ == "__main__":
    run()
