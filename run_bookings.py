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
import os

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
        logger.debug(f"Starting fast_login for email: {email[:5]}***")
        try:
            logger.debug(f"Navigating to login URL: {config.LOGIN_URL}")
            self.driver.get(config.LOGIN_URL)
            logger.debug("Login page loaded successfully")

            # Use fast element interactions
            logger.debug("Attempting to enter email address")
            if not fast_element_interaction(self.driver, ("id", 'loginEmail'), "send_keys", email):
                logger.warning("Fast email entry failed, falling back to standard login")
                super().login(email, password)
                return

            logger.debug("Attempting to enter password")
            if not fast_element_interaction(self.driver, ("id", 'loginPassword'), "send_keys", password):
                logger.warning("Fast password entry failed, falling back to standard login")
                super().login(email, password)
                return

            logger.debug("Attempting to click login button")
            if not fast_element_interaction(self.driver, ("xpath", '//button[@tabindex="3"]'), "click"):
                logger.warning("Fast login button click failed, falling back to standard login")
                super().login(email, password)
                return

            logger.info(f"Fast login successful for {email[:5]}***")

        except Exception as e:
            logger.error(f"Fast login failed with exception: {e}", exc_info=True)
            logger.warning(f"Fast login failed, using fallback: {e}")
            super().login(email, password)

    @timed_operation("Fast site selection")
    def fast_select_site_and_checkbox(self, site_id: str) -> None:
        logger.debug(f"Starting fast_select_site_and_checkbox for site_id: {site_id}")
        try:
            if site_id not in SITE_TO_CHECKBOX_MAP:
                logger.error(f"Site ID {site_id} not found in SITE_TO_CHECKBOX_MAP")
                raise ValueError(f"Unknown site_id: {site_id}")
            
            checkbox_id = SITE_TO_CHECKBOX_MAP[site_id]
            logger.debug(f"Using checkbox_id: {checkbox_id} for site_id: {site_id}")

            logger.debug("Executing JavaScript for site selection and checkbox interaction")
            success = self.driver.execute_script(f"""
                try {{
                    console.log('Starting site selection script for site_id: {site_id}');
                    var siteSelect = document.getElementById('site');
                    if (siteSelect) {{
                        console.log('Found site select element, setting value to {site_id}');
                        siteSelect.value = '{site_id}';
                        siteSelect.dispatchEvent(new Event('change'));
                        console.log('Site value set and change event dispatched');
                    }} else {{
                        console.error('Site select element not found');
                        return false;
                    }}
                    setTimeout(function() {{
                        console.log('Attempting to click addFacilitySet button');
                        var addButton = document.getElementById('addFacilitySet');
                        if (addButton) {{
                            addButton.click();
                            console.log('AddFacilitySet button clicked');
                        }} else {{
                            console.error('AddFacilitySet button not found');
                        }}
                        setTimeout(function() {{
                            console.log('Attempting to click checkbox: {checkbox_id}');
                            var checkbox = document.getElementById('{checkbox_id}');
                            if (checkbox) {{
                                checkbox.click();
                                console.log('Checkbox clicked successfully');
                            }} else {{
                                console.error('Checkbox not found: {checkbox_id}');
                            }}
                        }}, 500);
                    }}, 1000);
                    return true;
                }} catch(e) {{ 
                    console.error('JavaScript error in site selection:', e);
                    return false; 
                }}
            """)

            if success:
                import time as _t
                logger.debug("JavaScript execution successful, waiting 2 seconds for UI updates")
                _t.sleep(2)
                logger.info(f"Fast site selection successful for {site_id} (checkbox: {checkbox_id})")
            else:
                logger.warning("JavaScript site selection failed, falling back to standard method")
                super().select_site_and_checkbox(site_id)

        except Exception as e:
            logger.error(f"Fast site selection failed with exception: {e}", exc_info=True)
            logger.warning(f"Fast site selection failed, using fallback: {e}")
            super().select_site_and_checkbox(site_id)

    @timed_operation("Fast date/time selection")
    def fast_select_date_and_time(self, selected_time: str, relative_days: int) -> None:
        logger.debug(f"Starting fast_select_date_and_time for time: {selected_time}, days: {relative_days}")
        try:
            current_eastern = get_eastern_time()
            target_date = current_eastern + datetime.timedelta(days=relative_days)
            date_str = target_date.strftime('%m/%d/%Y')
            end_hour = str((int(selected_time) + 1) % 24)
            
            logger.debug(f"Current Eastern time: {current_eastern}")
            logger.debug(f"Target date: {target_date} ({date_str})")
            logger.debug(f"Time slot: {selected_time}:00 - {end_hour}:00")

            logger.debug("Calling javascript_date_time_selection function")
            if javascript_date_time_selection(self.driver, date_str, selected_time, end_hour):
                logger.info(f"Fast date/time selection successful: {date_str} at {selected_time}:00-{end_hour}:00")
            else:
                logger.warning("JavaScript date/time selection failed, falling back to standard method")
                super().select_date_and_time(selected_time, relative_days)

        except Exception as e:
            logger.error(f"Fast date/time selection failed with exception: {e}", exc_info=True)
            logger.warning(f"Fast date/time selection failed, using fallback: {e}")
            super().select_date_and_time(selected_time, relative_days)

    @timed_operation("Fast form filling")
    def fast_fill_additional_details(self) -> None:
        logger.debug("Starting fast_fill_additional_details")
        try:
            import json
            input_data_js = json.dumps(DEFAULT_FORM_DATA['input_data'])
            select_data_js = json.dumps(DEFAULT_FORM_DATA['select_data'])
            
            logger.debug(f"Input data to fill: {DEFAULT_FORM_DATA['input_data']}")
            logger.debug(f"Select data to fill: {DEFAULT_FORM_DATA['select_data']}")

            logger.debug("Executing JavaScript for form filling")
            success = self.driver.execute_script(f"""
                try {{
                    console.log('Starting form filling script');
                    var inputs = {input_data_js};
                    var inputCount = 0;
                    for (var id in inputs) {{
                        console.log('Filling input field:', id, 'with value:', inputs[id]);
                        var element = document.getElementById(id);
                        if (element) {{
                            element.value = inputs[id];
                            // Trigger change and input events for validation
                            element.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            element.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            inputCount++;
                            console.log('Successfully filled input:', id);
                        }} else {{
                            console.warn('Input element not found:', id);
                        }}
                    }}
                    console.log('Filled', inputCount, 'input fields');
                    
                    var selects = {select_data_js};
                    var selectCount = 0;
                    for (var id in selects) {{
                        console.log('Setting select field:', id, 'to value:', selects[id]);
                        var element = document.getElementById(id);
                        if (element) {{
                            element.value = selects[id];
                            // Trigger change event for validation
                            element.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            selectCount++;
                            console.log('Successfully set select:', id);
                        }} else {{
                            console.warn('Select element not found:', id);
                        }}
                    }}
                    console.log('Set', selectCount, 'select fields');
                    
                    console.log('Checking terms checkbox with proper event triggering');
                    var termsCheckbox = document.getElementById('acceptTerms');
                    if (termsCheckbox) {{
                        console.log('Terms checkbox found, current state:', termsCheckbox.checked);
                        termsCheckbox.checked = true;
                        
                        // Trigger all possible events that might enable the submit button
                        console.log('Triggering checkbox events...');
                        termsCheckbox.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        termsCheckbox.dispatchEvent(new Event('click', {{ bubbles: true }}));
                        termsCheckbox.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        
                        // Also try triggering on the parent form
                        var form = termsCheckbox.closest('form');
                        if (form) {{
                            console.log('Triggering form validation events');
                            form.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            form.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        }}
                        
                        console.log('Terms checkbox checked and events triggered, new state:', termsCheckbox.checked);
                        
                        // Wait a moment and check submit button state
                        setTimeout(function() {{
                            var submitButtons = document.querySelectorAll('button[type="submit"], input[type="submit"], button:contains("Submit")');
                            console.log('Found', submitButtons.length, 'submit buttons');
                            for (var i = 0; i < submitButtons.length; i++) {{
                                console.log('Submit button', i, 'disabled:', submitButtons[i].disabled, 'classes:', submitButtons[i].className);
                            }}
                        }}, 100);
                        
                    }} else {{
                        console.warn('Terms checkbox not found');
                    }}
                    
                    console.log('Form filling script completed successfully');
                    return true;
                }} catch(e) {{ 
                    console.error('JavaScript error in form filling:', e);
                    return false; 
                }}
            """)

            if success:
                logger.info("Fast form filling successful - all fields populated via JavaScript")
            else:
                logger.warning("JavaScript form filling failed, falling back to standard method")
                super().fill_additional_details()

        except Exception as e:
            logger.error(f"Fast form filling failed with exception: {e}", exc_info=True)
            logger.warning(f"Fast form filling failed, using fallback: {e}")
            super().fill_additional_details()


