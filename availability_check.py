import aiohttp
import asyncio
import argparse
import os
import ssl
import certifi
import datetime
from yarl import URL
from booking_core.config import config, COURT_IDS, DEFAULT_HEADERS
from booking_core.utils import setup_logging, retry_on_exception, get_eastern_date_string, get_eastern_time

logger = setup_logging(__name__)


def _session_with_certifi() -> aiohttp.ClientSession:
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    return aiohttp.ClientSession(connector=connector)


@retry_on_exception(max_retries=3, exceptions=(aiohttp.ClientError, asyncio.TimeoutError))
async def login(email, password):
    """Login and return session cookies."""
    async with _session_with_certifi() as session:
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
                # API returns [] when available, else non-empty array with conflicts
                return await response.json()
            else:
                logger.warning(f"API request failed with status {response.status}")
                return None
    except Exception as e:
        logger.error(f"Error checking availability: {e}")
        return None


async def check_day(headers, session, target_date: str):
    """Collect availability for a specific date and return (slots, total).

    slots is a list of tuples: (date_str, hour, [court_names]) for each time with any availability.
    total is the total number of available court slots for that date.
    """
    tasks = []
    for hour in range(config.BOOKING_START_HOUR, config.BOOKING_END_HOUR):
        for court_id, court_name in COURT_IDS.items():
            payload = {
                "facilityNames": ["Tennis Courts"],
                "facilityIds": [court_id],
                "dates": [{"start": f"{target_date}T{hour:02d}:00:00", "stop": f"{target_date}T{hour+1:02d}:00:00"}]
            }
            tasks.append(check_court_availability(session, config.AVAILABILITY_API_URL, headers, payload))

    responses = await asyncio.gather(*tasks, return_exceptions=True)

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

    total_available = 0
    slots = []
    for hour in range(config.BOOKING_START_HOUR, config.BOOKING_END_HOUR):
        time_str = f"{hour:02d}:00"
        courts = available_courts_by_time[time_str]
        if courts:
            slots.append((target_date, hour, courts))
            total_available += len(courts)
    return slots, total_available


async def main_window(days_window: int = 5, specific_day: int | None = None):
    EMAIL = os.getenv("TENNIS_EMAIL", "") or os.getenv("BOOKING_EMAIL", "jjjzzzzlalala@gmail.com")
    PASSWORD = os.getenv("TENNIS_PASSWORD", "") or os.getenv("BOOKING_PASSWORD", "Lalala@222")

    try:
        cookies = await login(EMAIL, PASSWORD)
        cookie_header = "; ".join([f"{key}={value}" for key, value in cookies.items()])

        headers = DEFAULT_HEADERS.copy()
        headers['Cookie'] = cookie_header

        all_slots = []
        totals_by_day = {}
        totals_by_court = {}
        async with _session_with_certifi() as session:
            if specific_day is not None:
                # Single day path
                target_date = get_eastern_date_string(specific_day)
                logger.info(f"Checking availability for {target_date} (Eastern Time)")
                slots, total = await check_day(headers, session, target_date)
                all_slots.extend(slots)
                totals_by_day[target_date] = total
            else:
                # Multi-day path: today through next N days inclusive
                for d in range(0, days_window + 1):
                    target_date = get_eastern_date_string(d)
                    logger.info(f"Checking availability for {target_date} (Eastern Time)")
                    slots, total = await check_day(headers, session, target_date)
                    all_slots.extend(slots)
                    totals_by_day[target_date] = total

        # Totals by court
        for _, _, courts in all_slots:
            for c in courts:
                totals_by_court[c] = totals_by_court.get(c, 0) + 1

        # Pretty, consolidated output
        if not all_slots:
            print(f"No available courts over the next {days_window + 1 if specific_day is None else 1} day(s).")
            return

        def dow(date_str: str) -> str:
            try:
                d = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                return d.strftime("%a")  # Mon, Tue, ...
            except Exception:
                return ""

        def rel(date_str: str) -> str:
            try:
                d = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                today = get_eastern_time().date()
                diff = (d - today).days
                if diff == 0:
                    return "today"
                if diff == 1:
                    return "tomorrow"
                if diff > 1:
                    return f"in {diff} days"
                return f"{abs(diff)} day(s) ago"
            except Exception:
                return ""

        # Header
        if specific_day is None:
            start_date = get_eastern_date_string(0)
            end_date = get_eastern_date_string(days_window)
            print(
                f"Available Courts [{start_date} ({dow(start_date)}) → {end_date} ({dow(end_date)})] "
                f"({config.BOOKING_START_HOUR:02d}:00–{config.BOOKING_END_HOUR-1:02d}:00)"
            )
        else:
            the_date = get_eastern_date_string(specific_day)
            print(
                f"Available Courts [{the_date} ({dow(the_date)})] "
                f"({config.BOOKING_START_HOUR:02d}:00–{config.BOOKING_END_HOUR-1:02d}:00)"
            )
        print("-" * 72)

        # Group by day and print with clear separators
        by_day: dict[str, list[tuple[int, list[str]]]] = {}
        for date_str, hour, courts in all_slots:
            by_day.setdefault(date_str, []).append((hour, courts))

        for date_str in sorted(by_day.keys()):
            print(f"\n===== {date_str} ({dow(date_str)}, {rel(date_str)}) =====")
            for hour, courts in sorted(by_day[date_str], key=lambda x: x[0]):
                print(f"{hour:02d}:00  —  {', '.join(courts)}")

    except Exception as e:
        logger.error(f"Error in availability window check: {e}")
        print(f"Error checking availability: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check court availability from today forward.")
    parser.add_argument("--days", type=int, help="Optional: specific relative day to check (0=today)")
    parser.add_argument("--days-window", type=int, default=5, help="Scan today through N days ahead (default 5)")
    args = parser.parse_args()

    asyncio.run(main_window(days_window=args.days_window, specific_day=args.days))
