"""Configuration file for tennis court booking system."""

import os
from typing import Dict, List, Tuple
from dataclasses import dataclass
import pytz

# Timezone configuration for US Eastern Time
EASTERN_TZ = pytz.timezone('US/Eastern')

@dataclass
class BookingConfig:
    """Configuration for booking system."""
    
    # API endpoints
    LOGIN_URL: str = "https://rioc.civicpermits.com/Account/Login?ReturnUrl=%2f"
    AVAILABILITY_API_URL: str = "https://rioc.civicpermits.com/Permits/ConflictCheck"
    
    # Time configuration
    BOOKING_START_HOUR: int = 8
    BOOKING_END_HOUR: int = 22
    WAIT_UNTIL_HOUR: int = 8
    
    # Retry configuration
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 2.0
    
    # Timeout configuration (optimized for speed)
    LOGIN_TIMEOUT: int = 5
    ELEMENT_TIMEOUT: int = 8
    SHORT_TIMEOUT: int = 3
    PAGE_LOAD_TIMEOUT: int = 15
    FAST_TIMEOUT: int = 2  # For known fast elements
    
    # WebDriver configuration
    CHROME_OPTIONS: List[str] = None
    
    def __post_init__(self):
        if self.CHROME_OPTIONS is None:
            self.CHROME_OPTIONS = [
                "--disable-gpu",
                "--window-size=1920,1080",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                # Speed optimizations (keeping JavaScript enabled for functionality)
                "--disable-images",
                "--disable-plugins",
                "--disable-extensions",
                "--disable-background-timer-throttling",
                "--disable-renderer-backgrounding",
                "--disable-backgrounding-occluded-windows",
                "--disable-features=TranslateUI",
                "--disable-default-apps",
                "--disable-sync",
                "--aggressive-cache-discard",
                "--memory-pressure-off",
                "--max_old_space_size=4096",
                "--disable-blink-features=AutomationControlled"
            ]

# Court mappings
COURT_IDS = {
    '036dfea4-c487-47b0-b7fe-c9cbe52b7c98': 'Octagon Tennis 1',
    '175bdff8-016e-46ab-a9df-829fe40c0754': 'Octagon Tennis 2',
    '9bdef00b-afa0-4b6b-bf9a-75899f7f97c7': 'Octagon Tennis 3',
    'd311851d-ce53-49fc-9662-42adcda26109': 'Octagon Tennis 4',
    '8a5ca8e8-3be0-4145-a4ef-91a69671295b': 'Octagon Tennis 5',
    '77c7f42c-8891-4818-a610-d5c1027c62fe': 'Octagon Tennis 6'
}

SITE_TO_CHECKBOX_MAP = {
    '3c9230f0-9e2c-4ff0-8ad7-5300eb475af5': '036dfea4-c487-47b0-b7fe-c9cbe52b7c98',  # Octagon Tennis 1
    'f96d68ab-adea-42cb-8b42-c45a89e7ae2b': '175bdff8-016e-46ab-a9df-829fe40c0754',  # Octagon Tennis 2
    '5633e568-7db6-4e84-a02b-3ac827406bfc': '9bdef00b-afa0-4b6b-bf9a-75899f7f97c7',  # Octagon Tennis 3
    '3e83f44d-ed76-4a95-a73e-e9c5dcfa6e55': 'd311851d-ce53-49fc-9662-42adcda26109',  # Octagon Tennis 4
    '2158c5f2-8734-4755-b2ef-2627d4a5f0b1': '8a5ca8e8-3be0-4145-a4ef-91a69671295b',  # Octagon Tennis 5
    'f3794e38-71ac-4440-9f3b-1adce02df1d7': '77c7f42c-8891-4818-a610-d5c1027c62fe'   # Octagon Tennis 6
}

COURT_NAME_MAP = {
    '3c9230f0-9e2c-4ff0-8ad7-5300eb475af5': 'Octagon Tennis 1',
    'f96d68ab-adea-42cb-8b42-c45a89e7ae2b': 'Octagon Tennis 2',
    '5633e568-7db6-4e84-a02b-3ac827406bfc': 'Octagon Tennis 3',
    '3e83f44d-ed76-4a95-a73e-e9c5dcfa6e55': 'Octagon Tennis 4',
    '2158c5f2-8734-4755-b2ef-2627d4a5f0b1': 'Octagon Tennis 5',
    'f3794e38-71ac-4440-9f3b-1adce02df1d7': 'Octagon Tennis 6'
}

# Form data
DEFAULT_FORM_DATA = {
    'input_data': {
        '11e79e5d3daf4712b9e6418d2691b976': "Tennis",
        'af8966101be44676b4ee564b052e1e87': '2',
        'f28f0dbea8b5438495778b0bb0ddcd93': 'No',
        'd46cb434558845fb9e0318ab6832e427': 'No',
        '1221940f5cca4abdb5288cfcbe284820': 'No',
        '0ce54956c4b14746ae5d364507da1e85': 'No',
        '6b1dda4172f840c7879662bcab1819db': 'No',
        'a31f4297075e4dab8c0ef154f2b9b1c1': '0',
        'activity': "Tennis"
    },
    'select_data': {
        '3754dcef7216446b9cc4bf1cd0f12a2e': 'No',
        '06b3f73192a84fd6b88758e56a64c3ad': 'No'
    }
}

# HTTP headers
DEFAULT_HEADERS = {
    'Content-Type': 'application/json; charset=UTF-8',
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

def get_court_order(selected_time: str) -> List[str]:
    """Get court order based on selected time."""
    hour = int(selected_time)
    if hour < 12:  # Morning session before 12 PM
        return [
            '3c9230f0-9e2c-4ff0-8ad7-5300eb475af5',  # Octagon Tennis 1
            '3e83f44d-ed76-4a95-a73e-e9c5dcfa6e55',  # Octagon Tennis 4
            '5633e568-7db6-4e84-a02b-3ac827406bfc',  # Octagon Tennis 3
            'f3794e38-71ac-4440-9f3b-1adce02df1d7',  # Octagon Tennis 6
            'f96d68ab-adea-42cb-8b42-c45a89e7ae2b',  # Octagon Tennis 2
            '2158c5f2-8734-4755-b2ef-2627d4a5f0b1'   # Octagon Tennis 5
        ]
    else:  # Afternoon or evening session
        return [
            'f3794e38-71ac-4440-9f3b-1adce02df1d7',  # Octagon Tennis 6
            '5633e568-7db6-4e84-a02b-3ac827406bfc',  # Octagon Tennis 3
            '3e83f44d-ed76-4a95-a73e-e9c5dcfa6e55',  # Octagon Tennis 4
            '3c9230f0-9e2c-4ff0-8ad7-5300eb475af5',  # Octagon Tennis 1
            '2158c5f2-8734-4755-b2ef-2627d4a5f0b1',  # Octagon Tennis 5
            'f96d68ab-adea-42cb-8b42-c45a89e7ae2b'   # Octagon Tennis 2
        ]

# Default configuration instance
config = BookingConfig()