def _resolve_site_id(site_id: str = None, court: str = None, selected_time: str = None) -> str:
    """Resolve a site id from either site_id, court name, or use priority order."""
    logger.debug(f"Resolving site_id from: site_id={site_id}, court={court}, time={selected_time}")
    
    if site_id:
        logger.debug(f"Using provided site_id: {site_id}")
        return site_id
        
    if court:
        logger.debug(f"Looking up site_id for court name: {court}")
        # Reverse map court name -> site_id
        for sid, name in COURT_NAME_MAP.items():
            if name.lower() == court.lower():
                logger.debug(f"Found matching site_id {sid} for court {court}")
                return sid
        logger.error(f"No site_id found for court name: {court}")
        logger.debug(f"Available courts: {list(COURT_NAME_MAP.values())}")
        raise ValueError(f"Unknown court name: {court}")
    
    # If no specific court is requested, use the first court in priority order
    if selected_time:
        from booking_core.config import get_court_order
        priority_order = get_court_order(selected_time)
        first_priority_site_id = priority_order[0]
        first_priority_court = COURT_NAME_MAP.get(first_priority_site_id, "Unknown Court")
        logger.info(f"No specific court requested, using priority order. First choice: {first_priority_court} (site_id: {first_priority_site_id})")
        return first_priority_site_id
    
    error_msg = f"Missing site_id, court name, and time for priority order. site_id={site_id}, court={court}, time={selected_time}"
    logger.error(error_msg)
    raise ValueError(error_msg)


