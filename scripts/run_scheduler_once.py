#!/usr/bin/env python3
"""
Standalone scheduler script for GitHub Actions.
Runs the WER automation job once without APScheduler.

Usage: python scripts/run_scheduler_once.py
"""

import sys
import os
import logging
from datetime import datetime

# Add workspace root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_logging():
    """Setup logging for GitHub Actions."""
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
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)


def validate_environment():
    """Validate that all required environment variables are set."""
    logger = logging.getLogger(__name__)
    
    required_vars = [
        'MONGODB_URI',
        'GOOGLE_DRIVE_ROOT_ID',
        'ALLOWED_USERS',
        'SERVICE_ACCOUNT_PATH'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in GitHub Secrets and workflow")
        return False
    
    # Validate service account file
    service_account_path = os.getenv('SERVICE_ACCOUNT_PATH')
    if not os.path.exists(service_account_path):
        logger.error(f"Service account file not found: {service_account_path}")
        return False
    
    logger.info("✓ All environment variables validated")
    return True


def run_automation():
    """Run the WER automation job."""
    logger = logging.getLogger(__name__)
    
    try:
        from app.Services.automation_trigger import run_all_folders
        
        log_separator()
        logger.info("[WER AUTOMATION JOB] Starting")
        logger.info(f"[WER AUTOMATION JOB] Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        logger.info("[WER AUTOMATION JOB] Platform: GitHub Actions")
        log_separator()
        
        # Run automation
        result = run_all_folders()
        
        log_separator()
        logger.info("[WER AUTOMATION JOB] ✓ Completed successfully")
        if result:
            logger.info(f"[WER AUTOMATION JOB] Summary:")
            for key, value in result.items():
                logger.info(f"  • {key}: {value}")
        log_separator()
        
        return True
        
    except Exception as e:
        log_separator()
        logger.error(f"[WER AUTOMATION JOB] ✗ Failed with error:")
        logger.error(f"[WER AUTOMATION JOB] {str(e)}")
        logger.error(f"[WER AUTOMATION JOB] Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        log_separator()
        
        # Print full traceback for debugging
        import traceback
        logger.error("Traceback:")
        logger.error(traceback.format_exc())
        return False


def log_separator():
    """Print a separator line for log visibility."""
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)


def main():
    """Main entry point."""
    logger = setup_logging()
    
    log_separator()
    logger.info("[SCHEDULER] WER Automation - GitHub Actions Edition")
    logger.info(f"[SCHEDULER] Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    log_separator()
    
    # Validate environment
    if not validate_environment():
        logger.error("[SCHEDULER] Environment validation failed. Exiting.")
        sys.exit(1)
    
    # Run automation
    success = run_automation()
    
    # Exit with appropriate code
    exit_code = 0 if success else 1
    logger.info(f"[SCHEDULER] Exiting with code: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
