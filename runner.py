import subprocess
import os
import concurrent.futures
import time
from typing import List, Tuple
from utils import setup_logging

logger = setup_logging(__name__)

def run_single_script(script_cmd: str, script_dir: str) -> Tuple[str, int, str]:
    """Run a single script and return result."""
    try:
        cmd = ['python3'] + script_cmd.split()
        logger.info(f"Starting script: {script_cmd}")
        
        start_time = time.time()
        result = subprocess.run(
            cmd, 
            cwd=script_dir, 
            capture_output=True, 
            text=True,
            timeout=300  # 5 minute timeout
        )
        end_time = time.time()
        
        duration = end_time - start_time
        logger.info(f"Script completed: {script_cmd} (took {duration:.2f}s)")
        
        return script_cmd, result.returncode, result.stdout if result.returncode == 0 else result.stderr
        
    except subprocess.TimeoutExpired:
        error_msg = f"Script timed out: {script_cmd}"
        logger.error(error_msg)
        return script_cmd, -1, error_msg
    except Exception as e:
        error_msg = f"Error running script {script_cmd}: {e}"
        logger.error(error_msg)
        return script_cmd, -1, error_msg

def run_scripts_concurrent(max_workers: int = 3):
    """Run scripts concurrently with improved error handling."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Configuration for scripts to run
    scripts = [
        'availability_check.py --days 1',
        
        # Day 0 bookings (today)
        # 'booking_script_refactored.py --time 16 --email Kainalam14@gmail.com --password Skyline2024! --days 0',  # Jennifer Chan
        # 'booking_script_refactored.py --time 17 --email jjjzzzzlalala@gmail.com --password Lalala@222 --days 0',  # Yihan Li
        # 'booking_script_refactored.py --time 18 --email nianiabu.chow@gmail.com --password Lalala@222 --days 0',  # Nia Zhou
        # 'booking_script_refactored.py --time 19 --email garvey_chow@sina.com --password Lalala@222 --days 0',  # Jaway Chow
        # 'booking_script_refactored.py --time 14 --email savannahlee.xiang@gmail.com --password test123123 --days 0',  # Xiang Li

        # Day 1 bookings (tomorrow)
        # 'booking_script_refactored.py --time 18 --email Kainalam14@gmail.com --password Skyline2024! --days 1',  # Jennifer Chan
        'booking_script_refactored.py --time 13 --email jjjzzzzlalala@gmail.com --password Lalala@222 --days 1',  # Yihan Li
        # 'booking_script_refactored.py --time 21 --email nianiabu.chow@gmail.com --password Lalala@222 --days 1',  # Nia Zhou
        # 'booking_script_refactored.py --time 21 --email garvey_chow@sina.com --password Lalala@222 --days 1',  # Jaway Chow
        # 'booking_script_refactored.py --time 20 --email savannahlee.xiang@gmail.com --password test123123 --days 1',  # Xiang Li

        # Day 2 bookings
        # 'booking_script_refactored.py --time 13 --email Kainalam14@gmail.com --password Skyline2024! --days 2',  # Jennifer Chan
        # 'booking_script_refactored.py --time 14 --email jjjzzzzlalala@gmail.com --password Lalala@222 --days 2',  # Yihan Li
        # 'booking_script_refactored.py --time 18 --email nianiabu.chow@gmail.com --password Lalala@222 --days 2',  # Nia Zhou
        # 'booking_script_refactored.py --time 19 --email garvey_chow@sina.com --password Lalala@222 --days 2',  # Jaway Chow
        # 'booking_script_refactored.py --time 20 --email savannahlee.xiang@gmail.com --password test123123 --days 2',  # Xiang Li
        # 'booking_script_refactored.py --time 17 --email vvveichen@gmail.com --password Topspin888999 --days 2',  # Vei
        # 'booking_script_refactored.py --time 16 --email Vvveichen112@gmail.com --password Topspin888999 --days 2',  # Vei
        
        # Day 3 bookings
        # 'booking_script_refactored.py --time 18 --email Kainalam14@gmail.com --password Skyline2024! --days 3',  # Jennifer Chan
        # 'booking_script_refactored.py --time 19 --email jjjzzzzlalala@gmail.com --password Lalala@222 --days 3',  # Yihan Li
        # 'booking_script_refactored.py --time 20 --email nianiabu.chow@gmail.com --password Lalala@222 --days 3',  # Nia Zhou
        # 'booking_script_refactored.py --time 21 --email garvey_chow@sina.com --password Lalala@222 --days 3',  # Jaway Chow
        # 'booking_script_refactored.py --time 17 --email savannahlee.xiang@gmail.com --password test123123 --days 3',  # Xiang Li

        # Day 4 bookings
        # 'booking_script_refactored.py --time 18 --email Kainalam14@gmail.com --password Skyline2024! --days 4',  # Jennifer Chan
        # 'booking_script_refactored.py --time 19 --email jjjzzzzlalala@gmail.com --password Lalala@222 --days 4',  # Yihan Li
        # 'booking_script_refactored.py --time 20 --email nianiabu.chow@gmail.com --password Lalala@222 --days 4',  # Nia Zhou
        # 'booking_script_refactored.py --time 21 --email garvey_chow@sina.com --password Lalala@222 --days 4',  # Jaway Chow
        # 'booking_script_refactored.py --time 17 --email savannahlee.xiang@gmail.com --password test123123 --days 4',  # Xiang Li

        # Day 5 bookings
        # 'booking_script_refactored.py --time 18 --email Kainalam14@gmail.com --password Skyline2024! --days 5',  # Jennifer Chan
        # 'booking_script_refactored.py --time 19 --email jjjzzzzlalala@gmail.com --password Lalala@222 --days 5',  # Yihan Li
        # 'booking_script_refactored.py --time 20 --email nianiabu.chow@gmail.com --password Lalala@222 --days 5',  # Nia Zhou
        # 'booking_script_refactored.py --time 21 --email garvey_chow@sina.com --password Lalala@222 --days 5',  # Jaway Chow
    ]
    
    # Filter out commented scripts
    active_scripts = [script for script in scripts if not script.strip().startswith('#')]
    
    logger.info(f"Starting {len(active_scripts)} scripts with max {max_workers} concurrent workers")
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all scripts
        future_to_script = {
            executor.submit(run_single_script, script, script_dir): script 
            for script in active_scripts
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_script):
            script_cmd, return_code, output = future.result()
            results.append((script_cmd, return_code, output))
            
            if return_code == 0:
                logger.info(f"✅ Success: {script_cmd}")
            else:
                logger.error(f"❌ Failed: {script_cmd} (code: {return_code})")
            
            # Print output for visibility
            if output.strip():
                print(f"\n--- Output for {script_cmd} ---")
                print(output)
                print("--- End Output ---\n")
    
    # Summary
    successful = sum(1 for _, code, _ in results if code == 0)
    failed = len(results) - successful
    
    logger.info(f"Execution complete: {successful} successful, {failed} failed")
    
    return results

def run_scripts_sequential():
    """Run scripts sequentially (legacy mode)."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    scripts = [
        'availability_check.py --days 1',
        # Add active booking scripts here - same format as concurrent version
        'booking_script_refactored.py --time 13 --email jjjzzzzlalala@gmail.com --password Lalala@222 --days 1',
    ]
    
    processes = []
    for script in scripts:
        cmd = ['python3'] + script.split()
        process = subprocess.Popen(cmd, cwd=script_dir)
        processes.append(process)

    # Wait for all processes to complete
    for proc in processes:
        proc.wait()

if __name__ == "__main__":
    # Use concurrent execution by default
    # Change to run_scripts_sequential() if you prefer the old behavior
    run_scripts_concurrent(max_workers=2)
