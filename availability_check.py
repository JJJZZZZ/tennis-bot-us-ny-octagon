import aiohttp
import asyncio
import datetime
import argparse
import os
from yarl import URL
from config import config, COURT_IDS, DEFAULT_HEADERS
from utils import setup_logging, retry_on_exception, get_eastern_date_string

logger = setup_logging(__name__)

@retry_on_exception(max_retries=3, exceptions=(aiohttp.ClientError, asyncio.TimeoutError))
async def login(email, password):
    """Login and return session cookies."""
    async with aiohttp.ClientSession() as session:
        payload = {
            'Email': email,
            'Password': password,
            'RememberMe': 'false'
        }
        try:
            async with session.post(config.LOGIN_URL, data=payload) as response:
                text = await response.text()
                if response.status == 200 and "New Permit Request" in text:
                    cookies = session.cookie_jar.filter_cookies(URL(config.LOGIN_URL))
                    logger.info(f"Login successful for {email}")
                    return {cookie.key: cookie.value for cookie in cookies.values()}
                else:
                    raise Exception(f"Login failed with status code {response.status}")
        except Exception as e:
            logger.error(f"Login error for {email}: {e}")
            raise

async def check_court_availability(session, api_url, headers, payload):
    """Check availability for a specific court and time slot."""
    try:
        async with session.post(api_url, headers=headers, json=payload) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.warning(f"API request failed with status {response.status}")
                return None
    except Exception as e:
        logger.error(f"Error checking availability: {e}")
        return None

async def main(relative_days):
    EMAIL = os.getenv("TENNIS_EMAIL", "jjjzzzzlalala@gmail.com")
    PASSWORD = os.getenv("TENNIS_PASSWORD", "Lalala@222")

    target_date = get_eastern_date_string(relative_days)
    logger.info(f"Checking availability for {target_date} (Eastern Time)")

    try:
        cookies = await login(EMAIL, PASSWORD)
        cookie_header = "; ".join([f"{key}={value}" for key, value in cookies.items()])

        headers = DEFAULT_HEADERS.copy()
        headers['Cookie'] = cookie_header

        tasks = []
        async with aiohttp.ClientSession() as session:
            for hour in range(config.BOOKING_START_HOUR, config.BOOKING_END_HOUR):
                for court_id, court_name in COURT_IDS.items():
                    payload = {
                        "facilityNames": ["Tennis Courts"],
                        "facilityIds": [court_id],
                        "dates": [{"start": f"{target_date}T{hour:02d}:00:00", "stop": f"{target_date}T{hour+1:02d}:00:00"}]
                    }
                    tasks.append(check_court_availability(session, config.AVAILABILITY_API_URL, headers, payload))

            responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        available_courts_by_time = {f"{hour:02d}:00": [] for hour in range(config.BOOKING_START_HOUR, config.BOOKING_END_HOUR)}

        court_list = list(COURT_IDS.items())
        for hour in range(config.BOOKING_START_HOUR, config.BOOKING_END_HOUR):
            hour_start_idx = (hour - config.BOOKING_START_HOUR) * len(COURT_IDS)
            hour_end_idx = hour_start_idx + len(COURT_IDS)
            hour_responses = responses[hour_start_idx:hour_end_idx]
            
            for response, (court_id, court_name) in zip(hour_responses, court_list):
                if isinstance(response, Exception):
                    logger.error(f"Error for {court_name} at {hour:02d}:00: {response}")
                elif response == []:
                    available_courts_by_time[f"{hour:02d}:00"].append(court_name)

        # Display results
        print(f"Available courts on {target_date}:")
        total_available = 0
        for time, courts in available_courts_by_time.items():
            if courts:
                print(f"Time: {time} - Courts: {', '.join(courts)}")
                total_available += len(courts)
        
        if total_available == 0:
            print("No courts available for the selected date.")
        else:
            print(f"\nTotal available slots: {total_available}")
            
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        print(f"Error checking availability: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check court availability for a given number of relative days from today.")
    parser.add_argument("--days", type=int, required=True, help="Number of days from today to check availability for")
    args = parser.parse_args()
    
    asyncio.run(main(args.days))