@timed_operation("Complete optimized booking with pre-setup")
async def optimized_booking_once(selected_time: str, email: str, password: str, relative_days: int, *, site_id: str = None, court: str = None) -> str:
    """Optimized booking with pre-setup before 8 AM for immediate execution."""
    logger.info(f"🚀 Starting optimized booking with pre-setup: email={email[:5]}***, time={selected_time}, days={relative_days}, site_id={site_id}, court={court}")
    
    with PerformanceTimer("Total booking operation", logger):
        try:
            # Check for headless mode from environment variable
            headless_mode = os.getenv('HEADLESS', 'false').lower() == 'true'
            if headless_mode:
                logger.info("🔧 Running in headless mode (no Chrome window will open)")

            with managed_webdriver(headless=headless_mode) as driver:
                booking_ops = OptimizedBookingOperations(driver)

                # Phase 1: Pre-setup (before 8 AM) - do everything except the actual booking
                with PerformanceTimer("Pre-setup phase", logger):
                    logger.info("📋 Starting pre-setup phase (before 8 AM)...")
                    
                    logger.debug("Pre-setup: Login")
                    booking_ops.fast_login(email, password)

                    logger.debug("Pre-setup: Navigate to booking page")
                    if not fast_element_interaction(driver, ("link_text", "New Permit Request"), "click"):
                        logger.debug("Fast navigation failed, using standard navigation")
                        booking_ops.navigate_to_new_permit_request()
                    else:
                        logger.debug("Fast navigation to New Permit Request successful")

                    logger.debug("Pre-setup: Resolve court information")
                    resolved_site_id = _resolve_site_id(site_id, court, selected_time)
                    court_name = COURT_NAME_MAP.get(resolved_site_id, court or "Unknown Court")
                    logger.info(f"Pre-setup: Prepared for court: {court_name} (site_id: {resolved_site_id})")

                    logger.debug("Pre-setup: Select site and checkbox (ready state)")
                    booking_ops.fast_select_site_and_checkbox(resolved_site_id)

                    logger.info("✅ Pre-setup completed! Ready for 8 AM booking execution...")

                # Phase 2: Wait until exactly 8 AM
                logger.debug("⏰ Waiting until booking time (8 AM EST)")
                booking_ops.wait_until_booking_time()

                # Phase 3: Immediate execution at 8 AM
                with PerformanceTimer("Immediate booking execution", logger):
                    logger.info("🏃‍♂️ 8 AM reached! Executing booking immediately...")

                    logger.debug("Immediate: Select date and time")
                    booking_ops.fast_select_date_and_time(selected_time, relative_days)

                    logger.debug("Immediate: Book court")
                    booking_ops.book_court()

                    logger.debug("Immediate: Check for errors")
                    if booking_ops.check_error_message():
                        logger.warning(f"Court {court_name} unavailable or booking failed; trying alternatives…")
                        alt_court = booking_ops.try_booking_alternative_courts(
                            selected_time, email, relative_days, exclude_site_id=resolved_site_id
                        )
                        if not alt_court:
                            error_msg = f"❌ Booking failed for {court_name} under account {email[:5]}*** for time {selected_time} on day {relative_days}."
                            logger.error(error_msg)
                            return error_msg
                        logger.info(f"Alternative booking successful: {alt_court}")
                        court_name = alt_court

                    logger.debug("Immediate: Fill form details")
                    booking_ops.fast_fill_additional_details()

                    logger.debug("Immediate: Submit booking")
                    booking_ops.submit_form()

                    success_msg = f"✅ Booking successful for {court_name} under account {email[:5]}*** for time {selected_time} on day {relative_days}."
                    logger.info(success_msg)
                    return success_msg

        except Exception as e:
            error_msg = f"❌ Optimized booking failed for {email[:5]}***: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg


