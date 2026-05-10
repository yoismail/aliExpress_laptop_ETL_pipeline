import logging
from etl.logger import setup_logging, section, timed
from etl.scraper import test_response, ALIEXPRESS_URL
from etl.wipe_all import wipe
from etl.extract import main as run_extract
from etl.transform import main as run_transform
from etl.load import main as run_load

setup_logging()


@timed
def main():
    section("FULL PIPELINE START")
    logging.info("🚀 wipe → extract → transform → load\n")

    # Wipe old data 
    section("WIPING OLD DATA")
    wipe("all")

    # Health check 
    section("HEALTH CHECK")
    if not test_response(ALIEXPRESS_URL):
        logging.error("❌ Site unreachable — aborting pipeline")
        return

    # Extract 
    section("EXTRACT")
    raw_df = run_extract()
    if raw_df is None:
        logging.error("❌ Extraction failed — aborting pipeline")
        return

    # Transform — receives raw df directly 
    section("TRANSFORM")
    transformed_df = run_transform(df=raw_df)
    if transformed_df is None:
        logging.error("❌ Transform failed — aborting pipeline")
        return

    # Load — receives transformed df directly 
    section("LOAD")
    success = run_load(df=transformed_df)

    if success:
        logging.info("\033[92m🎉 PIPELINE COMPLETED SUCCESSFULLY!\033[0m\n")
    else:
        logging.error("❌ Pipeline finished with errors")


if __name__ == "__main__":
    main()
