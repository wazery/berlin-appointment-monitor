#!/usr/bin/env python3
"""
Berlin Service Appointment Monitor - Main Entry Point

This script checks for available appointments on the Berlin service website
and sends notifications when appointments become available.
"""

import logging
import sys
import time
from datetime import datetime

from config import Config
from scraper import BerlinServiceScraper
from notifier import NotificationManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/monitor.log', mode='a')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main function to run the appointment monitor."""
    try:
        logger.info("Starting Berlin Service Appointment Monitor")
        
        # Initialize configuration
        config = Config()
        
        # Initialize scraper and notifier
        scraper = BerlinServiceScraper(config)
        notifier = NotificationManager(config)
        
        # Check for appointments
        logger.info("Checking for available appointments...")
        appointments = scraper.check_appointments()
        
        if appointments:
            logger.info(f"Found {len(appointments)} available appointments!")
            
            # Send notifications
            message = scraper.format_appointment_message(appointments)
            notifier.send_notification("🎉 Berlin Service Appointments Available!", message)
            
            logger.info("Notifications sent successfully")
        else:
            logger.info("No appointments currently available")
            
        logger.info("Monitor run completed successfully")
        
    except Exception as e:
        logger.error(f"Error during monitoring: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()