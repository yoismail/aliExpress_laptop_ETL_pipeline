import logging
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine
from etl.logger import setup_logging, section, timed
from etl.db_config import DB_CONFIG

setup_logging()

TRANSFORMED_CSV = Path("data/transformed_laptops.csv")


def get_db_engine():
    try:
        engine = create_engine(
            f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
            f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        )
        logging.info("✅ Database engine created")
        return engine
    except Exception as e:
        logging.error(f"❌ Failed to create engine: {e}")
        return None


def load_to_db(df: pd.DataFrame, engine) -> bool:
    section("Loading Data to Database")
    try:
        # Deduplicate against existing rows before inserting
        existing = pd.read_sql(
            "SELECT product_name, product_price FROM laptops", engine)

        before = len(df)
        df = df.merge(
            existing,
            on=["product_name", "product_price"],
            how="left",
            indicator=True
        )
        df = df[df["_merge"] == "left_only"].drop(columns=["_merge"])
        logging.info(f"✅ Skipping {before - len(df)} already existing rows")

        if df.empty:
            logging.info("ℹ️ No new rows to insert — table already up to date")
            return True

        df.to_sql(
            name="laptops",
            con=engine,
            if_exists="append",
            index=False,
            method="multi"
        )
        logging.info(f"✅ {len(df)} new rows loaded into laptops table")
        return True

    except Exception as e:
        logging.exception(f"❌ Failed to load data: {e}")
        return False


@timed
def main(df: pd.DataFrame = None) -> bool:
    section("Starting Load Process")

    # Accept df from run_all or load from CSV as fallback
    if df is None:
        if TRANSFORMED_CSV.exists():
            df = pd.read_csv(TRANSFORMED_CSV)
            logging.info(f"✅ Loaded transformed data from {TRANSFORMED_CSV}")
        else:
            logging.error("❌ No transformed data — run transform first")
            return False

    if df is None or df.empty:
        logging.error("❌ Empty DataFrame — nothing to load")
        return False

    engine = get_db_engine()
    if engine is None:
        return False

    success = load_to_db(df, engine)

    if success:
        logging.info("✅ Load complete")
    return success


if __name__ == "__main__":
    main()
