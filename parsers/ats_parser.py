import json
from typing import List, Dict, Any
from parsers.base_parser import BaseParser

class ATSParser(BaseParser):
    def parse(self) -> List[Dict[str, Any]]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return []

        if isinstance(data, dict):
            raw_candidates = [data]
        elif isinstance(data, list):
            raw_candidates = data
        else:
            return []

        candidates = []
        for item in raw_candidates:
            name = self._find_field(item, ["name", "fullName", "candidateName", "full_name"])
            if not name:
                first = self._find_field(item, ["firstName", "first_name", "fname"])
                last = self._find_field(item, ["lastName", "last_name", "lname"])
                if first or last:
                    name = f"{first or ''} {last or ''}".strip()

            email = self._find_field(item, ["email", "emailAddress", "mail", "email_address"])
            phone = self._find_field(item, ["phone", "phoneNumber", "tel", "mobile", "phone_number"])
            location = self._find_field(item, ["location", "address", "city", "location_str"])
            headline = self._find_field(item, ["headline", "title", "role", "currentRole", "current_title"])
            
            raw_skills = self._find_field(item, ["skills", "technologies", "keySkills", "skills_list"])
            skills = []
            if isinstance(raw_skills, list):
                skills = [str(s).strip() for s in raw_skills if s]
            elif isinstance(raw_skills, str):
                skills = [s.strip() for s in raw_skills.split(",") if s.strip()]

            raw_links = self._find_field(item, ["links", "socials", "profiles", "websites"])
            links = {}
            if isinstance(raw_links, dict):
                for k, v in raw_links.items():
                    lk = k.lower()
                    if "linkedin" in lk:
                        links["linkedin"] = v
                    elif "github" in lk:
                        links["github"] = v
                    elif "portfolio" in lk:
                        links["portfolio"] = v
                    else:
                        links["other"] = v
            elif isinstance(raw_links, list):
                for l in raw_links:
                    l_str = str(l).lower()
                    if "linkedin.com" in l_str:
                        links["linkedin"] = l
                    elif "github.com" in l_str:
                        links["github"] = l
                    else:
                        links["other"] = l

            raw_exp = self._find_field(item, ["experience", "workExperience", "jobs", "history", "work_history"]) or []
            experience = []
            if isinstance(raw_exp, list):
                for exp_item in raw_exp:
                    if isinstance(exp_item, dict):
                        comp = self._find_field(exp_item, ["company", "organization", "employer"])
                        tit = self._find_field(exp_item, ["title", "role", "designation"])
                        st = self._find_field(exp_item, ["start", "startDate", "from", "start_date"])
                        en = self._find_field(exp_item, ["end", "endDate", "to", "end_date"])
                        sum_val = self._find_field(exp_item, ["summary", "description", "details"])
                        
                        if comp or tit:
                            experience.append({
                                "company": comp or "Unknown",
                                "title": tit or "Unknown",
                                "start": str(st) if st else None,
                                "end": str(en) if en else None,
                                "summary": str(sum_val) if sum_val else None
                            })

            raw_edu = self._find_field(item, ["education", "studies", "schools", "degrees"]) or []
            education = []
            if isinstance(raw_edu, list):
                for edu_item in raw_edu:
                    if isinstance(edu_item, dict):
                        inst = self._find_field(edu_item, ["institution", "school", "university", "college"])
                        deg = self._find_field(edu_item, ["degree", "qualification", "certification"])
                        fld = self._find_field(edu_item, ["field", "major", "fieldOfStudy", "branch"])
                        ey = self._find_field(edu_item, ["end_year", "endYear", "year", "graduationYear", "grad_year"])
                        
                        if inst or deg:
                            education.append({
                                "institution": inst or "Unknown",
                                "degree": deg,
                                "field": fld,
                                "end_year": ey
                            })

            candidate = {
                "candidate_id": self._find_field(item, ["candidate_id", "id", "uid"]),
                "full_name": name,
                "emails": [email] if email else [],
                "phones": [phone] if phone else [],
                "location": location,
                "links": links,
                "headline": headline,
                "years_experience": self._find_field(item, ["years_experience", "experienceYears", "exp_years"]),
                "skills": skills,
                "experience": experience,
                "education": education,
                "_meta": {
                    "source": self.file_path,
                    "method": "ats_json_import"
                }
            }
            candidates.append(candidate)
        
        return candidates

    def _find_field(self, d: Dict[str, Any], keys: List[str]) -> Any:
        for k in keys:
            if k in d:
                return d[k]
            for dk in d.keys():
                if dk.lower() == k.lower():
                    return d[dk]
        return None
