import subprocess
import os

def run_scripts():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # List of scripts to run with optional time arguments
    scripts = [
        'availability_check.py --days 1',  # Add the availability_check.py script
        
        # 'booking_script.py --time 16 --email Kainalam14@gmail.com  --password Skyline2024! --days 0',  # Jennifer Chan
        # 'booking_script.py --time 17 --email jjjzzzzlalala@gmail.com --password Lalala@222 --days 0',  # Yihan Li
        # 'booking_script.py --time 18 --email nianiabu.chow@gmail.com --password Lalala@222 --days 0',  # Nia Zhou
        # 'booking_script.py --time 19 --email garvey_chow@sina.com --password Lalala@222 --days 0',  # Jaway Chow
        # 'booking_script.py --time 14 --email savannahlee.xiang@gmail.com --password test123123 --days 0',  # Xiang Li

        
        # 'booking_script.py --time 18 --email Kainalam14@gmail.com  --password Skyline2024! --days 1',  # Jennifer Chan
        'booking_script.py --time 13 --email jjjzzzzlalala@gmail.com --password Lalala@222 --days 1',  # Yihan Li
        # 'booking_script.py --time 21 --email nianiabu.chow@gmail.com --password Lalala@222 --days 1',  # Nia Zhou
        # 'booking_script.py --time 21 --email garvey_chow@sina.com --password Lalala@222 --days 1',  # Jaway Chow
        # 'booking_script.py --time 20 --email savannahlee.xiang@gmail.com --password test123123 --days 1',  # Xiang Li

        
        # 'booking_script.py --time 13 --email Kainalam14@gmail.com  --password Skyline2024! --days 2',  # Jennifer Chan
        # 'booking_script.py --time 14 --email jjjzzzzlalala@gmail.com --password Lalala@222 --days 2',  # Yihan Li
        # 'booking_script.py --time 18 --email nianiabu.chow@gmail.com --password Lalala@222 --days 2',  # Nia Zhou
        # 'booking_script.py --time 19 --email garvey_chow@sina.com --password Lalala@222 --days 2',  # Jaway Chow
        # 'booking_script.py --time 20 --email savannahlee.xiang@gmail.com --password test123123 --days 2',  # Xiang Li
        # 'booking_script.py --time 17 --email vvveichen@gmail.com --password Topspin888999 --days 2',  # Vei
        # 'booking_script.py --time 16 --email Vvveichen112@gmail.com --password Topspin888999 --days 2',  # Vei
        
        # 'booking_script.py --time 18 --email Kainalam14@gmail.com  --password Skyline2024! --days 3',  # Jennifer Chan
        # 'booking_script.py --time 19 --email jjjzzzzlalala@gmail.com --password Lalala@222 --days 3',  # Yihan Li
        # 'booking_script.py --time 20 --email nianiabu.chow@gmail.com --password Lalala@222 --days 3',  # Nia Zhou
        # 'booking_script.py --time 21 --email garvey_chow@sina.com --password Lalala@222 --days 3',  # Jaway Chow
        # 'booking_script.py --time 17 --email savannahlee.xiang@gmail.com --password test123123 --days 3',  # Xiang Li


        # 'booking_script.py --time 18 --email Kainalam14@gmail.com  --password Skyline2024! --days 4',  # Jennifer Chan
        # 'booking_script.py --time 19 --email jjjzzzzlalala@gmail.com --password Lalala@222 --days 4',  # Yihan Li
        # 'booking_script.py --time 20 --email nianiabu.chow@gmail.com --password Lalala@222 --days 4',  # Nia Zhou
        # 'booking_script.py --time 21 --email garvey_chow@sina.com --password Lalala@222 --days 4',  # Jaway Chow
        # 'booking_script.py --time 17 --email savannahlee.xiang@gmail.com --password test123123 --days 4',  # Xiang Li

        # 'booking_script.py --time 18 --email Kainalam14@gmail.com  --password Skyline2024! --days 5',  # Jennifer Chan
        # 'booking_script.py --time 19 --email jjjzzzzlalala@gmail.com --password Lalala@222 --days 5',  # Yihan Li
        # 'booking_script.py --time 20 --email nianiabu.chow@gmail.com --password Lalala@222 --days 5',  # Nia Zhou
        # 'booking_script.py --time 21 --email garvey_chow@sina.com --password Lalala@222 --days 5',  # Jaway Chow
    ]
    
    # Start each script using subprocess
    processes = []
    for script in scripts:
        # Change to the script directory and run the script
        cmd = ['python3'] + script.split()
        process = subprocess.Popen(cmd, cwd=script_dir)
        processes.append(process)

    # Optionally, you can wait for each to complete (remove if not needed)
    for proc in processes:
        proc.wait()

# Call the function directly to run scripts immediately
run_scripts()
