import shutil
import logging
import argparse
from pathlib import Path
from etl.logger import section, timed

RAW_CSV = Path("data/aliexpress_laptops.csv")
TRANSFORMED_CSV = Path("data/transformed_laptops.csv")
DATA_FOLDER = Path("data")


def delete_file(path: Path):
    """Delete a single file."""
    if path.exists() and path.is_file():
        path.unlink()
        logging.info(f"🗑️ Deleted file: {path}")
    else:
        logging.info(f"⚠️ File not found (skipped): {path}")


def delete_folder(path: Path):
    """Delete an entire folder and its contents."""
    if path.exists() and path.is_dir():
        shutil.rmtree(path)
        logging.info(f"🗑️ Deleted folder: {path}")
    else:
        logging.info(f"⚠️ Folder not found (skipped): {path}")


@timed
def wipe(mode: str):
    section(f"Wiping — mode: {mode}")
    mode = mode.lower()

    if mode == "raw":
        delete_file(RAW_CSV)

    elif mode == "transformed":
        delete_file(TRANSFORMED_CSV)

    elif mode == "all":
        delete_file(RAW_CSV)
        delete_file(TRANSFORMED_CSV)

    elif mode == "data":
        delete_folder(DATA_FOLDER)

    else:
        logging.error(f"❌ Unknown mode: {mode}")

    logging.info(f"\033[92m🎉 Wipe completed for mode: {mode}\033[0m")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Wipe ETL data files or folders.")
    parser.add_argument(
        "mode",
        choices=["raw", "transformed", "all", "data"],
        help="raw=raw CSV, transformed=transformed CSV, all=both CSVs, data=entire folder"
    )
    args = parser.parse_args()
    wipe(args.mode)
