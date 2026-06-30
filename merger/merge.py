import re
from datetime import datetime
from typing import List, Dict, Any, Tuple
from validator.schema import (
    CandidateProfile, Location, Links, SkillItem, Experience, Education, Provenance
)
from normalizers.phone import normalize_phone
from normalizers.date import normalize_date
from normalizers.location import normalize_location
from normalizers.skills import normalize_skills, canonicalize_skill

class MergeEngine:
    def merge_candidates(self, raw_candidates: List[Dict[str, Any]]) -> List[CandidateProfile]:
        groups = self._group_candidates(raw_candidates)
        
        merged_profiles = []
        for g in groups:
            profile = self._merge_group(g)
            merged_profiles.append(profile)
        return merged_profiles

    def _group_candidates(self, candidates: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        groups = []
        for c in candidates:
            matched_indices = []
            
            emails = set(e.lower().strip() for e in c.get("emails", []) if e)
            phones = set(re.sub(r"[^\d]", "", p) for p in c.get("phones", []) if p)
            c_id = c.get("candidate_id")

            for idx, g in enumerate(groups):
                match = False
                for gc in g:
                    if c_id and gc.get("candidate_id") == c_id:
                        match = True
                        break
                    gc_emails = set(e.lower().strip() for e in gc.get("emails", []) if e)
                    if emails & gc_emails:
                        match = True
                        break
                    gc_phones = set(re.sub(r"[^\d]", "", p) for p in gc.get("phones", []) if p)
                    if phones & gc_phones:
                        match = True
                        break
                if match:
                    matched_indices.append(idx)

            if not matched_indices:
                groups.append([c])
            elif len(matched_indices) == 1:
                groups[matched_indices[0]].append(c)
            else:
                new_group = [c]
                for idx in sorted(matched_indices, reverse=True):
                    new_group.extend(groups.pop(idx))
                groups.append(new_group)
        return groups

    def _merge_group(self, group: List[Dict[str, Any]]) -> CandidateProfile:
        def get_priority(meta: Dict[str, Any]) -> int:
            method = meta.get("method", "")
            if "csv" in method or "ats" in method:
                return 3
            if "resume" in method:
                return 2
            return 1

        group_sorted = sorted(group, key=lambda x: get_priority(x.get("_meta", {})), reverse=True)

        provenance = []
        field_values = {}

        def add_field_value(field: str, value: Any, source: str, method: str, priority: int):
            if value is not None and value != "" and value != [] and value != {}:
                if field not in field_values:
                    field_values[field] = []
                field_values[field].append((value, source, method, priority))

        for c in group_sorted:
            meta = c.get("_meta", {})
            source = meta.get("source", "Unknown")
            method = meta.get("method", "Unknown")
            priority = get_priority(meta)

            if c.get("candidate_id"):
                add_field_value("candidate_id", c.get("candidate_id"), source, method, priority)
            if c.get("full_name"):
                add_field_value("full_name", c.get("full_name"), source, method, priority)
            for email in c.get("emails", []):
                add_field_value("emails", email, source, method, priority)
            for phone in c.get("phones", []):
                add_field_value("phones", phone, source, method, priority)
            if c.get("location"):
                add_field_value("location", c.get("location"), source, method, priority)
            for k, v in c.get("links", {}).items():
                if v:
                    add_field_value(f"links.{k}", v, source, method, priority)
            if c.get("headline"):
                add_field_value("headline", c.get("headline"), source, method, priority)
            if c.get("years_experience") is not None:
                add_field_value("years_experience", c.get("years_experience"), source, method, priority)
            for skill in c.get("skills", []):
                add_field_value("skills", skill, source, method, priority)
            for exp in c.get("experience", []):
                add_field_value("experience", exp, source, method, priority)
            for edu in c.get("education", []):
                add_field_value("education", edu, source, method, priority)

        def get_best_value(field: str) -> Tuple[Any, List[Tuple[str, str]]]:
            entries = field_values.get(field, [])
            if not entries:
                return None, []
            
            def val_key(entry):
                val = entry[0]
                priority = entry[3]
                length = len(str(val)) if val else 0
                return (priority, length)

            sorted_entries = sorted(entries, key=val_key, reverse=True)
            best_val = sorted_entries[0][0]
            
            sources = []
            for entry in entries:
                if entry[0] == best_val:
                    sources.append((entry[1], entry[2]))
            return best_val, sources

        candidate_id, id_srcs = get_best_value("candidate_id")
        for src, meth in id_srcs:
            provenance.append(Provenance(field="candidate_id", source=src, method=meth))

        full_name, name_srcs = get_best_value("full_name")
        for src, meth in name_srcs:
            provenance.append(Provenance(field="full_name", source=src, method=meth))

        headline, head_srcs = get_best_value("headline")
        for src, meth in head_srcs:
            provenance.append(Provenance(field="headline", source=src, method=meth))

        emails_entries = field_values.get("emails", [])
        emails_unique = {}
        for val, src, meth, pri in emails_entries:
            email_norm = str(val).lower().strip()
            if email_norm not in emails_unique:
                emails_unique[email_norm] = []
            emails_unique[email_norm].append((src, meth))
        emails = list(emails_unique.keys())
        for e in emails:
            for src, meth in emails_unique[e]:
                provenance.append(Provenance(field="emails", source=src, method=meth))

        phones_entries = field_values.get("phones", [])
        phones_unique = {}
        for val, src, meth, pri in phones_entries:
            phone_norm = normalize_phone(val)
            if phone_norm:
                if phone_norm not in phones_unique:
                    phones_unique[phone_norm] = []
                phones_unique[phone_norm].append((src, meth))
        phones = list(phones_unique.keys())
        for p in phones:
            for src, meth in phones_unique[p]:
                provenance.append(Provenance(field="phones", source=src, method=meth))

        raw_loc_val, loc_srcs = get_best_value("location")
        location_obj = None
        if raw_loc_val:
            loc_dict = normalize_location(raw_loc_val)
            location_obj = Location(**loc_dict)
            for src, meth in loc_srcs:
                provenance.append(Provenance(field="location", source=src, method=meth))

        links_obj = Links()
        for link_type in ["linkedin", "github", "portfolio", "other"]:
            link_val, link_srcs = get_best_value(f"links.{link_type}")
            if link_val:
                setattr(links_obj, link_type, link_val)
                for src, meth in link_srcs:
                    provenance.append(Provenance(field=f"links.{link_type}", source=src, method=meth))

        skills_entries = field_values.get("skills", [])
        skills_by_canonical = {}
        for val, src, meth, pri in skills_entries:
            canon = canonicalize_skill(val)
            if canon:
                if canon not in skills_by_canonical:
                    skills_by_canonical[canon] = []
                skills_by_canonical[canon].append((src, meth, pri))

        skills_list = []
        for canon, srcs_info in skills_by_canonical.items():
            max_pri = max(item[2] for item in srcs_info)
            base_conf = 0.60
            if max_pri == 3:
                base_conf = 0.95
            elif max_pri == 2:
                base_conf = 0.85
            
            unique_sources = set(item[0] for item in srcs_info)
            boosted_conf = min(1.0, base_conf + 0.05 * (len(unique_sources) - 1))
            
            srcs = list(unique_sources)
            skills_list.append(SkillItem(
                name=canon,
                confidence=round(boosted_conf, 2),
                sources=srcs
            ))
            for src, meth, pri in srcs_info:
                provenance.append(Provenance(field=f"skills.{canon}", source=src, method=meth))

        exp_entries = field_values.get("experience", [])
        exp_by_company = {}
        for val, src, meth, pri in exp_entries:
            company = val.get("company", "Unknown")
            comp_key = company.lower().replace("inc", "").replace("llc", "").replace("labs", "").strip()
            comp_key = re.sub(r"[^\w\s]", "", comp_key)
            if comp_key not in exp_by_company:
                exp_by_company[comp_key] = []
            exp_by_company[comp_key].append((val, src, meth, pri))

        final_exp = []
        for comp_key, items in exp_by_company.items():
            best_company = "Unknown"
            best_title = "Unknown"
            best_start = None
            best_end = None
            best_summary = None

            items_sorted = sorted(items, key=lambda x: x[3], reverse=True)
            titles = []
            summaries = []
            companies = []
            
            for val, src, meth, pri in items_sorted:
                companies.append(val.get("company"))
                if val.get("title"):
                    titles.append(val.get("title"))
                start_n = normalize_date(val.get("start"))
                end_n = normalize_date(val.get("end"))
                if start_n and not best_start:
                    best_start = start_n
                if end_n and not best_end:
                    best_end = end_n
                if val.get("summary"):
                    summaries.append(val.get("summary"))

            best_company = max(companies, key=len) if companies else "Unknown"
            best_title = max(titles, key=len) if titles else "Unknown"
            best_summary = max(summaries, key=len) if summaries else None

            final_exp.append(Experience(
                company=best_company,
                title=best_title,
                start=best_start,
                end=best_end,
                summary=best_summary
            ))
            
            for val, src, meth, pri in items:
                provenance.append(Provenance(field=f"experience.{best_company}", source=src, method=meth))

        edu_entries = field_values.get("education", [])
        edu_by_inst = {}
        for val, src, meth, pri in edu_entries:
            inst = val.get("institution", "Unknown")
            inst_key = inst.lower().replace("university", "").replace("school", "").replace("college", "").strip()
            inst_key = re.sub(r"[^\w\s]", "", inst_key)
            if inst_key not in edu_by_inst:
                edu_by_inst[inst_key] = []
            edu_by_inst[inst_key].append((val, src, meth, pri))

        final_edu = []
        for inst_key, items in edu_by_inst.items():
            best_inst = "Unknown"
            best_degree = None
            best_field = None
            best_end_year = None

            items_sorted = sorted(items, key=lambda x: x[3], reverse=True)
            institutions = []
            degrees = []
            fields = []
            end_years = []

            for val, src, meth, pri in items_sorted:
                institutions.append(val.get("institution"))
                if val.get("degree"):
                    degrees.append(val.get("degree"))
                if val.get("field"):
                    fields.append(val.get("field"))
                if val.get("end_year"):
                    end_years.append(val.get("end_year"))

            best_inst = max(institutions, key=len) if institutions else "Unknown"
            best_degree = max(degrees, key=len) if degrees else None
            best_field = max(fields, key=len) if fields else None
            
            if end_years:
                for ey in end_years:
                    try:
                        best_end_year = int(float(str(ey)))
                        break
                    except ValueError:
                        pass

            final_edu.append(Education(
                institution=best_inst,
                degree=best_degree,
                field=best_field,
                end_year=best_end_year
            ))
            
            for val, src, meth, pri in items:
                provenance.append(Provenance(field=f"education.{best_inst}", source=src, method=meth))

        calculated_years = 0.0
        for exp in final_exp:
            if exp.start:
                try:
                    start_dt = datetime.strptime(exp.start, "%Y-%m")
                    if exp.end == "Present" or not exp.end:
                        end_dt = datetime(2026, 6, 1)
                    else:
                        end_dt = datetime.strptime(exp.end, "%Y-%m")
                    diff_months = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month)
                    if diff_months > 0:
                        calculated_years += diff_months / 12.0
                except Exception:
                    pass
        
        explicit_years_val, exp_srcs = get_best_value("years_experience")
        if explicit_years_val is not None:
            try:
                years_experience = float(explicit_years_val)
                for src, meth in exp_srcs:
                    provenance.append(Provenance(field="years_experience", source=src, method=meth))
            except ValueError:
                years_experience = round(calculated_years, 1) if calculated_years > 0 else None
        else:
            years_experience = round(calculated_years, 1) if calculated_years > 0 else None

        profile = CandidateProfile(
            candidate_id=candidate_id,
            full_name=full_name,
            emails=emails,
            phones=phones,
            location=location_obj,
            links=links_obj,
            headline=headline,
            years_experience=years_experience,
            skills=skills_list,
            experience=final_exp,
            education=final_edu,
            provenance=[],
            overall_confidence=0.0
        )

        seen_prov = set()
        unique_prov = []
        for p in provenance:
            key = (p.field, p.source, p.method)
            if key not in seen_prov:
                unique_prov.append(p)
                seen_prov.add(key)
        profile.provenance = unique_prov

        score = 0.0
        total_fields = 0

        if full_name:
            total_fields += 1
            entries = field_values.get("full_name", [])
            unique_sources = set(item[1] for item in entries)
            base = 0.95 if any(item[3] == 3 for item in entries) else 0.80
            score += min(1.0, base + 0.05 * (len(unique_sources) - 1))

        if emails:
            total_fields += 1
            entries = field_values.get("emails", [])
            unique_sources = set(item[1] for item in entries)
            score += min(1.0, 0.95 + 0.05 * (len(unique_sources) - 1))

        if phones:
            total_fields += 1
            entries = field_values.get("phones", [])
            unique_sources = set(item[1] for item in entries)
            score += min(1.0, 0.95 + 0.05 * (len(unique_sources) - 1))

        if location_obj and (location_obj.city or location_obj.country):
            total_fields += 1
            entries = field_values.get("location", [])
            unique_sources = set(item[1] for item in entries)
            base = 0.95 if any(item[3] == 3 for item in entries) else 0.75
            score += min(1.0, base + 0.05 * (len(unique_sources) - 1))

        if headline:
            total_fields += 1
            entries = field_values.get("headline", [])
            unique_sources = set(item[1] for item in entries)
            base = 0.95 if any(item[3] == 3 for item in entries) else 0.75
            score += min(1.0, base + 0.05 * (len(unique_sources) - 1))

        if skills_list:
            total_fields += 1
            score += sum(sk.confidence for sk in skills_list) / len(skills_list)

        if final_exp:
            total_fields += 1
            score += 0.85

        if final_edu:
            total_fields += 1
            score += 0.85

        profile.overall_confidence = round(score / total_fields, 2) if total_fields > 0 else 0.0

        return profile