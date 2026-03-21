"""Daily WER report automation scheduler using APScheduler."""

import logging
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


def start_scheduler():
    """
    Start the APScheduler for daily WER automation.
    
    The scheduler runs at the configured time (SCHEDULER_TIME in config.py)
    and automatically processes all Google Drive folders, storing results in MongoDB.
    """
    try:
        from app.config import Config
        from app.Services.automation_trigger import run_all_folders
        
        # Get scheduler time from config
        schedule_time = getattr(Config, 'SCHEDULER_TIME', '02:00')
        
        # Parse time (expected format: "HH:MM")
        try:
            hour, minute = map(int, schedule_time.split(':'))
        except ValueError:
            logger.error(f"Invalid SCHEDULER_TIME format: {schedule_time}. Expected 'HH:MM'")
            return
        
        # Initialize scheduler
        scheduler = BackgroundScheduler()
        
        # Register the daily task
        scheduler.add_job(
            func=automation_job_wrapper,
            trigger=CronTrigger(hour=hour, minute=minute),
            id='wer_automation_daily',
            name='Daily WER Report Automation',
            replace_existing=True
        )
        
        # Start scheduler
        scheduler.start()
        logger.info(f"✓ Scheduler started. WER automation scheduled daily at {schedule_time}")
        logger.info(f"Scheduler will run indefinitely. Press Ctrl+C to stop.")
        
        # Keep scheduler running
        try:
            while True:
                pass
        except KeyboardInterrupt:
            logger.info("Scheduler interrupted by user")
            scheduler.shutdown()
    
    except ImportError as e:
        logger.error(f"Failed to import required modules: {str(e)}")
        logger.error("Make sure APScheduler is installed: pip install APScheduler")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")


def automation_job_wrapper():
    """
    Wrapper function that gets called by APScheduler at scheduled time.
    Handles logging and error management for the automation job.
    """
    try:
        from app.Services.automation_trigger import run_all_folders
        
        logger.info("=" * 60)
        logger.info(f"[WER AUTOMATION] Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # Run the automation
        result = run_all_folders()
        
        logger.info("=" * 60)
        logger.info(f"[WER AUTOMATION] Completed successfully")
        logger.info(f"Summary: {result}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"[WER AUTOMATION ERROR] {str(e)}")
        logger.error("=" * 60)
        raise


if __name__ == "__main__":
    # Setup logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    start_scheduler()
