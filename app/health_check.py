"""Health check module for external service validation."""

import logging
import os
import json
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def check_mongodb_connection() -> Tuple[bool, str]:
    """
    Check if MongoDB connection is accessible.
    
    Returns:
        Tuple[bool, str]: (is_healthy, message)
    """
    try:
        from app.config import Config
        from app.database.mongo_connection import get_mongo_client
        
        logger.info("Checking MongoDB connection...")
        client = get_mongo_client(timeout=3000)  # Shorter timeout for health check
        
        # Try to run ping command
        client.admin.command('ping')
        logger.info("✓ MongoDB connection successful")
        return True, "MongoDB connection OK"
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"MongoDB connection failed: {error_msg}")
        return False, f"MongoDB unreachable: {error_msg[:100]}"


def check_google_drive_credentials() -> Tuple[bool, str]:
    """
    Check if Google Drive service account credentials are valid.
    
    Returns:
        Tuple[bool, str]: (is_healthy, message)
    """
    try:
        from app.config import Config
        from app.drive.drive_service import get_drive_service
        
        logger.info("Checking Google Drive credentials...")
        
        # First check if service account file exists
        if not os.path.exists(Config.SERVICE_ACCOUNT_PATH):
            return False, f"❌ Google service account file not found at: {Config.SERVICE_ACCOUNT_PATH}. Please verify the SERVICE_ACCOUNT_PATH in your .env file."
        
        # Check if it's valid JSON
        try:
            with open(Config.SERVICE_ACCOUNT_PATH, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            return False, f"Service account file is not valid JSON: {str(e)}"
        except Exception as e:
            return False, f"Cannot read service account file: {str(e)}"
        
        # Try to instantiate drive service
        service = get_drive_service()
        
        # Try a simple API call to verify credentials work
        service.files().list(pageSize=1, fields="files(id)").execute()
        
        logger.info("✓ Google Drive credentials valid")
        return True, "Google Drive authentication OK"
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Google Drive credential check failed: {error_msg}")
        return False, f"Google Drive connection failed: {error_msg[:100]}"


def check_allowed_users() -> Tuple[bool, str]:
    """
    Check if allowed users are properly configured.
    
    Returns:
        Tuple[bool, str]: (is_healthy, message)
    """
    try:
        from app.config import Config
        
        logger.info("Checking allowed users configuration...")
        users = Config.get_allowed_users()
        
        if not users or len(users) == 0:
            logger.warning("⚠️ No authorized users configured")
            return False, "No users in ALLOWED_USERS"
        
        logger.info(f"✓ Loaded {len(users)} authorized users")
        return True, f"Loaded {len(users)} users OK"
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"User configuration check failed: {error_msg}")
        return False, f"User configuration error: {error_msg[:100]}"


def run_startup_health_checks() -> Dict[str, Tuple[bool, str]]:
    """
    Run all startup health checks and collect results.
    
    Returns:
        Dict: Results keyed by service name with (status, message) tuples
    """
    logger.info("=" * 70)
    logger.info("Running startup health checks...")
    logger.info("=" * 70)
    
    results = {}
    
    # Check MongoDB (non-blocking - has fallback layers)
    results["MongoDB"] = check_mongodb_connection()
    
    # Check Google Drive (warning only - cached data still accessible)
    results["Google Drive"] = check_google_drive_credentials()
    
    # Check Users Configuration (blocking - needed for login)
    results["Users Configuration"] = check_allowed_users()
    
    # Summary
    healthy_count = sum(1 for status, _ in results.values() if status)
    total_count = len(results)
    
    logger.info("=" * 70)
    logger.info(f"Health Check Summary: {healthy_count}/{total_count} services OK")
    logger.info("=" * 70)
    
    return results


def format_health_check_results(results: Dict[str, Tuple[bool, str]]) -> tuple:
    """
    Format health check results for UI display.
    
    Args:
        results: Dictionary of health check results
        
    Returns:
        tuple: (blocking_errors, warning_message)
        
    Blocking: Critical services (Users, cached data accessible)
    Warnings: Degraded services (Drive down, but reports still viewable)
    """
    critical_failures = []
    warnings = []
    
    # MongoDB failures are non-blocking (has fallback layers)
    if "MongoDB" in results and not results["MongoDB"][0]:
        warnings.append(f"⚠️ {results['MongoDB'][1]}")
        warnings.append("   → Using local cache fallback")
    
    # Google Drive failures are now non-blocking (cached data still accessible)
    if "Google Drive" in results and not results["Google Drive"][0]:
        warnings.append(f"⚠️ Drive connection issue: {results['Google Drive'][1]}")
        warnings.append("   → Viewing cached reports only. Unable to generate new reports.")
    
    # Users config failures are blocking (needed for login)
    if "Users Configuration" in results and not results["Users Configuration"][0]:
        critical_failures.append(f"❌ Users: {results['Users Configuration'][1]}")
    
    # Format messages
    critical_message = None
    warning_message = None
    
    if critical_failures:
        critical_message = "❌ **Startup Health Check - Critical Issues:**\n\n"
        critical_message += "\n".join(critical_failures)
        critical_message += "\n\n**Troubleshooting Steps:**\n"
        critical_message += "1. Verify `.env` file has all required variables:\n"
        critical_message += "   - GOOGLE_DRIVE_ROOT_ID\n"
        critical_message += "   - SERVICE_ACCOUNT_PATH\n"
        critical_message += "   - ALLOWED_USERS (format: email:hash,email:hash)\n"
        critical_message += "   - MONGODB_URI\n"
        critical_message += "2. Check that service account file exists and is valid JSON\n"
        critical_message += "3. Ensure Google Drive service account has proper permissions"
    
    if warnings:
        warning_message = "⚠️ **Service Status:**\n\n"
        warning_message += "\n".join(warnings)
    
    return critical_message, warning_message
