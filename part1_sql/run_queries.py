import sqlite3
import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(
    BASE_DIR,
    "..",
    "data",
    "meesho_reseller.db"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "output"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()


# ============================================================
# 1. Monthly revenue by category
# ============================================================

query1 = """
SELECT
    month,
    category,
    ROUND(SUM(quantity * unit_price), 2) AS revenue,
    COUNT(*) AS n_orders
FROM orders
GROUP BY month, category
ORDER BY
    CASE month
        WHEN 'April' THEN 1
        WHEN 'May' THEN 2
        WHEN 'June' THEN 3
    END,
    category
"""

cursor.execute(query1)

rows = cursor.fetchall()

output_file = os.path.join(
    OUTPUT_DIR,
    "monthly_category_revenue.csv"
)

with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow([
        "month",
        "category",
        "revenue",
        "n_orders"
    ])

    writer.writerows(rows)

print(f"Created: {output_file}")


# ============================================================
# 2. Region-wise revenue and order count
# ============================================================

query2 = """
SELECT
    r.region,
    ROUND(SUM(o.quantity * o.unit_price), 2) AS total_revenue,
    COUNT(*) AS order_count
FROM orders o
JOIN resellers r
    ON o.reseller_id = r.reseller_id
GROUP BY r.region
ORDER BY r.region
"""

cursor.execute(query2)

rows = cursor.fetchall()

output_file = os.path.join(
    OUTPUT_DIR,
    "region_revenue.csv"
)

with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow([
        "region",
        "total_revenue",
        "order_count"
    ])

    writer.writerows(rows)

print(f"Created: {output_file}")


# ============================================================
# 3. Top 5 resellers by total spend
# ============================================================

query3 = """
SELECT
    r.reseller_id,
    r.reseller_name,
    ROUND(SUM(o.quantity * o.unit_price), 2) AS total_spend
FROM orders o
JOIN resellers r
    ON o.reseller_id = r.reseller_id
GROUP BY
    r.reseller_id,
    r.reseller_name
HAVING total_spend > 50000
ORDER BY total_spend DESC
LIMIT 5
"""

cursor.execute(query3)

rows = cursor.fetchall()

output_file = os.path.join(
    OUTPUT_DIR,
    "top_resellers.csv"
)

with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow([
        "reseller_id",
        "reseller_name",
        "total_spend"
    ])

    writer.writerows(rows)

print(f"Created: {output_file}")


# ============================================================
# 4A. Resellers who never placed an order
# ============================================================

query4a = """
SELECT
    r.reseller_id,
    r.reseller_name
FROM resellers r
LEFT JOIN orders o
    ON r.reseller_id = o.reseller_id
WHERE o.order_id IS NULL
"""

cursor.execute(query4a)

rows = cursor.fetchall()

output_file = os.path.join(
    OUTPUT_DIR,
    "never_ordered_resellers.csv"
)

with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow([
        "reseller_id",
        "reseller_name"
    ])

    writer.writerows(rows)

print(f"Created: {output_file}")


# ============================================================
# 4B. COUNT(*) vs COUNT(order_id)
# ============================================================

query4b = """
SELECT
    r.reseller_id,
    COUNT(*) AS count_star,
    COUNT(o.order_id) AS count_order_id
FROM resellers r
LEFT JOIN orders o
    ON r.reseller_id = o.reseller_id
GROUP BY r.reseller_id
HAVING COUNT(o.order_id) = 0
"""

cursor.execute(query4b)

rows = cursor.fetchall()

output_file = os.path.join(
    OUTPUT_DIR,
    "zero_order_count_demo.csv"
)

with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow([
        "reseller_id",
        "count_star",
        "count_order_id"
    ])

    writer.writerows(rows)

print(f"Created: {output_file}")


# ============================================================
# 5. June Delivered AOV
# ============================================================

query5 = """
SELECT
    ROUND(
        SUM(quantity * unit_price) * 1.0 / COUNT(*),
        2
    ) AS aov
FROM orders
WHERE month = 'June'
  AND status = 'Delivered'
"""

cursor.execute(query5)

rows = cursor.fetchall()

output_file = os.path.join(
    OUTPUT_DIR,
    "june_delivered_aov.csv"
)

with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow([
        "aov"
    ])

    writer.writerows(rows)

print(f"Created: {output_file}")


conn.close()

print("\nAll Part 1 SQL outputs generated successfully.")