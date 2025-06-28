import json
from pathlib import Path
from random import choice, randint

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / 'data' / 'mock_data.json'


def _load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def analyze_phone(phone_number: str) -> dict:
    """Return intelligence for the given phone number."""
    data = _load_data()
    for entry in data:
        if entry.get('phone_number') == phone_number:
            return entry

    # generate fake data when phone number not found
    fake_entry = {
        'phone_number': phone_number,
        'name': f'John Doe {randint(100, 999)}',
        'country': choice(['United States', 'United Kingdom', 'Canada', 'Australia']),
        'email': f'user{randint(1000,9999)}@example.com',
        'accounts': [
            f'twitter:user{randint(100,999)}',
            f'instagram:user{randint(100,999)}'
        ],
        'connections': []
    }
    return fake_entry
