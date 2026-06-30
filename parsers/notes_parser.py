import re
from typing import List, Dict, Any
from parsers.base_parser import BaseParser

class NotesParser(BaseParser):
    def parse(self) -> List[Dict[str, Any]]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception:
            return []

        lines = [l.strip() for l in text.split("\n")]
        non_empty = [l for l in lines if l]

        candidate = {
            "candidate_id": None,
            "full_name": None,
            "emails": [],
            "phones": [],
            "location": None,
            "links": {},
            "headline": None,
            "years_experience": None,
            "skills": [],
            "experience": [],
            "education": []
        }

        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        candidate["emails"] = list(dict.fromkeys(emails))

        phones = re.findall(r"(?:\+?\d{1,3}[-\s]?)?\(?[6-9]\d{2,4}\)?[-\s]?\d{3,5}[-\s]?\d{3,5}", text)
        cleaned_phones = []
        for p in phones:
            p_clean = re.sub(r"[^\d+]", "", p)
            if len(p_clean) >= 10:
                cleaned_phones.append(p)
        candidate["phones"] = list(dict.fromkeys(cleaned_phones))

        name_match = re.search(r"(?:name|candidate)\s*:\s*(.*)", text, re.IGNORECASE)
        if name_match:
            candidate["full_name"] = name_match.group(1).strip()
        elif non_empty:
            first = non_empty[0]
            if len(first.split()) <= 4 and "@" not in first and not any(c.isdigit() for c in first):
                candidate["full_name"] = first

        links = {}
        github_match = re.search(r"github\.com/([a-zA-Z0-9_-]+)", text, re.IGNORECASE)
        linkedin_match = re.search(r"linkedin\.com/in/([a-zA-Z0-9_-]+)", text, re.IGNORECASE)
        if github_match:
            links["github"] = f"https://github.com/{github_match.group(1)}"
        if linkedin_match:
            links["linkedin"] = f"https://linkedin.com/in/{linkedin_match.group(1)}"
        candidate["links"] = links

        yexp_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\s*(?:of\s*)?experience", text, re.IGNORECASE)
        if yexp_match:
            try:
                candidate["years_experience"] = float(yexp_match.group(1))
            except ValueError:
                pass

        skills_match = re.search(r"(?:skills|technologies|proficient in|knows)\s*:\s*(.*)", text, re.IGNORECASE)
        if skills_match:
            skills_part = skills_match.group(1)
            if "," in skills_part:
                candidate["skills"] = [s.strip() for s in skills_part.split(",") if s.strip()]
            else:
                candidate["skills"] = [s.strip() for s in skills_part.split() if s.strip()]

        candidate["_meta"] = {
            "source": self.file_path,
            "method": "recruiter_notes_extraction"
        }

        return [candidate]
