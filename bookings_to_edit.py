"""Booking schedule to edit easily.

Edit this file: comment/uncomment the entries you want to run.
The system will automatically use the priority order for court selection based on the time:
  - Morning (before 12 PM): Tennis 1, 4, 3, 6, 2, 5
  - Afternoon/Evening (12 PM+): Tennis 6, 3, 4, 1, 5, 2

You can still specify a specific court if needed:
  - "court": human name, e.g. "Octagon Tennis 3"; or
  - "site_id": internal site id (advanced)

Then run:  python3 run_bookings.py
"""

from typing import List, Dict


BOOKINGS: List[Dict[str, str]] = [
    # Day 0 bookings (today)
    # {"time": "16", "email": "Kainalam14@gmail.com", "password": "Skyline2024!", "days": 0},  # Jennifer Chan
    # {"time": "12", "email": "jjjzzzzlalala@gmail.com", "password": "Lalala@222", "days": 0},  # Yihan Li
    # {"time": "18", "email": "nianiabu.chow@gmail.com", "password": "Lalala@222", "days": 0},  # Nia Zhou
    # {"time": "19", "email": "garvey_chow@sina.com", "password": "Lalala@222", "days": 0},  # Jaway Chow
    # {"time": "14", "email": "savannahlee.xiang@gmail.com", "password": "test123123", "days": 0},  # Xiang Li

    # Day 1 bookings (tomorrow)
    # {"time": "18", "email": "Kainalam14@gmail.com", "password": "Skyline2024!", "days": 1},  # Jennifer Chan
    {"time": "18", "email": "jjjzzzzlalala@gmail.com", "password": "Lalala@222", "days": 1},  # Yihan Li
    {"time": "19", "email": "nianiabu.chow@gmail.com", "password": "Lalala@222", "days": 1},  # Nia Zhou
    # {"time": "21", "email": "garvey_chow@sina.com", "password": "Lalala@222", "days": 1},  # Jaway Chow
    # {"time": "20", "email": "savannahlee.xiang@gmail.com", "password": "test123123", "days": 1},  # Xiang Li

    # Day 2 bookings
    # {"time": "13", "email": "Kainalam14@gmail.com", "password": "Skyline2024!", "days": 2},  # Jennifer Chan
    # {"time": "20", "email": "jjjzzzzlalala@gmail.com", "password": "Lalala@222", "days": 2},  # Yihan Li
    # {"time": "18", "email": "nianiabu.chow@gmail.com", "password": "Lalala@222", "days": 2},  # Nia Zhou
    # {"time": "19", "email": "garvey_chow@sina.com", "password": "Lalala@222", "days": 2},  # Jaway Chow
    # {"time": "20", "email": "savannahlee.xiang@gmail.com", "password": "test123123", "days": 2},  # Xiang Li
    # {"time": "17", "email": "vvveichen@gmail.com", "password": "Topspin888999", "days": 2},  # Vei
    # {"time": "16", "email": "Vvveichen112@gmail.com", "password": "Topspin888999", "days": 2},  # Vei

    # Day 3 bookings
    # {"time": "18", "email": "Kainalam14@gmail.com", "password": "Skyline2024!", "days": 3},  # Jennifer Chan
    # {"time": "13", "email": "jjjzzzzlalala@gmail.com", "password": "Lalala@222", "days": 3},  # Yihan Li
    # {"time": "20", "email": "nianiabu.chow@gmail.com", "password": "Lalala@222", "days": 3},  # Nia Zhou
    # {"time": "21", "email": "garvey_chow@sina.com", "password": "Lalala@222", "days": 3},  # Jaway Chow
    # {"time": "17", "email": "savannahlee.xiang@gmail.com", "password": "test123123", "days": 3},  # Xiang Li

    # Day 4 bookings
    # {"time": "18", "email": "Kainalam14@gmail.com", "password": "Skyline2024!", "days": 4},  # Jennifer Chan
    # {"time": "19", "email": "jjjzzzzlalala@gmail.com", "password": "Lalala@222", "days": 4},  # Yihan Li
    # {"time": "20", "email": "nianiabu.chow@gmail.com", "password": "Lalala@222", "days": 4},  # Nia Zhou
    # {"time": "21", "email": "garvey_chow@sina.com", "password": "Lalala@222", "days": 4},  # Jaway Chow
    # {"time": "17", "email": "savannahlee.xiang@gmail.com", "password": "test123123", "days": 4},  # Xiang Li

    # Day 5 bookings
    # {"time": "18", "email": "Kainalam14@gmail.com", "password": "Skyline2024!", "days": 5},  # Jennifer Chan
    # {"time": "19", "email": "jjjzzzzlalala@gmail.com", "password": "Lalala@222", "days": 5},  # Yihan Li
    # {"time": "20", "email": "nianiabu.chow@gmail.com", "password": "Lalala@222", "days": 5},  # Nia Zhou
    # {"time": "21", "email": "garvey_chow@sina.com", "password": "Lalala@222", "days": 5},  # Jaway Chow
]

