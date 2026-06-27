import os
import logging
import time

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level= logging.INFO
)
logger = logging.getLogger('prioritizer')

INPUT_FILE="/data/summary.txt"
OUTPUT_FILE="/data/prioritized.txt"

PRIORITY_KEYWORDS = [
    "urgent", "today", "asap", "important",
    "deadline", "critical", "action required"
]

def score_line(line):
    """ Count occurence of priority keywords in the line """
    line = line.lower()
    return sum(1 for keyword in PRIORITY_KEYWORDS if keyword in line)

def main():
    with open(INPUT_FILE, 'r', encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    scored = [(line, score_line(line)) for line in lines]
    scored.sort(key=lambda x:x[1], reverse=True)

    with open(OUTPUT_FILE, 'w', encoding="utf-8") as out:
        for line, score in scored:
            out.write(f"[{score}] {line}\n")

    logger.info(f"Prioritized {len(scored)} items into {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
