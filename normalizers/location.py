import re
from typing import Optional, Dict, Any

COUNTRY_MAP = {
    "india": "IN",
    "ind": "IN",
    "in": "IN",
    "united states": "US",
    "united states of america": "US",
    "usa": "US",
    "us": "US",
    "united kingdom": "GB",
    "uk": "GB",
    "great britain": "GB",
    "gb": "GB",
    "canada": "CA",
    "ca": "CA",
    "australia": "AU",
    "germany": "DE",
    "france": "FR",
    "japan": "JP",
    "singapore": "SG",
}

def normalize_country(country_str: Optional[str]) -> Optional[str]:
    if not country_str:
        return None
    c_clean = str(country_str).strip().lower()
    c_clean = re.sub(r"[^\w\s]", "", c_clean)
    
    if c_clean in COUNTRY_MAP:
        return COUNTRY_MAP[c_clean]
        
    for name, code in COUNTRY_MAP.items():
        if name in c_clean or c_clean in name:
            return code
            
    if len(c_clean) == 2:
        return c_clean.upper()
        
    return country_str.upper()

def normalize_location(location_input: Any) -> Dict[str, Optional[str]]:
    default_location = {"city": None, "region": None, "country": None}
    
    if not location_input:
        return default_location
        
    if isinstance(location_input, dict):
        city = location_input.get("city")
        region = location_input.get("region")
        country = location_input.get("country")
        return {
            "city": str(city).strip() if city else None,
            "region": str(region).strip() if region else None,
            "country": normalize_country(country)
        }
        
    if isinstance(location_input, str):
        parts = [p.strip() for p in location_input.split(",") if p.strip()]
        if len(parts) == 3:
            return {
                "city": parts[0],
                "region": parts[1],
                "country": normalize_country(parts[2])
            }
        elif len(parts) == 2:
            c_norm = normalize_country(parts[1])
            if c_norm and len(c_norm) == 2:
                return {
                    "city": parts[0],
                    "region": None,
                    "country": c_norm
                }
            else:
                return {
                    "city": parts[0],
                    "region": parts[1],
                    "country": None
                }
        elif len(parts) == 1:
            c_norm = normalize_country(parts[0])
            if c_norm and c_norm in COUNTRY_MAP.values():
                return {
                    "city": None,
                    "region": None,
                    "country": c_norm
                }
            else:
                if parts[0].lower() in ["chandigarh", "delhi", "mumbai", "bangalore", "bengaluru", "pune", "hyderabad", "chennai"]:
                    return {
                        "city": parts[0],
                        "region": None,
                        "country": "IN"
                    }
                return {
                    "city": parts[0],
                    "region": None,
                    "country": None
                }
                
    return default_location
