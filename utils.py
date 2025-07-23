"""Utility functions for tennis court booking system."""

import time
import logging
import functools
import datetime
from contextlib import contextmanager
from typing import Any, Callable, Optional, Generator
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from config import config, EASTERN_TZ

def get_eastern_time() -> datetime.datetime:
    """Get current time in US Eastern timezone."""
    return datetime.datetime.now(EASTERN_TZ)

def get_eastern_date_string(days_offset: int = 0) -> str:
    """Get date string in Eastern timezone with optional offset."""
    target_date = get_eastern_time() + datetime.timedelta(days=days_offset)
    return target_date.strftime('%Y-%m-%d')

def setup_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    """Set up consistent logging across modules."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s EST - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def retry_on_exception(max_retries: int = None, delay: float = None, 
                      exceptions: tuple = (Exception,)):
    """Decorator to retry function on specified exceptions."""
    if max_retries is None:
        max_retries = config.MAX_RETRIES
    if delay is None:
        delay = config.RETRY_DELAY
        
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed. Last error: {e}")
                        
            raise last_exception
        return wrapper
    return decorator

@contextmanager
def managed_webdriver(headless: bool = False) -> Generator[webdriver.Chrome, None, None]:
    """Context manager for WebDriver with proper resource cleanup."""
    driver = None
    logger = setup_logging(__name__)
    
    try:
        # Suppress ChromeDriverManager logging
        logging.getLogger('WDM').setLevel(logging.CRITICAL)
        
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        
        if headless:
            options.add_argument("--headless")
            
        for option in config.CHROME_OPTIONS:
            options.add_argument(option)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
        
        # Restore logging level
        logging.getLogger('WDM').setLevel(logging.INFO)
        
        logger.info("WebDriver initialized successfully")
        yield driver
        
    except Exception as e:
        logger.error(f"Error initializing WebDriver: {e}")
        raise
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")

def safe_wait_and_click(driver: webdriver.Chrome, locator: tuple, 
                       timeout: int = None) -> bool:
    """Safely wait for element and click with error handling."""
    if timeout is None:
        timeout = config.ELEMENT_TIMEOUT
        
    logger = setup_logging(__name__)
    
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
        element.click()
        return True
    except TimeoutException:
        logger.error(f"Timeout waiting for clickable element: {locator}")
        return False
    except Exception as e:
        logger.error(f"Error clicking element {locator}: {e}")
        return False

def safe_wait_and_send_keys(driver: webdriver.Chrome, locator: tuple, 
                           text: str, timeout: int = None) -> bool:
    """Safely wait for element and send keys with error handling."""
    if timeout is None:
        timeout = config.ELEMENT_TIMEOUT
        
    logger = setup_logging(__name__)
    
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
        element.clear()
        element.send_keys(text)
        return True
    except TimeoutException:
        logger.error(f"Timeout waiting for element: {locator}")
        return False
    except Exception as e:
        logger.error(f"Error sending keys to element {locator}: {e}")
        return False

def safe_wait_for_element(driver: webdriver.Chrome, locator: tuple, 
                         timeout: int = None) -> Optional[Any]:
    """Safely wait for element with error handling."""
    if timeout is None:
        timeout = config.ELEMENT_TIMEOUT
        
    logger = setup_logging(__name__)
    
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
    except TimeoutException:
        logger.error(f"Timeout waiting for element: {locator}")
        return None
    except Exception as e:
        logger.error(f"Error waiting for element {locator}: {e}")
        return None

class BookingError(Exception):
    """Custom exception for booking-related errors."""
    pass

class LoginError(BookingError):
    """Exception raised when login fails."""
    pass

class CourtUnavailableError(BookingError):
    """Exception raised when court is unavailable."""
    pass