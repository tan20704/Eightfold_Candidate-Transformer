from typing import List, Dict, Any, Union

SKILL_SYNONYMS = {
    "c++ programming": "C++",
    "c++": "C++",
    "cpp": "C++",
    "python programming": "Python",
    "python": "Python",
    "c programming": "C",
    "c": "C",
    "java programming": "Java",
    "java": "Java",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "mysql": "MySQL",
    "sql": "SQL",
    "manual testing": "Manual Testing",
    "debugging": "Debugging",
    "tensorflow": "TensorFlow",
    "opencv": "OpenCV",
    "cloud computing": "Cloud Computing",
    "machine learning": "Machine Learning",
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
}

def canonicalize_skill(skill_str: str) -> str:
    if not skill_str:
        return ""
    s_clean = str(skill_str).strip().lower()
    if s_clean in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[s_clean]
    return str(skill_str).strip()

def normalize_skills(skills: List[Union[str, Dict[str, Any]]]) -> List[str]:
    normalized = []
    seen = set()
    for s in skills:
        if isinstance(s, dict):
            name = s.get("name", "")
        else:
            name = str(s)
            
        canonical_name = canonicalize_skill(name)
        if canonical_name and canonical_name.lower() not in seen:
            normalized.append(canonical_name)
            seen.add(canonical_name.lower())
            
    return normalized