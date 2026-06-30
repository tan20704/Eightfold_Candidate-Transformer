from typing import Dict, Any, List, Optional
from validator.schema import CandidateProfile

def project_profile(profile: CandidateProfile, config: Dict[str, Any]) -> Dict[str, Any]:
    profile_dict = profile.model_dump()
    projected = {}
    
    fields_config = config.get("fields", {})
    missing_strategy = config.get("missing_value_strategy", "null")
    
    # If fields config is empty, include all fields as is
    if not fields_config:
        fields_config = {k: k for k in profile_dict.keys() if k not in ["provenance", "overall_confidence"]}
        
    for out_key, mapping in fields_config.items():
        if isinstance(mapping, dict):
            canonical_key = mapping.get("from", out_key)
        else:
            canonical_key = mapping
            
        val = profile_dict.get(canonical_key)
        
        is_missing = False
        if val is None:
            is_missing = True
        elif isinstance(val, list) and not val:
            is_missing = True
        elif isinstance(val, dict) and not val:
            is_missing = True
            
        if is_missing:
            if missing_strategy == "error":
                raise ValueError(f"Required field '{canonical_key}' (mapped to '{out_key}') is missing or empty.")
            elif missing_strategy == "omit":
                continue
            else: # "null"
                projected[out_key] = None
        else:
            if canonical_key == "skills" and isinstance(mapping, dict):
                if mapping.get("format") == "names_only":
                    val = [sk["name"] for sk in val]
            projected[out_key] = val

    include_provenance = config.get("include_provenance", True)
    include_confidence = config.get("include_confidence", True)
    
    if include_provenance:
        renamed_provenance = []
        canon_to_out = {}
        for out_k, mapping in fields_config.items():
            canonical_k = mapping.get("from", out_k) if isinstance(mapping, dict) else mapping
            canon_to_out[canonical_k] = out_k
            
        for prov in profile_dict.get("provenance", []):
            field_name = prov.get("field", "")
            matched_out_key = None
            for canon_k, out_k in canon_to_out.items():
                if field_name == canon_k or field_name.startswith(canon_k + "."):
                    if field_name.startswith(canon_k + "."):
                        matched_out_key = field_name.replace(canon_k, out_k, 1)
                    else:
                        matched_out_key = out_k
                    break
            
            if matched_out_key:
                renamed_provenance.append({
                    "field": matched_out_key,
                    "source": prov.get("source"),
                    "method": prov.get("method")
                })
        projected["provenance"] = renamed_provenance
            
    if include_confidence:
        projected["overall_confidence"] = profile_dict.get("overall_confidence", 0.0)
            
    return projected
