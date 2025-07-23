"""Refactored booking script with improved error handling and structure."""

import argparse
import os
from utils import setup_logging, managed_webdriver
from booking_operations import BookingOperations
from config import config, get_court_order, COURT_NAME_MAP

logger = setup_logging(__name__)

def main(selected_time: str, email: str, password: str, relative_days: int) -> str:
    """Main booking function with improved error handling."""
    
    logger.info(f"Starting booking process for {email}, time: {selected_time}, days: {relative_days}")
    
    try:
        with managed_webdriver() as driver:
            booking_ops = BookingOperations(driver)
            
            # Step 1: Login
            booking_ops.login(email, password)
            
            # Step 2: Navigate to booking page
            booking_ops.navigate_to_new_permit_request()
            
            # Step 3: Wait until booking time
            booking_ops.wait_until_booking_time()
            
            # Step 4: Select first choice court
            court_order = get_court_order(selected_time)
            first_court = court_order[0]
            first_court_name = COURT_NAME_MAP[first_court]
            
            booking_ops.select_site_and_checkbox(first_court)
            booking_ops.select_date_and_time(selected_time, relative_days)
            booking_ops.book_court()
            
            # Step 5: Check if booking succeeded or try alternatives
            result_message = ""
            if booking_ops.check_error_message():
                logger.info(f"{first_court_name} not available, trying alternatives")
                result_message = booking_ops.try_booking_alternative_courts(
                    selected_time, email, relative_days
                )
            else:
                result_message = f"Booking successful for {first_court_name} under account {email} for time {selected_time} on day {relative_days}."
                logger.info(result_message)
            
            # Step 6: Fill additional details and submit
            booking_ops.fill_additional_details()
            booking_ops.submit_form()
            
            logger.info("Booking process completed")
            return result_message
            
    except Exception as e:
        error_msg = f"Booking failed for {email}: {str(e)}"
        logger.error(error_msg)
        return error_msg

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Automated Court Booking (Refactored)')
    parser.add_argument('--time', type=str, required=True, help='Selected time for booking')
    parser.add_argument('--email', type=str, required=True, help='Email for login')
    parser.add_argument('--password', type=str, required=True, help='Password for login')
    parser.add_argument('--days', type=int, required=True, help='Relative days for booking (0 for today, 1 for tomorrow, etc.)')
    
    args = parser.parse_args()
    
    result = main(args.time, args.email, args.password, args.days)
    print(result)