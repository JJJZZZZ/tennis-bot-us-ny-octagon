"""Run one or many bookings using the optimized flow.

Edit bookings in booking_schedule.py (comment/uncomment entries),
then run this script. This version books the specific court you provide
in the schedule (no API pre-check auto-selection).
"""

import concurrent.futures
import time
from typing import List, Dict, Tuple
import asyncio
import datetime

from booking_core.utils import (
    setup_logging, managed_webdriver, PerformanceTimer,
    fast_element_interaction, javascript_date_time_selection,
    get_eastern_time, timed_operation,
)
from booking_core.booking_ui_actions import BookingOperations
from bookings_to_edit import BOOKINGS
from booking_core.config import config, COURT_NAME_MAP, SITE_TO_CHECKBOX_MAP, DEFAULT_FORM_DATA

logger = setup_logging(__name__)


# -----------------------------------------------------------------------------
# Configure your bookings in bookings_to_edit.py. Edit that file only.
# -----------------------------------------------------------------------------

# How many parallel bookings to run at once
MAX_PARALLEL = 2


class OptimizedBookingOperations(BookingOperations):
    """Optimized Selenium actions with speed improvements."""

    @timed_operation("Fast login")
    def fast_login(self, email: str, password: str) -> None:
        try:
            self.driver.get(config.LOGIN_URL)

            # Use fast element interactions
            if not fast_element_interaction(self.driver, ("id", 'loginEmail'), "send_keys", email):
                super().login(email, password)
                return

            if not fast_element_interaction(self.driver, ("id", 'loginPassword'), "send_keys", password):
                super().login(email, password)
                return

            if not fast_element_interaction(self.driver, ("xpath", '//button[@tabindex="3"]'), "click"):
                super().login(email, password)
                return

            logger.info(f"Fast login successful for {email}")

        except Exception as e:
            logger.warning(f"Fast login failed, using fallback: {e}")
            super().login(email, password)

    @timed_operation("Fast site selection")
    def fast_select_site_and_checkbox(self, site_id: str) -> None:
        try:
            checkbox_id = SITE_TO_CHECKBOX_MAP[site_id]

            success = self.driver.execute_script(f"""
                try {{
                    var siteSelect = document.getElementById('site');
                    if (siteSelect) {{
                        siteSelect.value = '{site_id}';
                        siteSelect.dispatchEvent(new Event('change'));
                    }}
                    setTimeout(function() {{
                        var addButton = document.getElementById('addFacilitySet');
                        if (addButton) addButton.click();
                        setTimeout(function() {{
                            var checkbox = document.getElementById('{checkbox_id}');
                            if (checkbox) checkbox.click();
                        }}, 500);
                    }}, 1000);
                    return true;
                }} catch(e) {{ return false; }}
            """)

            if success:
                import time as _t
                _t.sleep(2)
                logger.info(f"Fast site selection successful for {site_id}")
            else:
                super().select_site_and_checkbox(site_id)

        except Exception as e:
            logger.warning(f"Fast site selection failed, using fallback: {e}")
            super().select_site_and_checkbox(site_id)

    @timed_operation("Fast date/time selection")
    def fast_select_date_and_time(self, selected_time: str, relative_days: int) -> None:
        try:
            target_date = get_eastern_time() + datetime.timedelta(days=relative_days)
            date_str = target_date.strftime('%m/%d/%Y')
            end_hour = str((int(selected_time) + 1) % 24)

            if javascript_date_time_selection(self.driver, date_str, selected_time, end_hour):
                logger.info(f"Fast date/time selection successful: {date_str} at {selected_time}:00")
            else:
                super().select_date_and_time(selected_time, relative_days)

        except Exception as e:
            logger.warning(f"Fast date/time selection failed, using fallback: {e}")
            super().select_date_and_time(selected_time, relative_days)

    @timed_operation("Fast form filling")
    def fast_fill_additional_details(self) -> None:
        try:
            import json
            input_data_js = json.dumps(DEFAULT_FORM_DATA['input_data'])
            select_data_js = json.dumps(DEFAULT_FORM_DATA['select_data'])

            success = self.driver.execute_script(f"""
                try {{
                    var inputs = {input_data_js};
                    for (var id in inputs) {{
                        var element = document.getElementById(id);
                        if (element) element.value = inputs[id];
                    }}
                    var selects = {select_data_js};
                    for (var id in selects) {{
                        var element = document.getElementById(id);
                        if (element) element.value = selects[id];
                    }}
                    var termsCheckbox = document.getElementById('acceptTerms');
                    if (termsCheckbox) termsCheckbox.checked = true;
                    return true;
                }} catch(e) {{ return false; }}
            """)

            if success:
                logger.info("Fast form filling successful")
            else:
                super().fill_additional_details()

        except Exception as e:
            logger.warning(f"Fast form filling failed, using fallback: {e}")
            super().fill_additional_details()


def _resolve_site_id(site_id: str = None, court: str = None) -> str:
    """Resolve a site id from either site_id or court name."""
    if site_id:
        return site_id
    if court:
        # Reverse map court name -> site_id
        for sid, name in COURT_NAME_MAP.items():
            if name.lower() == court.lower():
                return sid
    raise ValueError("Missing site_id or unknown court name")


