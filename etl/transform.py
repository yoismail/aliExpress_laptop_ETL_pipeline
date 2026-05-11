import logging
import pandas as pd
from pathlib import Path
from etl.logger import setup_logging, section, timed

setup_logging()

RAW_CSV = Path("data/aliexpress_laptops.csv")
TRANSFORMED_CSV = Path("data/transformed_laptops.csv")


def validate_quality(df: pd.DataFrame) -> bool:
    """Basic data quality checks after transformation."""
    issues = []

    null_prices = df["product_price"].isna().sum()
    if null_prices > 0:
        issues.append(f"{null_prices} rows with null product_price")

    zero_prices = (df["product_price"] == 0).sum()
    if zero_prices > 0:
        issues.append(f"{zero_prices} rows with zero product_price")

    if df["product_name"].isna().sum() > 0:
        issues.append("Some rows have null product_name")

    if issues:
        for issue in issues:
            logging.warning(f"⚠️ Data quality issue: {issue}")
        return False

    logging.info("✅ Data quality checks passed")
    return True


def transform(df: pd.DataFrame) -> pd.DataFrame | None:
    section("Transforming Data")

    if df is None or df.empty:
        logging.error("❌ No data to transform")
        return None

    logging.info(f"Input — {len(df)} rows, {len(df.columns)} columns")

    # Drop duplicates
    before = len(df)
    df = df.drop_duplicates(subset=["product_name", "product_price"])
    logging.info(
        f"✅ Dropped {before - len(df)} duplicates — {len(df)} remaining")

    # Convert prices to numeric
    df["product_price"] = pd.to_numeric(df["product_price"], errors="coerce")
    df["was_price"] = pd.to_numeric(df["was_price"],     errors="coerce")
    logging.info("✅ Price columns converted to numeric")

    # Fill missing prices with median
    price_median = df["product_price"].median()
    df["product_price"] = df["product_price"].fillna(price_median)
    logging.info(
        f"✅ Missing product prices filled with median: £{price_median:.2f}")

    # Clean total sold
    df["total_sold_count"] = pd.to_numeric(
        df["total_sold_count"], errors="coerce"
    ).fillna(0).astype(int)
    logging.info("✅ Total sold count cleaned to integer")

    # Discount amount
    df["discount_amount"] = (
        df["was_price"].fillna(0) - df["product_price"].fillna(0)
    ).clip(lower=0).round(2)
    logging.info("✅ Discount amount calculated")

    # Discount percentage
    df["discount_percentage"] = (
        df["discount_amount"] /
        df["was_price"].replace(0, float("nan")) * 100
    ).round(1).fillna(0.0)
    logging.info("✅ Discount percentage calculated")

    # Boolean flags
    df["is_on_sale"] = df["was_price"] > df["product_price"]
    df["is_free_shipping"] = df["shipping_status"] == "Free shipping"
    df["is_top_seller"] = df["top_selling_status"] != "Not top selling"
    logging.info("✅ Boolean flags created")

    # Price band
    df["price_band"] = pd.cut(
        df["product_price"],
        bins=[0, 100, 300, 600, 1000, float("inf")],
        labels=["Budget", "Mid-Range", "Upper-Mid", "Premium", "Luxury"]
    )
    logging.info("✅ Price band assigned")

    # Select final columns
    df = df[[
        "product_name", "product_price", "was_price",
        "discount_amount", "discount_percentage",
        "is_on_sale", "is_free_shipping", "is_top_seller", "price_band"
    ]].reset_index(drop=True)

    # Data quality check
    validate_quality(df)

    logging.info(
        f"✅ Transform complete — {len(df)} rows, {len(df.columns)} columns")
    logging.info(f"\n{df.head()}")

    return df


@timed
def main(df: pd.DataFrame = None) -> pd.DataFrame | None:
    section("Starting Transformation Process")

    # Accept df from run_all or load from CSV as fallback
    if df is None:
        if RAW_CSV.exists():
            df = pd.read_csv(RAW_CSV).copy()  # Avoid SettingWithCopyWarning

            logging.info(f"✅ Loaded raw data from {RAW_CSV}")
        else:
            logging.error("❌ No raw data available — run extract first")
            return None

    transformed_df = transform(df)

    if transformed_df is not None:
        TRANSFORMED_CSV.parent.mkdir(parents=True, exist_ok=True)
        transformed_df.to_csv(TRANSFORMED_CSV, index=False)
        logging.info(f"✅ Transformed data saved to {TRANSFORMED_CSV}")
        return transformed_df

    logging.error("❌ Transform failed")
    return None


if __name__ == "__main__":
    main()
