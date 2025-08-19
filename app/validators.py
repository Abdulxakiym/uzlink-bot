from datetime import datetime

def is_valid_date(text: str) -> bool:
    try:
        datetime.strptime(text, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def is_valid_time(text: str) -> bool:
    try:
        datetime.strptime(text, "%H:%M")
        return True
    except ValueError:
        return False

def is_int(text: str) -> bool:
    try:
        int(text)
        return True
    except ValueError:
        return False
