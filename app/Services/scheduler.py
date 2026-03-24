"""Daily WER report automation scheduler using APScheduler."""

import logging
import os
import signal
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler_instance = None
shutdown_event = False


def signal_handler(signum, frame):
    """Handle graceful shutdown on SIGTERM/SIGINT."""
    global shutdown_event
    log_separator()
    logger.info(f"[SCHEDULER] Received signal {signum}. Starting graceful shutdown...")
    log_separator()
    shutdown_event = True
    
    if scheduler_instance and scheduler_instance.running:
        scheduler_instance.shutdown(wait=True)
        logger.info("[SCHEDULER] Scheduler shut down successfully")


def log_separator():
    """Print a separator line for log visibility."""
    logger.info("=" * 80)


def start_scheduler():
    """
    Start the APScheduler for daily WER automation.
    
    The scheduler runs at the configured time (SCHEDULER_TIME in config.py)
    and automatically processes all Google Drive folders, storing results in MongoDB.
    
    Designed for Render background workers with graceful shutdown handling.
    """
    global scheduler_instance
    
    try:
        from app.config import Config
        from app.Services.automation_trigger import run_all_folders
        
        # Validate environment
        try:
            Config.validate()
        except ValueError as e:
            logger.error(f"[SCHEDULER] Configuration validation failed: {str(e)}")
            return
        
        # Get scheduler time from config
        schedule_time = getattr(Config, 'SCHEDULER_TIME', '02:00')
        scheduler_timezone = getattr(Config, 'SCHEDULER_TIMEZONE', 'UTC')
        
        # Parse time (expected format: "HH:MM")
        try:
            hour, minute = map(int, schedule_time.split(':'))
        except ValueError:
            logger.error(f"[SCHEDULER] Invalid SCHEDULER_TIME format: {schedule_time}. Expected 'HH:MM'")
            return
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        log_separator()
        logger.info("[SCHEDULER] Initializing APScheduler for Render production...")
        log_separator()
        
        # Initialize scheduler with production settings
        scheduler_instance = BackgroundScheduler(
            daemon=False,  # Don't run as daemon - we handle shutdown ourselves
            timezone=scheduler_timezone
        )
        
        # Register the daily task
        scheduler_instance.add_job(
            func=automation_job_wrapper,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=scheduler_timezone),
            id='wer_automation_daily',
            name='Daily WER Report Automation',
            replace_existing=True,
            coalesce=True,  # Skip missed jobs if scheduler was down
            max_instances=1  # Only one instance at a time
        )
        
        # Start scheduler
        scheduler_instance.start()
        log_separator()
        logger.info(f"✓ [SCHEDULER] Started successfully!")
        logger.info(f"  • Time: Daily at {schedule_time} ({scheduler_timezone})")
        logger.info(f"  • Job: Daily WER Report Automation")
        logger.info(f"  • Status: Running with graceful shutdown handling")
        log_separator()
        
        # Keep scheduler running - handle graceful shutdown
        try:
            while not shutdown_event:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("[SCHEDULER] Interrupted by user")
            signal_handler(signal.SIGINT, None)
    
    except ImportError as e:
        logger.error(f"[SCHEDULER] Failed to import required modules: {str(e)}")
        logger.error("[SCHEDULER] Make sure APScheduler is installed: pip install APScheduler")
    except Exception as e:
        log_separator()
        logger.error(f"[SCHEDULER] Failed to start scheduler: {str(e)}")
        log_separator()
        raise


def automation_job_wrapper():
    """
    Wrapper function that gets called by APScheduler at scheduled time.
    Handles logging and error management for the automation job.
    """
    try:
        from app.Services.automation_trigger import run_all_folders
        
        log_separator()
        logger.info(f"[WER AUTOMATION] Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"[WER AUTOMATION] Processing all Google Drive folders...")
        log_separator()
        
        # Run the automation
        result = run_all_folders()
        
        log_separator()
        logger.info(f"[WER AUTOMATION] ✓ Completed successfully")
        if result:
            logger.info(f"[WER AUTOMATION] Summary: {result}")
        log_separator()
        
        return result
        
    except Exception as e:
        log_separator()
        logger.error(f"[WER AUTOMATION ERROR] {str(e)}")
        logger.error(f"[WER AUTOMATION ERROR] Automation job failed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log_separator()
        # Don't re-raise - allow scheduler to continue


if __name__ == "__main__":
    # Setup logging for production execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Output to console (Render logs)
        ]
    )
    
    # Suppress verbose logs from libraries
    logging.getLogger('apscheduler').setLevel(logging.WARNING)
    logging.getLogger('google').setLevel(logging.WARNING)
    logging.getLogger('googleapiclient').setLevel(logging.WARNING)
    
    log_separator()
    logger.info("[SCHEDULER] WER Automation Scheduler - Production Edition")
    logger.info("[SCHEDULER] Environment: Render Background Worker")
    log_separator()
    
    start_scheduler()