def book_sync(selected_time: str, email: str, password: str, relative_days: int, *, site_id: str = None, court: str = None) -> str:
    """Synchronous wrapper to run one optimized booking for a specific court."""
    logger.debug(f"book_sync called with: time={selected_time}, email={email[:5]}***, days={relative_days}, site_id={site_id}, court={court}")
    result = asyncio.run(optimized_booking_once(selected_time, email, password, relative_days, site_id=site_id, court=court))
    logger.debug(f"book_sync result: {result}")
    return result


def run_all(bookings: List[Dict[str, str]], max_workers: int = MAX_PARALLEL) -> List[Tuple[str, int, str]]:
    """Run all configured bookings concurrently."""
    results: List[Tuple[str, int, str]] = []
    start_overall = time.time()

    logger.info(f"🚀 Starting {len(bookings)} booking(s) with up to {max_workers} parallel workers")
    logger.debug(f"Booking details: {[{k: (v if k != 'password' else '***') for k, v in b.items()} for b in bookings]}")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_booking = {}
        logger.debug("Submitting booking tasks to thread pool")
        
        for i, b in enumerate(bookings):
            logger.debug(f"Processing booking {i+1}/{len(bookings)}: {b.get('email', 'unknown')} @ {b.get('time', 'unknown')}")
            
            try:
                days_val = int(b["days"]) if isinstance(b["days"], str) else b["days"]
                site = b.get("site_id")
                court = b.get("court")
                
                # Allow bookings without specific court (will use priority order)
                # Only require either site_id, court, or time (for priority order)
                if not site and not court and not b.get("time"):
                    error_msg = f"Missing 'site_id', 'court', or 'time' (for priority order) in booking entry: {b}"
                    logger.error(error_msg)
                    results.append((f"{b.get('email', 'unknown')}@{b.get('time', 'unknown')}", -1, error_msg))
                    continue
                
                logger.debug(f"Submitting booking task: email={b['email'][:5]}***, time={b['time']}, days={days_val}, site_id={site}, court={court}")
                fut = executor.submit(
                    book_sync,
                    b["time"], b["email"], b["password"], days_val,
                    site_id=site, court=court,
                )
                future_to_booking[fut] = b
                
            except Exception as e:
                error_msg = f"Error preparing booking {i+1}: {e}"
                logger.error(error_msg, exc_info=True)
                results.append((f"{b.get('email', 'unknown')}@{b.get('time', 'unknown')}", -1, error_msg))

        logger.info(f"Submitted {len(future_to_booking)} booking tasks, waiting for completion...")
        
        completed_count = 0
        for future in concurrent.futures.as_completed(future_to_booking):
            completed_count += 1
            b = future_to_booking[future]
            logger.debug(f"Processing completed future {completed_count}/{len(future_to_booking)} for {b['email'][:5]}***")
            
            try:
                output = future.result()
                # Check if booking actually succeeded based on the message content
                is_success = output.startswith("✅")
                status = 0 if is_success else -1
                
                if is_success:
                    logger.info(f"✅ Completed ({completed_count}/{len(future_to_booking)}): {b['email'][:5]}*** @ {b['time']} (days={b['days']})")
                else:
                    logger.error(f"❌ Failed ({completed_count}/{len(future_to_booking)}): {b['email'][:5]}*** @ {b['time']} (days={b['days']})")
                
                print(f"\n--- Result for {b['email'][:5]}*** @ {b['time']} ---\n{output}\n--- End Result ---\n")
                results.append((f"{b['email']}@{b['time']}", status, output))
            except Exception as e:
                logger.error(f"❌ Failed ({completed_count}/{len(future_to_booking)}): {b['email'][:5]}*** @ {b['time']} (days={b['days']}): {e}", exc_info=True)
                results.append((f"{b['email']}@{b['time']}", -1, str(e)))

    duration = time.time() - start_overall
    successful_bookings = sum(1 for _, status, _ in results if status == 0)
    failed_bookings = sum(1 for _, status, _ in results if status != 0)
    
    logger.info(f"🏁 All bookings finished in {duration:.2f}s - Success: {successful_bookings}, Failed: {failed_bookings}")
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
    logger.info(f"🎾 Tennis booking script started with args: dry_run={args.dry_run}, max_parallel={args.max_parallel}")

    if not BOOKINGS:
        logger.warning("No bookings configured in bookings_to_edit.py. Edit that file and uncomment entries.")
        return 0

    logger.info(f"Found {len(BOOKINGS)} bookings to process")

    if args.dry_run:
        logger.info("Running in dry-run mode - no actual bookings will be made")
        print("Planned bookings (dry-run):\n")
        for i, b in enumerate(BOOKINGS):
            try:
                days_val = int(b["days"]) if isinstance(b["days"], str) else b["days"]
                site = b.get("site_id")
                court = b.get("court")
                resolved = _resolve_site_id(site, court, b['time'])
                court_name = COURT_NAME_MAP.get(resolved, court or "Auto Priority Order")
                logger.debug(f"Dry-run booking {i+1}: email={b['email'][:5]}***, time={b['time']}, days={days_val}, court={court_name}")
                print(f"- {b['email'][:5]}*** time={b['time']} days={days_val} court={court_name} (site_id={resolved})")
            except Exception as e:
                logger.error(f"Invalid entry {i+1}: {e}")
                print(f"! Invalid entry {b}: {e}")
        logger.info("Dry-run completed successfully")
        return 0

    max_workers = args.max_parallel if args.max_parallel else MAX_PARALLEL
    logger.info(f"Starting live booking run with {max_workers} parallel workers")
    
    try:
        results = run_all(BOOKINGS, max_workers)
        logger.info(f"Booking run completed with {len(results)} results")
        return 0
    except Exception as e:
        logger.error(f"Booking run failed with exception: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
