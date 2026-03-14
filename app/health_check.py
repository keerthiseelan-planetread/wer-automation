"""Health check module for external service validation."""

import logging
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
        
        # Try to instantiate drive service
        service = get_drive_service()
        
        # Try a simple API call to verify credentials work
        service.files().list(pageSize=1, fields="files(id)").execute()
        
        logger.info("✓ Google Drive credentials valid")
        return True, "Google Drive authentication OK"
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Google Drive credential check failed: {error_msg}")
        return False, f"Google Drive authentication failed: {error_msg[:100]}"


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
    
    # Check MongoDB
    results["MongoDB"] = check_mongodb_connection()
    
    # Check Google Drive
    results["Google Drive"] = check_google_drive_credentials()
    
    # Check Users Configuration
    results["Users Configuration"] = check_allowed_users()
    
    # Summary
    healthy_count = sum(1 for status, _ in results.values() if status)
    total_count = len(results)
    
    logger.info("=" * 70)
    logger.info(f"Health Check Summary: {healthy_count}/{total_count} services OK")
    logger.info("=" * 70)
    
    return results


def format_health_check_results(results: Dict[str, Tuple[bool, str]]) -> str:
    """
    Format health check results for UI display.
    
    Args:
        results: Dictionary of health check results
        
    Returns:
        str: Formatted message for display
    """
    message_lines = []
    
    unhealthy_services = []
    for service, (is_healthy, message) in results.items():
        if not is_healthy:
            unhealthy_services.append(f"• {service}: {message}")
    
    if unhealthy_services:
        message_lines.append("⚠️ **Startup Health Check Issues:**\n")
        message_lines.extend(unhealthy_services)
        message_lines.append("\n**Troubleshooting Steps:**")
        message_lines.append("1. Verify `.env` file has all required variables:")
        message_lines.append("   - GOOGLE_DRIVE_ROOT_ID")
        message_lines.append("   - SERVICE_ACCOUNT_PATH")
        message_lines.append("   - ALLOWED_USERS (format: email:hash,email:hash)")
        message_lines.append("   - MONGODB_URI")
        message_lines.append("2. Check that service account file exists and is valid JSON")
        message_lines.append("3. Verify MongoDB connection string is correct")
        message_lines.append("4. Ensure Google Drive service account has proper permissions")
        
        return "\n".join(message_lines)
    
    return None  # All healthy
