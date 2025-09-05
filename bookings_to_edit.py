"""Booking schedule to edit easily.

Edit this file: comment/uncomment the entries you want to run.
You must specify which court to book via either:
  - "court": human name, e.g. "Octagon Tennis 3"; or
  - "site_id": internal site id (advanced)

Then run:  python3 run_bookings.py
"""

from typing import List, Dict


BOOKINGS: List[Dict[str, str]] = [
    # Day 0 bookings (today)
    # {"time": "16", "email": "Kainalam14@gmail.com", "password": "Skyline2024!", "days": 0, "court": "Octagon Tennis 1"},  # Jennifer Chan
    {"time": "12", "email": "jjjzzzzlalala@gmail.com", "password": "Lalala@222", "days": 0, "court": "Octagon Tennis 2"},  # Yihan Li
    # {"time": "18", "email": "nianiabu.chow@gmail.com", "password": "Lalala@222", "days": 0, "court": "Octagon Tennis 3"},  # Nia Zhou
    # {"time": "19", "email": "garvey_chow@sina.com", "password": "Lalala@222", "days": 0, "court": "Octagon Tennis 4"},  # Jaway Chow
    # {"time": "14", "email": "savannahlee.xiang@gmail.com", "password": "test123123", "days": 0, "court": "Octagon Tennis 5"},  # Xiang Li

    # Day 1 bookings (tomorrow)
    # {"time": "18", "email": "Kainalam14@gmail.com", "password": "Skyline2024!", "days": 1, "court": "Octagon Tennis 6"},  # Jennifer Chan
    # {"time": "12", "email": "jjjzzzzlalala@gmail.com", "password": "Lalala@222", "days": 1, "court": "Octagon Tennis 2"},  # Yihan Li
    # {"time": "21", "email": "nianiabu.chow@gmail.com", "password": "Lalala@222", "days": 1, "court": "Octagon Tennis 3"},  # Nia Zhou
    # {"time": "21", "email": "garvey_chow@sina.com", "password": "Lalala@222", "days": 1, "court": "Octagon Tennis 4"},  # Jaway Chow
    # {"time": "20", "email": "savannahlee.xiang@gmail.com", "password": "test123123", "days": 1, "court": "Octagon Tennis 5"},  # Xiang Li

    # Day 2 bookings
    # {"time": "13", "email": "Kainalam14@gmail.com", "password": "Skyline2024!", "days": 2, "court": "Octagon Tennis 1"},  # Jennifer Chan
    # {"time": "20", "email": "jjjzzzzlalala@gmail.com", "password": "Lalala@222", "days": 2, "court": "Octagon Tennis 2"},  # Yihan Li
    # {"time": "18", "email": "nianiabu.chow@gmail.com", "password": "Lalala@222", "days": 2, "court": "Octagon Tennis 3"},  # Nia Zhou
    # {"time": "19", "email": "garvey_chow@sina.com", "password": "Lalala@222", "days": 2, "court": "Octagon Tennis 4"},  # Jaway Chow
    # {"time": "20", "email": "savannahlee.xiang@gmail.com", "password": "test123123", "days": 2, "court": "Octagon Tennis 5"},  # Xiang Li
    # {"time": "17", "email": "vvveichen@gmail.com", "password": "Topspin888999", "days": 2, "court": "Octagon Tennis 6"},  # Vei
    # {"time": "16", "email": "Vvveichen112@gmail.com", "password": "Topspin888999", "days": 2, "court": "Octagon Tennis 1"},  # Vei

    # Day 3 bookings
    # {"time": "18", "email": "Kainalam14@gmail.com", "password": "Skyline2024!", "days": 3, "court": "Octagon Tennis 1"},  # Jennifer Chan
    # {"time": "19", "email": "jjjzzzzlalala@gmail.com", "password": "Lalala@222", "days": 3, "court": "Octagon Tennis 2"},  # Yihan Li
    # {"time": "20", "email": "nianiabu.chow@gmail.com", "password": "Lalala@222", "days": 3, "court": "Octagon Tennis 3"},  # Nia Zhou
    # {"time": "21", "email": "garvey_chow@sina.com", "password": "Lalala@222", "days": 3, "court": "Octagon Tennis 4"},  # Jaway Chow
    # {"time": "17", "email": "savannahlee.xiang@gmail.com", "password": "test123123", "days": 3, "court": "Octagon Tennis 5"},  # Xiang Li

    # Day 4 bookings
    # {"time": "18", "email": "Kainalam14@gmail.com", "password": "Skyline2024!", "days": 4, "court": "Octagon Tennis 6"},  # Jennifer Chan
    # {"time": "19", "email": "jjjzzzzlalala@gmail.com", "password": "Lalala@222", "days": 4, "court": "Octagon Tennis 2"},  # Yihan Li
    # {"time": "20", "email": "nianiabu.chow@gmail.com", "password": "Lalala@222", "days": 4, "court": "Octagon Tennis 3"},  # Nia Zhou
    # {"time": "21", "email": "garvey_chow@sina.com", "password": "Lalala@222", "days": 4, "court": "Octagon Tennis 4"},  # Jaway Chow
    # {"time": "17", "email": "savannahlee.xiang@gmail.com", "password": "test123123", "days": 4, "court": "Octagon Tennis 5"},  # Xiang Li

    # Day 5 bookings
    # {"time": "18", "email": "Kainalam14@gmail.com", "password": "Skyline2024!", "days": 5, "court": "Octagon Tennis 1"},  # Jennifer Chan
    # {"time": "19", "email": "jjjzzzzlalala@gmail.com", "password": "Lalala@222", "days": 5, "court": "Octagon Tennis 2"},  # Yihan Li
    # {"time": "20", "email": "nianiabu.chow@gmail.com", "password": "Lalala@222", "days": 5, "court": "Octagon Tennis 3"},  # Nia Zhou
    # {"time": "21", "email": "garvey_chow@sina.com", "password": "Lalala@222", "days": 5, "court": "Octagon Tennis 4"},  # Jaway Chow
]

