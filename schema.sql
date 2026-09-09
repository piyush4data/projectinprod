-- ============================================================
-- E-commerce Sales & Inventory Analytics Suite - Schema
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_products (
    product_id      INTEGER PRIMARY KEY,
    product_name    TEXT NOT NULL,
    category        TEXT NOT NULL,
    unit_cost       REAL NOT NULL,
    unit_price      REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_orders (
    order_id        INTEGER PRIMARY KEY,
    order_date      DATE NOT NULL,
    product_id      INTEGER NOT NULL REFERENCES dim_products(product_id),
    region          TEXT NOT NULL,
    channel         TEXT NOT NULL,
    quantity        INTEGER NOT NULL,
    unit_price      REAL NOT NULL,
    discount_pct    REAL NOT NULL,
    revenue         REAL NOT NULL,
    cost            REAL NOT NULL,
    profit          REAL NOT NULL,
    returned        INTEGER NOT NULL,
    customer_id     TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_orders_date     ON fact_orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_category ON fact_orders(product_id);
CREATE INDEX IF NOT EXISTS idx_orders_region   ON fact_orders(region);

-- ============================================================
-- Key Analytical Queries (used to power the dashboard)
-- ============================================================

-- 1. Monthly revenue & profit trend
-- SELECT strftime('%Y-%m', order_date) AS month,
--        SUM(revenue) AS revenue, SUM(profit) AS profit
-- FROM fact_orders GROUP BY 1 ORDER BY 1;

-- 2. Revenue by category
-- SELECT p.category, SUM(o.revenue) AS revenue, SUM(o.profit) AS profit
-- FROM fact_orders o JOIN dim_products p ON o.product_id = p.product_id
-- GROUP BY p.category ORDER BY revenue DESC;

-- 3. Top 10 products by revenue
-- SELECT p.product_name, SUM(o.revenue) revenue, SUM(o.quantity) units_sold
-- FROM fact_orders o JOIN dim_products p ON o.product_id = p.product_id
-- GROUP BY p.product_name ORDER BY revenue DESC LIMIT 10;

-- 4. Sales channel performance
-- SELECT channel, SUM(revenue) revenue, COUNT(*) orders,
--        ROUND(100.0*SUM(returned)/COUNT(*),2) AS return_rate_pct
-- FROM fact_orders GROUP BY channel;

-- 5. Regional performance
-- SELECT region, SUM(revenue) revenue, SUM(profit) profit, COUNT(DISTINCT customer_id) customers
-- FROM fact_orders GROUP BY region ORDER BY revenue DESC;

-- 6. Return rate by category
-- SELECT p.category, ROUND(100.0*SUM(o.returned)/COUNT(*),2) AS return_rate_pct
-- FROM fact_orders o JOIN dim_products p ON o.product_id = p.product_id
-- GROUP BY p.category ORDER BY return_rate_pct DESC;
