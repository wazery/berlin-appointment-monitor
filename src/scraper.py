"""
Berlin Service Website Scraper

This module handles scraping the Berlin service website for appointment availability.
"""

import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import time
import random

logger = logging.getLogger(__name__)


class BerlinServiceScraper:
    """Scrapes the Berlin service website for appointment availability."""
    
    def __init__(self, config):
        self.config = config
        self.base_url = "https://service.berlin.de/dienstleistung/324591/"
        self.session = requests.Session()
        
        # Set up headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def check_appointments(self) -> List[Dict[str, str]]:
        """
        Check for available appointments on the Berlin service website.
        
        Returns:
            List of available appointment slots with details
        """
        try:
            logger.info(f"Fetching page: {self.base_url}")
            
            # Add random delay to avoid being blocked
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Successfully fetched page (status: {response.status_code})")
            
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for appointment availability indicators
            appointments = self._parse_appointments(soup)
            
            return appointments
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while fetching appointments: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error parsing appointments: {str(e)}")
            return []
    
    def _parse_appointments(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Parse the HTML content to find available appointments.
        
        Args:
            soup: BeautifulSoup object of the page content
            
        Returns:
            List of appointment dictionaries
        """
        appointments = []
        
        try:
            # Look for common appointment availability indicators
            # This might need to be adjusted based on the actual website structure
            
            # Check for "Termin buchen" or similar booking buttons
            booking_buttons = soup.find_all(['a', 'button'], text=lambda text: text and any(
                keyword in text.lower() for keyword in ['termin', 'buchen', 'book', 'appointment']
            ))
            
            # Check for calendar or date elements
            date_elements = soup.find_all(['div', 'span', 'td'], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['date', 'calendar', 'available', 'free']
            ))
            
            # Check for specific availability text
            availability_text = soup.find_all(text=lambda text: text and any(
                keyword in text.lower() for keyword in [
                    'verfügbar', 'available', 'frei', 'free', 'buchbar', 'bookable'
                ]
            ))
            
            # Log what we found for debugging
            logger.info(f"Found {len(booking_buttons)} booking buttons")
            logger.info(f"Found {len(date_elements)} date elements")
            logger.info(f"Found {len(availability_text)} availability indicators")
            
            # If we find any indicators of availability, consider it an appointment
            if booking_buttons or (date_elements and availability_text):
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                appointments.append({
                    'type': 'Berlin Service Appointment',
                    'url': self.base_url,
                    'found_at': current_time,
                    'details': f"Appointment availability detected on page"
                })
                
                logger.info("Appointment availability detected!")
            else:
                logger.info("No appointment availability detected")
                
                # Log page title and key content for debugging
                title = soup.find('title')
                if title:
                    logger.debug(f"Page title: {title.get_text().strip()}")
                
                # Look for "no appointments" messages
                no_appointments = soup.find_all(text=lambda text: text and any(
                    keyword in text.lower() for keyword in [
                        'keine termine', 'no appointments', 'ausgebucht', 'nicht verfügbar'
                    ]
                ))
                
                if no_appointments:
                    logger.info("Found 'no appointments' indicator")
            
        except Exception as e:
            logger.error(f"Error parsing appointment content: {str(e)}")
        
        return appointments
    
    def format_appointment_message(self, appointments: List[Dict[str, str]]) -> str:
        """
        Format appointment information into a notification message.
        
        Args:
            appointments: List of appointment dictionaries
            
        Returns:
            Formatted message string
        """
        if not appointments:
            return "No appointments found."
        
        message_lines = [
            "🎉 Berlin Service Appointments Available!",
            "",
            f"Found {len(appointments)} available appointment(s):",
            ""
        ]
        
        for i, apt in enumerate(appointments, 1):
            message_lines.extend([
                f"Appointment {i}:",
                f"  Type: {apt.get('type', 'Unknown')}",
                f"  URL: {apt.get('url', 'N/A')}",
                f"  Found at: {apt.get('found_at', 'N/A')}",
                f"  Details: {apt.get('details', 'N/A')}",
                ""
            ])
        
        message_lines.extend([
            "🚀 Book your appointment quickly!",
            f"Direct link: {self.base_url}",
            "",
            f"Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ])
        
        return "\n".join(message_lines)