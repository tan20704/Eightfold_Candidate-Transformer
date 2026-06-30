import pandas as pd
from typing import List, Dict, Any
from parsers.base_parser import BaseParser

class CSVParser(BaseParser):
    def parse(self) -> List[Dict[str, Any]]:
        try:
            df = pd.read_csv(self.file_path)
        except Exception:
            # Degrade gracefully on malformed files
            return []

        candidates = []
        for _, row in df.iterrows():
            name = str(row.get("full_name", "")).strip() if pd.notna(row.get("full_name")) else None
            email = str(row.get("email", "")).strip() if pd.notna(row.get("email")) else None
            phone = str(row.get("phone", "")).strip() if pd.notna(row.get("phone")) else None
            
            experience = []
            company = str(row.get("current_company", "")).strip() if pd.notna(row.get("current_company")) else None
            title = str(row.get("title", "")).strip() if pd.notna(row.get("title")) else None
            if company or title:
                experience.append({
                    "company": company or "Unknown",
                    "title": title or "Unknown",
                    "start": None,
                    "end": None,
                    "summary": "Current role from CSV import"
                })

            skills = []
            raw_skills = row.get("skills")
            if pd.notna(raw_skills):
                skills = [s.strip() for s in str(raw_skills).split(",") if s.strip()]

            location_str = str(row.get("location", "")).strip() if pd.notna(row.get("location")) else None

            candidate = {
                "candidate_id": str(row.get("candidate_id", "")).strip() if pd.notna(row.get("candidate_id")) else None,
                "full_name": name,
                "emails": [email] if email else [],
                "phones": [phone] if phone else [],
                "location": location_str,
                "links": {},
                "headline": title,
                "years_experience": None,
                "skills": skills,
                "experience": experience,
                "education": [],
                "_meta": {
                    "source": self.file_path,
                    "method": "csv_row_import"
                }
            }
            candidates.append(candidate)
        
        return candidates