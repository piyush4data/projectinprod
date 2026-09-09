# E-commerce Sales & Inventory Analytics Suite

An end-to-end analytics project simulating a real e-commerce data pipeline — from raw
transactional data to a live interactive dashboard.

**Stack:** Python (Pandas) · SQL (SQLite) · ETL · Interactive HTML/Chart.js Dashboard
*(swap the final layer for Power BI or Tableau by pointing either tool at `data/ecommerce.db`)*

## 🔗 Live Dashboard
Open `dashboard/index.html` in any browser, or host it free via **GitHub Pages**
(Settings → Pages → deploy from `/dashboard`).

## 📁 Project Structure
```
ecommerce_project/
├── data/
│   ├── products.csv          # raw product master data (25 SKUs, 5 categories)
│   ├── orders.csv             # raw order-level transactions (6,000 rows, 2024–2025)
│   └── ecommerce.db           # SQLite warehouse (built by the ETL script)
├── sql/
│   └── schema.sql             # star-schema DDL + 6 analytical queries
├── etl/
│   └── etl_pipeline.py        # Extract → Transform → Load → Export pipeline
├── dashboard/
│   ├── index.html             # self-contained interactive dashboard
│   └── dashboard_data.json    # aggregated output consumed by the dashboard
└── README.md
```

## ⚙️ How It Works
1. **Extract** — reads raw `products.csv` and `orders.csv`
2. **Transform** — deduplicates, validates types, and re-derives revenue/profit
   for data-quality consistency (Pandas)
3. **Load** — writes a clean star schema (`dim_products`, `fact_orders`) into
   SQLite (`sql/schema.sql`)
4. **Export** — runs 6 analytical SQL queries (monthly trend, category mix,
   top products, channel performance, regional performance, return rates) and
   exports the results as JSON
5. **Visualize** — a single-file HTML dashboard renders KPIs and 5 charts
   from that JSON — no server required

## ▶️ Run It Yourself
```bash
pip install pandas numpy
python etl/etl_pipeline.py     # rebuilds ecommerce.db + dashboard_data.json
open dashboard/index.html      # view the dashboard
```

## 📊 Dashboard Highlights
- KPI strip: total revenue, profit, orders, unique customers, AOV, return rate
- Monthly revenue & profit trend (24 months)
- Revenue mix by category
- Sales channel performance (Website / App / Marketplace)
- Regional revenue & profit comparison
- Top 10 products by revenue
- Return rate by category

## 💡 Resume Bullet (example)
> Built an end-to-end e-commerce analytics pipeline (Python/Pandas ETL → SQLite
> star schema → interactive dashboard) processing 6,000+ transactions across
> 5 regions and 3 sales channels; surfaced revenue, profitability, and return-rate
> insights via 6 SQL analytical queries and a KPI dashboard.

## 🔁 Extending This Project
- Load `data/ecommerce.db` directly into **Power BI Desktop** or **Tableau**
  (via ODBC/SQLite connector) for a native BI version
- Swap the synthetic CSVs for a real dataset (Kaggle's Online Retail, Olist, etc.)
- Add a `cohort_retention` table + Python cohort analysis
- Deploy the dashboard for free on GitHub Pages
