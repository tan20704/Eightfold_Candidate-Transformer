import phonenumbers
import re
from typing import Optional

def normalize_phone(phone: Optional[str], default_region: str = "IN") -> Optional[str]:
    if not phone:
        return None
    
    phone_str = str(phone).strip()
    # Remove icon prefixes or non-numeric characters at start (e.g. ƒ +91...)
    phone_str = re.sub(r"^[^\d+]+", "", phone_str)
    
    try:
        parsed = phonenumbers.parse(phone_str, default_region)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.E164
            )
    except Exception:
        pass
    
    # Heuristics: if formatting fails but it contains 10 digits
    digits = re.sub(r"[^\d]", "", phone_str)
    if len(digits) == 10:
        return f"+91{digits}"
    elif len(digits) == 12 and digits.startswith("91"):
        return f"+{digits}"
        
    return phone_str