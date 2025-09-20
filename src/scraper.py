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
            logger.info(f"Fetching main page: {self.base_url}")
            
            # Add random delay to avoid being blocked
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Successfully fetched main page (status: {response.status_code})")
            
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # First, check if we need to select a location (Standort)
            locations = self._find_available_locations(soup)
            
            if locations:
                logger.info(f"Found {len(locations)} specific locations to check")
                return self._check_locations_for_appointments(locations)
            else:
                # No specific locations found, check the main page directly
                # This could happen if the appointment selection is on the same page
                logger.info("No specific locations found, checking main page for appointments")
                return self._parse_appointments(soup)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while fetching appointments: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error checking appointments: {str(e)}")
            return []
    
    def _find_available_locations(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Find available Standesamt locations that can be selected.
        
        Args:
            soup: BeautifulSoup object of the main page
            
        Returns:
            List of location dictionaries with names and URLs
        """
        locations = []
        
        try:
            # Look specifically for appointment booking links for Standesamt locations
            # These often have patterns like "Termin buchen" or "Terminvereinbarung" in the URL
            
            appointment_links = soup.find_all('a', href=True)
            
            for link in appointment_links:
                href = link.get('href')
                link_text = link.get_text().strip()
                
                # Skip if no meaningful text
                if not link_text or len(link_text) < 5:
                    continue
                
                # Skip email links and generic navigation
                if '@' in href or 'mailto:' in href:
                    continue
                    
                # Skip generic navigation links
                if any(skip in link_text.lower() for skip in ['standorte a-z', 'nach behörden', 'weitere standorte']):
                    continue
                
                # Look for actual Standesamt location names or appointment booking links
                is_standesamt_location = any([
                    'standesamt' in link_text.lower() and any(district in link_text.lower() for district in [
                        'marzahn', 'hellersdorf', 'spandau', 'mitte', 'charlottenburg', 'wilmersdorf',
                        'tempelhof', 'schöneberg', 'neukölln', 'friedrichshain', 'kreuzberg',
                        'pankow', 'lichtenberg', 'reinickendorf', 'steglitz', 'zehlendorf', 'treptow'
                    ]),
                    ('termin' in href.lower() and 'standesamt' in link_text.lower()),
                    ('buchung' in href.lower() and 'standesamt' in link_text.lower()),
                    href.startswith('/terminvereinbarung/') and 'standesamt' in link_text.lower()
                ])
                
                if is_standesamt_location:
                    full_url = href if href.startswith('http') else f"https://service.berlin.de{href}"
                    
                    locations.append({
                        'name': link_text,
                        'url': full_url
                    })
                    
                    logger.info(f"Found Standesamt location: {link_text}")
            
            # If no specific location links found, look for form-based location selection
            if not locations:
                # Look for select elements with Standesamt options
                select_elements = soup.find_all('select')
                
                for select in select_elements:
                    options = select.find_all('option', value=True)
                    
                    for option in options:
                        option_text = option.get_text().strip()
                        option_value = option.get('value')
                        
                        # Skip empty or placeholder options
                        if not option_value or option_value == '' or 'wählen' in option_text.lower():
                            continue
                        
                        # Look for Standesamt in option text
                        if 'standesamt' in option_text.lower():
                            locations.append({
                                'name': option_text,
                                'url': None,  # Form-based, will need special handling
                                'value': option_value,
                                'form_based': True
                            })
                            
                            logger.info(f"Found Standesamt option: {option_text}")
            
            # If still no locations, this might be a page that needs direct form interaction
            # Look for specific buttons or form elements that suggest appointment booking
            if not locations:
                booking_forms = soup.find_all('form')
                for form in booking_forms:
                    form_text = form.get_text().lower()
                    if 'termin' in form_text and 'standesamt' in form_text:
                        logger.info("Found appointment form that may require direct interaction")
                        # For now, we'll fall back to checking the main page
                        break
            
        except Exception as e:
            logger.error(f"Error finding locations: {str(e)}")
        
        # Log what we found
        if locations:
            logger.info(f"Total locations to check: {len(locations)}")
        else:
            logger.info("No specific Standesamt locations found, will check main page")
        
        return locations
    
    def _check_locations_for_appointments(self, locations: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Check each location for available appointments.
        
        Args:
            locations: List of location dictionaries
            
        Returns:
            List of available appointments across all locations
        """
        all_appointments = []
        
        for location in locations[:5]:  # Limit to first 5 locations to avoid too many requests
            try:
                location_name = location['name']
                location_url = location.get('url')
                
                if not location_url:
                    logger.info(f"Skipping {location_name} - no direct URL available")
                    continue
                
                logger.info(f"Checking appointments for: {location_name}")
                
                # Add delay between requests
                time.sleep(random.uniform(2, 4))
                
                response = self.session.get(location_url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                appointments = self._parse_appointments(soup, location_name)
                
                if appointments:
                    logger.info(f"✅ Found {len(appointments)} appointments at {location_name}")
                    all_appointments.extend(appointments)
                else:
                    logger.info(f"❌ No appointments at {location_name}")
                    
            except Exception as e:
                logger.error(f"Error checking {location.get('name', 'unknown')}: {str(e)}")
                continue
        
        return all_appointments
    
    def _parse_appointments(self, soup: BeautifulSoup, location_name: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Parse the HTML content to find available appointments.
        
        Args:
            soup: BeautifulSoup object of the page content
            location_name: Name of the location being checked (optional)
            
        Returns:
            List of appointment dictionaries
        """
        appointments = []
        location_info = f" at {location_name}" if location_name else ""
        
        try:
            # Look for explicit "no appointments" messages
            no_appointments_indicators = [
                'keine termine', 'no appointments', 'ausgebucht', 'nicht verfügbar',
                'derzeit keine termine', 'currently no appointments',
                'alle termine vergeben', 'all appointments taken',
                'keine verfügbaren termine', 'no available appointments',
                'keine freien termine', 'no free appointments'
            ]
            
            page_text = soup.get_text().lower()
            
            for indicator in no_appointments_indicators:
                if indicator in page_text:
                    logger.info(f"Found 'no appointments' indicator{location_info}: '{indicator}'")
                    return []
            
            # Look for ENABLED booking buttons (not disabled)
            enabled_booking_buttons = soup.find_all(['button', 'a'], 
                class_=lambda x: x and not any('disabled' in str(c).lower() for c in (x if isinstance(x, list) else [x])),
                string=lambda text: text and any(
                    keyword in text.lower() for keyword in ['termin buchen', 'book appointment', 'termin vereinbaren', 'buchen']
                )
            )
            
            # Look for calendar/date picker elements
            calendar_elements = soup.find_all(['input'], attrs={
                'type': ['date', 'datetime-local'],
                'class': lambda x: x and 'calendar' in str(x).lower()
            })
            
            # Look for time slot buttons/links that are clickable and enabled
            time_slot_elements = soup.find_all(['button', 'a'], 
                class_=lambda x: x and not any('disabled' in str(c).lower() for c in (x if isinstance(x, list) else [x])),
                string=lambda text: text and text.strip() and (
                    # Time patterns like "09:00", "14:30"
                    ':' in text and len(text.strip()) <= 10 and 
                    any(char.isdigit() for char in text)
                )
            )
            
            # Look for explicit availability confirmation text
            positive_availability = soup.find_all(string=lambda text: text and any(
                phrase in text.lower() for phrase in [
                    'termine verfügbar', 'appointments available',
                    'freie termine', 'free appointments',
                    'buchbare termine', 'bookable appointments',
                    'termin wählen', 'choose appointment',
                    'verfügbare zeiten', 'available times'
                ]
            ))
            
            # Look for date/time selection forms
            date_selects = soup.find_all(['select'], attrs={
                'name': lambda x: x and any(keyword in x.lower() for keyword in ['date', 'time', 'termin'])
            })
            
            # Count meaningful indicators
            meaningful_indicators = (
                len(enabled_booking_buttons) + 
                len(calendar_elements) + 
                len(time_slot_elements) + 
                len(positive_availability) +
                len(date_selects)
            )
            
            logger.info(f"Appointment check{location_info}:")
            logger.info(f"  - {len(enabled_booking_buttons)} enabled booking buttons")
            logger.info(f"  - {len(calendar_elements)} calendar elements")
            logger.info(f"  - {len(time_slot_elements)} time slot elements")
            logger.info(f"  - {len(positive_availability)} positive availability texts")
            logger.info(f"  - {len(date_selects)} date/time selects")
            logger.info(f"  - Total meaningful indicators: {meaningful_indicators}")
            
            # Check for disabled buttons that would indicate the location selection step
            disabled_booking_buttons = soup.find_all(['button'], 
                class_=lambda x: x and any('disabled' in str(c).lower() for c in (x if isinstance(x, list) else [x])),
                string=lambda text: text and 'termin' in text.lower()
            )
            
            if disabled_booking_buttons and not location_name:
                logger.info("Found disabled booking button on main page - location selection required")
                return []
            
            # Report appointments if we have good evidence
            if meaningful_indicators >= 1:  # Lower threshold since we're checking specific locations
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                appointment_data = {
                    'type': 'Berlin Service Appointment',
                    'url': self.base_url,
                    'found_at': current_time,
                    'details': f"Appointment availability detected{location_info} (indicators: {meaningful_indicators})",
                    'enabled_buttons': len(enabled_booking_buttons),
                    'calendar_elements': len(calendar_elements),
                    'time_slots': len(time_slot_elements),
                    'availability_texts': len(positive_availability),
                    'date_selects': len(date_selects)
                }
                
                if location_name:
                    appointment_data['location'] = location_name
                
                appointments.append(appointment_data)
                
                logger.info(f"✅ Confirmed appointment availability{location_info}!")
            else:
                logger.info(f"❌ No appointment availability detected{location_info}")
            
        except Exception as e:
            logger.error(f"Error parsing appointment content{location_info}: {str(e)}")
        
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
                f"📍 Appointment {i}:",
                f"  Type: {apt.get('type', 'Unknown')}",
                f"  Location: {apt.get('location', 'Main page')}"
            ])
            
            if apt.get('location'):
                message_lines.append(f"  🏢 Standesamt: {apt.get('location')}")
            
            message_lines.extend([
                f"  🔗 URL: {apt.get('url', 'N/A')}",
                f"  ⏰ Found at: {apt.get('found_at', 'N/A')}",
                f"  📊 Indicators: {apt.get('details', 'N/A')}",
                ""
            ])
            
            # Add technical details
            if apt.get('enabled_buttons', 0) > 0:
                message_lines.append(f"  ✅ {apt.get('enabled_buttons')} enabled booking buttons")
            if apt.get('time_slots', 0) > 0:
                message_lines.append(f"  🕐 {apt.get('time_slots')} time slots available")
            if apt.get('calendar_elements', 0) > 0:
                message_lines.append(f"  📅 {apt.get('calendar_elements')} calendar elements")
            if apt.get('date_selects', 0) > 0:
                message_lines.append(f"  📝 {apt.get('date_selects')} date selection forms")
            
            message_lines.append("")
        
        message_lines.extend([
            "🚀 **Action Required:**",
            "1. Click the link above",
            "2. Select your preferred Standesamt location",
            "3. Choose an available appointment slot",
            "4. Complete the booking process",
            "",
            "📍 **Available Locations May Include:**",
            "- Standesamt Marzahn-Hellersdorf",
            "- Standesamt Spandau", 
            "- Other Berlin Standesamt offices",
            "",
            f"🔍 **Monitoring Details:**",
            f"- Service: Namensrechtliche Erklärung", 
            f"- Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"- Direct link: {self.base_url}",
            "",
            "⚡ **Note:** Book quickly as appointments fill up fast!"
        ])
        
        return "\n".join(message_lines)