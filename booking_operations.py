"""Booking operations module with refactored functions."""

import datetime
import time
from typing import Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from config import (
    config, SITE_TO_CHECKBOX_MAP, COURT_NAME_MAP, 
    DEFAULT_FORM_DATA, get_court_order
)
from utils import (
    setup_logging, retry_on_exception, safe_wait_and_click,
    safe_wait_and_send_keys, safe_wait_for_element,
    get_eastern_time, get_eastern_date_string,
    LoginError, CourtUnavailableError
)

logger = setup_logging(__name__)

class BookingOperations:
    """Handles all booking-related operations."""
    
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        
    @retry_on_exception(max_retries=2)
    def login(self, email: str, password: str) -> None:
        """Login to the booking system."""
        try:
            self.driver.get(config.LOGIN_URL)
            
            if not safe_wait_and_send_keys(
                self.driver, (By.ID, 'loginEmail'), email, config.LOGIN_TIMEOUT
            ):
                raise LoginError("Failed to enter email")
                
            if not safe_wait_and_send_keys(
                self.driver, (By.ID, 'loginPassword'), password, config.LOGIN_TIMEOUT
            ):
                raise LoginError("Failed to enter password")
                
            if not safe_wait_and_click(
                self.driver, (By.XPATH, '//button[@tabindex="3"]'), config.LOGIN_TIMEOUT
            ):
                raise LoginError("Failed to click login button")
                
            logger.info(f"Login successful for {email}")
            
        except Exception as e:
            logger.error(f"Login failed for {email}: {e}")
            raise LoginError(f"Login failed: {e}")
    
    def navigate_to_new_permit_request(self) -> None:
        """Navigate to new permit request page."""
        if not safe_wait_and_click(
            self.driver, (By.LINK_TEXT, "New Permit Request"), config.ELEMENT_TIMEOUT
        ):
            raise Exception("Failed to navigate to new permit request")
        logger.info("Navigated to new permit request page")
    
    def select_site_and_checkbox(self, site_id: str) -> None:
        """Select site and corresponding checkbox."""
        try:
            # Select the site
            site_select_element = safe_wait_for_element(
                self.driver, (By.ID, 'site'), config.ELEMENT_TIMEOUT
            )
            if not site_select_element:
                raise Exception("Site selection element not found")
                
            site_select = Select(site_select_element)
            site_select.select_by_value(site_id)
            
            # Wait for site description to update
            initial_text = self.driver.find_element(By.ID, "siteDescription").text
            WebDriverWait(self.driver, config.ELEMENT_TIMEOUT).until(
                lambda driver: driver.find_element(By.ID, "siteDescription").text != initial_text
            )
            
            # Click add facility set button
            if not safe_wait_and_click(
                self.driver, (By.ID, "addFacilitySet"), config.ELEMENT_TIMEOUT
            ):
                raise Exception("Failed to click add facility set button")
            
            # Click checkbox
            checkbox_id = SITE_TO_CHECKBOX_MAP[site_id]
            if not safe_wait_and_click(
                self.driver, (By.ID, checkbox_id), config.ELEMENT_TIMEOUT
            ):
                raise Exception(f"Failed to click checkbox {checkbox_id}")
                
            logger.info(f"Selected site {site_id} and checkbox {checkbox_id}")
            
        except Exception as e:
            logger.error(f"Failed to select site {site_id}: {e}")
            raise
    
    def select_date_and_time(self, selected_time: str, relative_days: int) -> None:
        """Select date and time for booking."""
        try:
            target_date = get_eastern_time() + datetime.timedelta(days=relative_days)
            target_day = str(target_date.day)
            target_month = target_date.strftime('%B')
            target_year = target_date.year
            
            # Click date picker
            if not safe_wait_and_click(
                self.driver, (By.ID, 'event0'), config.ELEMENT_TIMEOUT
            ):
                raise Exception("Failed to open date picker")
            
            # Wait for date picker to be visible
            WebDriverWait(self.driver, config.ELEMENT_TIMEOUT).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "ui-datepicker"))
            )
            
            # Navigate to correct month/year
            self._navigate_to_date(target_month, target_year, target_day)
            
            # Select time
            self._select_time(selected_time)
            
            logger.info(f"Selected date {target_date.strftime('%Y-%m-%d')} and time {selected_time}")
            
        except Exception as e:
            logger.error(f"Failed to select date and time: {e}")
            raise
    
    def _navigate_to_date(self, target_month: str, target_year: int, target_day: str) -> None:
        """Navigate to the target date in date picker."""
        while True:
            headers = self.driver.find_elements(By.CLASS_NAME, "ui-datepicker-title")
            found = False
            
            for header in headers:
                month_text, year = header.text.split()
                year = int(year)
                
                if year == target_year and month_text == target_month:
                    day_element = self.driver.find_element(By.XPATH, f'//a[text()="{target_day}"]')
                    day_element.click()
                    found = True
                    break
            
            if found:
                break
            else:
                next_button = WebDriverWait(self.driver, config.ELEMENT_TIMEOUT).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "ui-datepicker-next"))
                )
                next_button.click()
                WebDriverWait(self.driver, config.ELEMENT_TIMEOUT).until(
                    EC.staleness_of(headers[0])
                )
    
    def _select_time(self, selected_time: str) -> None:
        """Select start and end time."""
        start_hour_element = safe_wait_for_element(
            self.driver, (By.NAME, "startHour"), config.ELEMENT_TIMEOUT
        )
        if not start_hour_element:
            raise Exception("Start hour element not found")
            
        end_hour_element = safe_wait_for_element(
            self.driver, (By.NAME, "endHour"), config.ELEMENT_TIMEOUT
        )
        if not end_hour_element:
            raise Exception("End hour element not found")
        
        Select(start_hour_element).select_by_value(selected_time)
        Select(end_hour_element).select_by_value(str((int(selected_time) + 1) % 24))
    
    def book_court(self) -> None:
        """Attempt to book the court."""
        if not safe_wait_and_click(
            self.driver, (By.XPATH, '//button[text()="Add & Confirm"]'), config.ELEMENT_TIMEOUT
        ):
            raise Exception("Failed to click Add & Confirm button")
        logger.info("Clicked Add & Confirm button")
    
    def check_error_message(self) -> bool:
        """Check if booking failed due to unavailability."""
        try:
            WebDriverWait(self.driver, config.SHORT_TIMEOUT).until(
                EC.visibility_of_element_located((
                    By.XPATH, 
                    "//label[@class='error' and contains(text(), 'The selected facilities are not available for the above date and time.')]"
                ))
            )
            return True
        except TimeoutException:
            return False
    
    def try_booking_alternative_courts(self, selected_time: str, email: str, relative_days: int) -> str:
        """Try booking alternative courts in priority order."""
        court_ids = get_court_order(selected_time)
        
        for court_id in court_ids:
            try:
                court_name = COURT_NAME_MAP[court_id]
                logger.info(f"Trying to book {court_name}")
                
                # Select alternative court
                site_select_element = safe_wait_for_element(
                    self.driver, (By.ID, 'site'), config.ELEMENT_TIMEOUT
                )
                if site_select_element:
                    Select(site_select_element).select_by_value(court_id)
                    
                    checkbox_id = SITE_TO_CHECKBOX_MAP[court_id]
                    if safe_wait_and_click(
                        self.driver, (By.ID, checkbox_id), config.SHORT_TIMEOUT
                    ):
                        if safe_wait_and_click(
                            self.driver, (By.XPATH, '//button[text()="Add & Confirm"]'), config.SHORT_TIMEOUT
                        ):
                            # Check if booking succeeded
                            if WebDriverWait(self.driver, 2, 0.1).until(
                                EC.invisibility_of_element_located((By.XPATH, '//button[text()="Add & Confirm"]'))
                            ):
                                return f"Booking successful for {court_name} under account {email} for time {selected_time} on day {relative_days}."
                            
            except Exception as e:
                logger.warning(f"Failed to book {court_name}: {e}")
                continue
                
        return f"Booking failed under account {email} for time {selected_time} on day {relative_days}."
    
    def fill_additional_details(self) -> None:
        """Fill in additional booking details."""
        try:
            # Fill input fields
            for input_id, value in DEFAULT_FORM_DATA['input_data'].items():
                if not safe_wait_and_send_keys(
                    self.driver, (By.ID, input_id), value, config.ELEMENT_TIMEOUT
                ):
                    logger.warning(f"Failed to fill input field {input_id}")
            
            # Fill select fields
            for select_id, value in DEFAULT_FORM_DATA['select_data'].items():
                try:
                    select_element = safe_wait_for_element(
                        self.driver, (By.ID, select_id), config.ELEMENT_TIMEOUT
                    )
                    if select_element:
                        Select(select_element).select_by_visible_text(value)
                except Exception as e:
                    logger.warning(f"Failed to select value for {select_id}: {e}")
            
            # Accept terms
            if not safe_wait_and_click(
                self.driver, (By.ID, 'acceptTerms'), config.ELEMENT_TIMEOUT
            ):
                logger.warning("Failed to click accept terms")
                
            logger.info("Additional details filled successfully")
            
        except Exception as e:
            logger.error(f"Failed to fill additional details: {e}")
            raise
    
    def submit_form(self) -> None:
        """Submit the booking form."""
        if not safe_wait_and_click(
            self.driver, (By.XPATH, '//button[text()="Submit"]'), config.ELEMENT_TIMEOUT
        ):
            raise Exception("Failed to submit form")
        logger.info("Form submitted successfully")
    
    def wait_until_booking_time(self) -> None:
        """Wait until the configured booking time."""
        now = get_eastern_time()
        target_time = now.replace(hour=config.WAIT_UNTIL_HOUR, minute=0, second=0, microsecond=0)
        
        if now < target_time:
            wait_seconds = (target_time - now).total_seconds()
            logger.info(f"Waiting {wait_seconds} seconds until {config.WAIT_UNTIL_HOUR}:00 AM")
            time.sleep(wait_seconds)
        else:
            logger.info("Already past booking time, proceeding immediately")