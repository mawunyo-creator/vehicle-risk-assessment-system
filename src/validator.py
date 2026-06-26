import re

def validate_vin(vin_string: str) -> bool:
    if not vin_string or len(vin_string) != 17:
        return False
    vin_clean = vin_string.upper().strip()
    if not re.match(r"^[A-HJ-NPR-Z0-9]{17}$", vin_clean):
        return False
    return True