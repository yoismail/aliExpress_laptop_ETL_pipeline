# 🛒 AliExpress Laptop ETL Pipeline
*A production-grade web scraping and ETL pipeline built with Python, Selenium, BeautifulSoup, and PostgreSQL.*

---

## 🏷️ Badges
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-blue)
![ETL Pipeline](https://img.shields.io/badge/ETL-Production--Grade-green)
![Selenium](https://img.shields.io/badge/Scraping-Selenium-orange)
![BeautifulSoup](https://img.shields.io/badge/Parsing-BeautifulSoup-yellow)

---

## 🌟 Why I Built This Project

I built the **AliExpress Laptop ETL Pipeline** to demonstrate how I approach real-world data engineering problems — not just scraping data, but designing a **reliable, modular, analytics-ready pipeline** from source to database.

My goals were to build a pipeline that is:

- **Reliable** — retry logic, explicit waits, and health checks before every run
- **Reproducible** — clean separation of extract, transform, and load responsibilities
- **Maintainable** — modular ETL components with consistent logging throughout
- **Analytics-ready** — enriched data with discount metrics, price bands, and boolean flags
- **Observable** — production-grade logging with timing, color, and rotating file output

This project reflects how I think as a data engineer:
**structured, intentional, and focused on long-term maintainability.**

---

## 🧠 What This Project Demonstrates

### 🔹 Web Scraping with Selenium and BeautifulSoup
I built a real browser scraper that handles cookie banners, lazy loading, pagination, and bot detection avoidance across 10 pages of AliExpress listings.

### 🔹 End-to-End ETL Engineering
A complete pipeline that scrapes, validates, transforms, and loads data into PostgreSQL — with each stage isolated and independently runnable.

### 🔹 Data Cleaning and Feature Engineering
I engineered business-friendly features including discount amounts, discount percentages, price bands, free shipping flags, top seller flags, and on-sale detection.

### 🔹 Production-Grade Logging
A cross-platform, UTF-8-aware logging framework with colorized console output, rotating file logs, emoji-safe formatting, and execution timing.

### 🔹 Modular, Maintainable Architecture
Each ETL stage is isolated, independently runnable, and orchestrated through a clean pipeline runner with direct df passing between steps.

---

## 🌐 High-Level Architecture

```
AliExpress (Live)
      ↓
  scraper.py        — health check + browser setup
      ↓
  extract.py        — scrapes 10 pages, returns raw DataFrame
      ↓
  transform.py      — cleans, enriches, validates data quality
      ↓
  load.py           — deduplicates and appends to PostgreSQL
      ↓
  PostgreSQL
  └── laptops table
```

---

## ⭐ Features at a Glance

- Live web scraping with Selenium and BeautifulSoup
- Multi-page pagination with retry logic and explicit waits
- Bot detection avoidance — disables automation flags
- Cookie banner auto-acceptance
- Modular ETL pipeline — extract → transform → load
- Feature engineering — discount amount, discount %, price band, boolean flags
- Data quality validation before loading
- Append-only loading with pre-insert deduplication
- Production-grade logging with timing and color
- One-command pipeline orchestration
- Wipe utility for clean reruns

---

## 🗂 Project Structure

```
etl/
├── scraper.py           — Selenium browser setup and health check
├── extract.py           — Scrapes AliExpress and returns raw DataFrame
├── transform.py         — Cleans, enriches, and validates data
├── load.py              — Loads transformed data into PostgreSQL
├── run_all.py           — Orchestrates the full pipeline
├── wipe_all.py          — Wipes raw and/or transformed CSV files
├── logger.py            — Production-grade logging system
└── db_config.py         — Database connection configuration

sql/
└── create_table.sql     — DDL for the laptops table

data/ (generated)
├── aliexpress_laptops.csv      — Raw scraped data
└── transformed_laptops.csv     — Cleaned and enriched data

logs/
└── pipeline.log         — Rotating log file
```

---

## 🔄 Pipeline Flow

### 1️⃣ Health Check
`scraper.py` sends an HTTP request and opens a real Chrome browser to verify the site is reachable before scraping begins.

### 2️⃣ Extract
`extract.py` scrapes 10 pages of AliExpress laptop listings using Selenium for navigation and BeautifulSoup for parsing. Returns a raw DataFrame with snake_case columns.

### 3️⃣ Transform
`transform.py` cleans prices, removes duplicates, fills missing values with the median, engineers new features, and runs data quality checks before passing the DataFrame downstream.

### 4️⃣ Load
`load.py` deduplicates against existing rows and appends only new data to PostgreSQL — never wiping existing records.

### 5️⃣ Orchestrate
`run_all.py` executes the full pipeline with structured logs, execution timings, and clean abort handling at every failure point.

---

## 🧩 Data Extracted

| Column | Description |
|---|---|
| `product_name` | Full listing title |
| `product_price` | Current sale price (£) |
| `was_price` | Original crossed-out price (£) |
| `discount_info` | Discount label from listing |
| `extra_discount` | Additional coupon or offer |
| `shipping_status` | Free shipping or not |
| `total_sold_count` | Number of units sold |
| `top_selling_status` | Top selling on AliExpress flag |
| `scraped_at` | Timestamp of scrape |

---

## 🧩 Features Engineered in Transform

| Column | Description |
|---|---|
| `discount_amount` | `was_price - product_price` in £ |
| `discount_percentage` | % saved off original price |
| `is_on_sale` | Boolean — was price exists and is higher |
| `is_free_shipping` | Boolean — free shipping offered |
| `is_top_seller` | Boolean — top selling badge present |
| `price_band` | Budget / Mid-Range / Upper-Mid / Premium / Luxury |

---

## 📊 Example Business Questions This Data Answers

```sql
-- Which laptops offer the best discount?
SELECT product_name, product_price, discount_percentage
FROM laptops
WHERE is_on_sale = TRUE
ORDER BY discount_percentage DESC
LIMIT 10;

-- What price band has the most listings?
SELECT price_band, COUNT(*) AS total
FROM laptops
GROUP BY price_band
ORDER BY total DESC;

-- Do free shipping laptops cost more on average?
SELECT is_free_shipping, ROUND(AVG(product_price), 2) AS avg_price
FROM laptops
GROUP BY is_free_shipping;
```

---

## ▶️ Running the Pipeline

### Install dependencies
```bash
pip install -r requirements.txt
```

### Configure environment
Create a `.env` file in the project root:
```bash
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
```

### Create the database table
```bash
psql -U your_user -d your_database -f sql/create_table.sql
```

### Run the full pipeline
```bash
python -m etl.run_all
```

### Run individual steps
```bash
python -m etl.extract      # scrape and save raw data
python -m etl.transform    # clean and enrich
python -m etl.load         # load to PostgreSQL
```

### Wipe data files
```bash
python -m etl.wipe_all raw          # delete raw CSV
python -m etl.wipe_all transformed  # delete transformed CSV
python -m etl.wipe_all all          # delete both
python -m etl.wipe_all data         # delete entire data folder
```

---

## 🧩 Logging System

I engineered a production-grade logging system designed for ETL pipelines running across different environments.

- **Cross-platform UTF-8 detection** — Windows Terminal, VS Code, PowerShell 7+, macOS/Linux
- **Emoji-safe output** — stripped from console only when terminal cannot support them
- **Dual-handler logging** — colorized console + rotating file handler
- **Message-only colorization** — timestamps stay clean
- **Section banners** — visually separate each ETL stage
- **Execution timing** — `@timed` decorator logs how long each step takes
- **SQLAlchemy noise suppression** — engine logs silenced for cleaner output

---

## 👤 Author

**Yomi Ismail**  
Data Engineer

[![GitHub](https://img.shields.io/badge/GitHub-yoismail-black?logo=github)](https://github.com/yoismail)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-yomi--ismail-blue?logo=linkedin)](https://www.linkedin.com/in/yomi-ismail/)
