import dateparser
from typing import Optional

def normalize_date(date_string: Optional[str]) -> Optional[str]:
    if not date_string:
        return None
    
    clean_date = str(date_string).strip()
    if clean_date.lower() in ["present", "current", "now", "ongoing"]:
        return "Present"
        
    try:
        parsed_dt = dateparser.parse(clean_date)
        if parsed_dt:
            return parsed_dt.strftime("%Y-%m")
    except Exception:
        pass
        
    return clean_date