@timed_operation("Complete optimized booking")
async def optimized_booking_once(selected_time: str, email: str, password: str, relative_days: int, *, site_id: str = None, court: str = None) -> str:
    """Optimized booking for a specific court from the schedule (no API pre-check)."""
    with PerformanceTimer("Total booking operation", logger):
        logger.info("🚀 Starting booking for court specified in schedule")

        try:
            with PerformanceTimer("Selenium booking phase", logger):
                with managed_webdriver() as driver:
                    booking_ops = OptimizedBookingOperations(driver)

                    booking_ops.fast_login(email, password)

                    with PerformanceTimer("Navigation", logger):
                        if not fast_element_interaction(driver, ("link_text", "New Permit Request"), "click"):
                            booking_ops.navigate_to_new_permit_request()

                    booking_ops.wait_until_booking_time()

                    resolved_site_id = _resolve_site_id(site_id, court)
                    court_name = COURT_NAME_MAP.get(resolved_site_id, court or "Unknown Court")
                    booking_ops.fast_select_site_and_checkbox(resolved_site_id)

                    booking_ops.fast_select_date_and_time(selected_time, relative_days)

                    with PerformanceTimer("Booking confirmation", logger):
                        booking_ops.book_court()

                    if booking_ops.check_error_message():
                        logger.warning(f"Court {court_name} unavailable or booking failed; trying alternatives…")
                        alt_court = booking_ops.try_booking_alternative_courts(
                            selected_time, email, relative_days, exclude_site_id=resolved_site_id
                        )
                        if not alt_court:
                            return f"❌ Booking failed for {court_name} under account {email} for time {selected_time} on day {relative_days}."
                        # Replace court_name to reflect the alternative selected
                        court_name = alt_court

                    # Only fill and submit if we did not see an error (either initial or alternative worked)
                    booking_ops.fast_fill_additional_details()

                    with PerformanceTimer("Form submission", logger):
                        booking_ops.submit_form()

                    return f"✅ Booking successful for {court_name} under account {email} for time {selected_time} on day {relative_days}."

        except Exception as e:
            error_msg = f"❌ Optimized booking failed for {email}: {str(e)}"
            logger.error(error_msg)
            return error_msg


def book_sync(selected_time: str, email: str, password: str, relative_days: int, *, site_id: str = None, court: str = None) -> str:
    """Synchronous wrapper to run one optimized booking for a specific court."""
    return asyncio.run(optimized_booking_once(selected_time, email, password, relative_days, site_id=site_id, court=court))


def run_all(bookings: List[Dict[str, str]], max_workers: int = MAX_PARALLEL) -> List[Tuple[str, int, str]]:
    """Run all configured bookings concurrently."""
    results: List[Tuple[str, int, str]] = []
    start_overall = time.time()

    logger.info(f"Starting {len(bookings)} booking(s) with up to {max_workers} parallel workers")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_booking = {}
        for b in bookings:
            days_val = int(b["days"]) if isinstance(b["days"], str) else b["days"]
            site = b.get("site_id")
            court = b.get("court")
            if not site and not court:
                logger.error(f"Missing 'site_id' or 'court' in booking entry: {b}")
                continue
            fut = executor.submit(
                book_sync,
                b["time"], b["email"], b["password"], days_val,
                site_id=site, court=court,
            )
            future_to_booking[fut] = b

        for future in concurrent.futures.as_completed(future_to_booking):
            b = future_to_booking[future]
            try:
                output = future.result()
                logger.info(f"✅ Completed: {b['email']} @ {b['time']} (days={b['days']})")
                print(f"\n--- Result for {b['email']} @ {b['time']} ---\n{output}\n--- End Result ---\n")
                results.append((f"{b['email']}@{b['time']}", 0, output))
            except Exception as e:
                logger.error(f"❌ Failed: {b['email']} @ {b['time']} (days={b['days']}): {e}")
                results.append((f"{b['email']}@{b['time']}", -1, str(e)))

    duration = time.time() - start_overall
    logger.info(f"All bookings finished in {duration:.2f}s")
    return results

import argparse


def _mask(s: str, keep: int = 2) -> str:
    if not s:
        return ""
    return s[:keep] + "*" * max(0, len(s) - keep)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run tennis court bookings from bookings_to_edit.py")
    p.add_argument("--dry-run", action="store_true", help="Print planned bookings without using Selenium")
    p.add_argument("--max-parallel", type=int, help=f"Override max parallel (default {MAX_PARALLEL})")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    if not BOOKINGS:
        logger.warning("No bookings configured in bookings_to_edit.py. Edit that file and uncomment entries.")
        return 0

    if args.dry_run:
        print("Planned bookings (dry-run):\n")
        for b in BOOKINGS:
            try:
                days_val = int(b["days"]) if isinstance(b["days"], str) else b["days"]
                site = b.get("site_id")
                court = b.get("court")
                resolved = _resolve_site_id(site, court)
                court_name = COURT_NAME_MAP.get(resolved, court or "Unknown Court")
                print(f"- {b['email']} time={b['time']} days={days_val} court={court_name} (site_id={resolved})")
            except Exception as e:
                print(f"! Invalid entry {b}: {e}")
        return 0

    max_workers = args.max_parallel if args.max_parallel else MAX_PARALLEL
    run_all(BOOKINGS, max_workers)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
