"""Utility functions for tennis court booking system."""

import time
import logging
import functools
import datetime
from contextlib import contextmanager
from typing import Any, Callable, Optional, Generator, Dict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from .config import config, EASTERN_TZ

def get_eastern_time() -> datetime.datetime:
    """Get current time in US Eastern timezone."""
    return datetime.datetime.now(EASTERN_TZ)

def get_eastern_date_string(days_offset: int = 0) -> str:
    """Get date string in Eastern timezone with optional offset."""
    target_date = get_eastern_time() + datetime.timedelta(days=days_offset)
    return target_date.strftime('%Y-%m-%d')

# Performance timing utilities
class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str, logger: Optional[logging.Logger] = None):
        self.operation_name = operation_name
        self.logger = logger or setup_logging(__name__)
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"Starting {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        if exc_type is None:
            self.logger.info(f"✅ {self.operation_name} completed in {duration:.2f}s")
        else:
            self.logger.error(f"❌ {self.operation_name} failed after {duration:.2f}s: {exc_val}")
    
    @property
    def duration(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

def timed_operation(operation_name: str):
    """Decorator to time function execution."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = setup_logging(func.__module__)
            with PerformanceTimer(f"{operation_name} ({func.__name__})", logger):
                return func(*args, **kwargs)
        return wrapper
    return decorator

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

def fast_element_interaction(driver: webdriver.Chrome, locator: tuple, 
                           action: str, value: str = None, timeout: int = None) -> bool:
    """Fast element interaction using JavaScript when possible."""
    if timeout is None:
        timeout = config.FAST_TIMEOUT
        
    logger = setup_logging(__name__)
    
    try:
        # Try JavaScript first for speed
        element_id = locator[1] if locator[0] == "id" else None
        
        if element_id and action == "click":
            driver.execute_script(f"document.getElementById('{element_id}').click();")
            return True
        elif element_id and action == "send_keys" and value:
            driver.execute_script(f"document.getElementById('{element_id}').value = '{value}';")
            return True
        else:
            # Fallback to regular Selenium (support simple string aliases)
            by = locator[0]
            if isinstance(by, str):
                by_lower = by.lower()
                if by_lower == 'link_text':
                    locator = (By.LINK_TEXT, locator[1])
                elif by_lower == 'css' or by_lower == 'css_selector':
                    locator = (By.CSS_SELECTOR, locator[1])
                elif by_lower == 'xpath':
                    locator = (By.XPATH, locator[1])
                elif by_lower == 'id':
                    locator = (By.ID, locator[1])
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(locator) if action == "click" 
                else EC.presence_of_element_located(locator)
            )
            if action == "click":
                element.click()
            elif action == "send_keys" and value:
                element.clear()
                element.send_keys(value)
            return True
            
    except Exception as e:
        logger.warning(f"Fast interaction failed for {locator}, using fallback: {e}")
        return False

def javascript_date_time_selection(driver: webdriver.Chrome, date_str: str, 
                                 start_hour: str, end_hour: str) -> bool:
    """Use JavaScript to directly set date and time values."""
    try:
        driver.execute_script(f"""
            (function() {{
                function setDate(val) {{
                    var el = document.getElementById('event0')
                        || document.querySelector('input.hasDatepicker')
                        || document.querySelector("input[id*='event']")
                        || document.querySelector("input[name*='event']");
                    if (!el) return false;
                    el.value = val;
                    el.dispatchEvent(new Event('input', {{bubbles: true}}));
                    el.dispatchEvent(new Event('change', {{bubbles: true}}));
                    return true;
                }}
                function setTime(startVal, endVal) {{
                    var startSelect = document.getElementsByName('startHour')[0];
                    var endSelect = document.getElementsByName('endHour')[0];
                    if (startSelect) {{ startSelect.value = startVal; startSelect.dispatchEvent(new Event('change', {{bubbles:true}})); }}
                    if (endSelect) {{ endSelect.value = endVal; endSelect.dispatchEvent(new Event('change', {{bubbles:true}})); }}
                    return true;
                }}
                return setDate('{date_str}') && setTime('{start_hour}', '{end_hour}');
            }})();
        """)
        return True
    except Exception as e:
        logger = setup_logging(__name__)
        logger.warning(f"JavaScript date/time selection failed: {e}")
        return False

class BookingError(Exception):
    """Custom exception for booking-related errors."""
    pass

class LoginError(BookingError):
    """Exception raised when login fails."""
    pass

class CourtUnavailableError(BookingError):
    """Exception raised when court is unavailable."""
    pass
