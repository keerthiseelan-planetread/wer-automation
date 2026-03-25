"""
Entry point for running the scheduler as a module.
Allows: python -m app.Services.scheduler
"""

import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)

# Suppress verbose library logs
logging.getLogger('apscheduler').setLevel(logging.WARNING)
logging.getLogger('google').setLevel(logging.WARNING)
logging.getLogger('googleapiclient').setLevel(logging.WARNING)

from app.Services.scheduler import start_scheduler

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("[SCHEDULER] WER Automation Scheduler - Production Edition")
    logger.info("[SCHEDULER] Environment: Render Background Worker")
    logger.info("=" * 80)
    
    start_scheduler()
