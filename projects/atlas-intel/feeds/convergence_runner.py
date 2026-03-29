#!/usr/bin/env python3
"""Combined scheduler for geopolitical feed (every 15 min) and correlator (every 5 min)."""

import logging
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from feeds.geopolitical_feed import run as run_geopolitical
from feeds.correlator import run as run_correlator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger("atlas_intel.convergence_runner")

CORRELATOR_INTERVAL = 300   # 5 minutes
GEO_INTERVAL = 900          # 15 minutes


def main():
    logger.info("Convergence runner starting (correlator=%ds, geopolitical=%ds)",
                CORRELATOR_INTERVAL, GEO_INTERVAL)

    last_geo = 0
    last_corr = 0

    # Run both immediately on start
    try:
        logger.info("Initial geopolitical feed collection")
        run_geopolitical()
    except Exception as e:
        logger.error("Geopolitical feed error: %s", e, exc_info=True)
    last_geo = time.time()

    try:
        logger.info("Initial correlation run")
        run_correlator()
    except Exception as e:
        logger.error("Correlator error: %s", e, exc_info=True)
    last_corr = time.time()

    while True:
        time.sleep(30)  # Check every 30s
        now = time.time()

        if now - last_geo >= GEO_INTERVAL:
            try:
                run_geopolitical()
            except Exception as e:
                logger.error("Geopolitical feed error: %s", e, exc_info=True)
            last_geo = now

        if now - last_corr >= CORRELATOR_INTERVAL:
            try:
                run_correlator()
            except Exception as e:
                logger.error("Correlator error: %s", e, exc_info=True)
            last_corr = now


if __name__ == "__main__":
    main()
