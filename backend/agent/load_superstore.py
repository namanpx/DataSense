"""
backend/agent/load_superstore.py
==================================
Downloads the Superstore Sales CSV dataset, cleans/renames the columns,
and loads it into the DuckDB 'orders' table.
"""
from __future__ import annotations

import logging
import urllib.request
from pathlib import Path
import pandas as pd
import duckdb

logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CSV_PATH = RAW_DIR / "superstore.csv"
DB_PATH = PROJECT_ROOT / "data" / "analytics.duckdb"

DATASET_URL = "https://raw.githubusercontent.com/dhruvsoin/sales_perfomance_dashboard/main/data/raw/Sample%20-%20Superstore.csv"

def download_dataset() -> None:
    """Download the dataset from the public GitHub raw URL if not already downloaded."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if not CSV_PATH.exists():
        logger.info("Downloading Superstore Sales dataset from %s...", DATASET_URL)
        urllib.request.urlretrieve(DATASET_URL, CSV_PATH)
        logger.info("Dataset downloaded and saved to %s", CSV_PATH)
    else:
        logger.info("Dataset CSV already exists at %s", CSV_PATH)

def load_and_clean_data() -> pd.DataFrame:
    """Reads the CSV, renames/selects columns, and converts types."""
    download_dataset()

    logger.info("Reading dataset from %s", CSV_PATH)
    # The file might use windows-1252 or utf-8 encoding.
    try:
        df = pd.read_csv(CSV_PATH, encoding="utf-8")
    except UnicodeDecodeError:
        logger.info("UTF-8 decoding failed, trying windows-1252...")
        df = pd.read_csv(CSV_PATH, encoding="windows-1252")

    # Rename & select columns per mapping instructions:
    # Existing schema column -> Maps from:
    #   order_id   <- Order ID (keep as string to avoid format loss and collisions)
    #   product    <- Product Name
    #   category   <- Category
    #   region     <- Region
    #   sale_date  <- Order Date (convert to proper DATE)
    #   amount     <- Sales
    #   sub_category <- Sub-Category (optional)
    #   profit     <- Profit (optional)
    #   discount   <- Discount (optional)
    #   quantity   <- Quantity (optional)
    #   state      <- State (optional)
    
    mapping = {
        "Order ID": "order_id",
        "Product Name": "product",
        "Category": "category",
        "Region": "region",
        "Order Date": "sale_date",
        "Sales": "amount",
        "Sub-Category": "sub_category",
        "Profit": "profit",
        "Discount": "discount",
        "Quantity": "quantity",
        "State": "state"
    }

    # Ensure all required source columns exist
    missing_cols = [col for col in mapping.keys() if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing expected columns in CSV: {missing_cols}")

    # Select and rename columns
    df_cleaned = df[list(mapping.keys())].rename(columns=mapping).copy()

    # Convert sale_date to datetime and then to date format YYYY-MM-DD
    # Order Date is usually MM/DD/YYYY in Superstore dataset
    df_cleaned["sale_date"] = pd.to_datetime(df_cleaned["sale_date"]).dt.date

    # Cast other columns to ensure correct type
    df_cleaned["order_id"] = df_cleaned["order_id"].astype(str)
    df_cleaned["product"] = df_cleaned["product"].astype(str)
    df_cleaned["category"] = df_cleaned["category"].astype(str)
    df_cleaned["region"] = df_cleaned["region"].astype(str)
    df_cleaned["amount"] = pd.to_numeric(df_cleaned["amount"], errors="coerce").astype(float)
    
    # Optional columns
    df_cleaned["sub_category"] = df_cleaned["sub_category"].astype(str)
    df_cleaned["profit"] = pd.to_numeric(df_cleaned["profit"], errors="coerce").astype(float)
    df_cleaned["discount"] = pd.to_numeric(df_cleaned["discount"], errors="coerce").astype(float)
    df_cleaned["quantity"] = pd.to_numeric(df_cleaned["quantity"], errors="coerce").astype(int)
    df_cleaned["state"] = df_cleaned["state"].astype(str)

    logger.info("Cleaned dataframe size: %d rows", len(df_cleaned))
    return df_cleaned

def load_into_duckdb() -> None:
    """Load the cleaned pandas DataFrame into the DuckDB 'orders' table."""
    df_cleaned = load_and_clean_data()
    
    # Ensure directory for DB exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info("Connecting to DuckDB at %s", DB_PATH)
    con = duckdb.connect(str(DB_PATH))
    
    # Register the dataframe so DuckDB can see it
    con.register("df_temp", df_cleaned)
    
    # Create or replace table
    logger.info("Creating/Replacing table 'orders' in DuckDB...")
    con.execute("DROP TABLE IF EXISTS orders")
    con.execute("CREATE TABLE orders AS SELECT * FROM df_temp")
    
    # Unregister temp name
    con.unregister("df_temp")
    
    # Get row count and verify
    row_count = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    con.close()
    
    logger.info("Successfully loaded %d rows into 'orders' table in DuckDB.", row_count)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    load_into_duckdb()
