import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger('ingestor')

INPUT_DIR = "/data/input"
OUTPUT_FILE = "/data/ingested.txt"

def ingest():
    content = ""
    file_proceesed_counts = 0

    for filename in sorted(os.listdir(INPUT_DIR)):
        file_path = os.path.join(INPUT_DIR, filename)
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding="utf-8") as f:
                    content += f"\n--- {filename} ---\n"
                    for line in f:
                        content += line
                    content += "\n"
                    file_proceesed_counts += 1
            except Exception as e:
                logger.error(f"Error reading file [{filename}]: {e}")
    
    if file_proceesed_counts == 0:
        logger.warning(f"No input files found to read in the {INPUT_DIR}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as w:
        w.write(content)
    logger.info(f"Successfully ingested {file_proceesed_counts} files and write to {OUTPUT_FILE}")

if __name__ == "__main__":
    ingest()