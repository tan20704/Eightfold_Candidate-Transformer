import argparse
import json
import sys
from typing import List, Dict, Any

from parsers.csv_parser import CSVParser
from parsers.resume_parser import ResumeParser
from parsers.ats_parser import ATSParser
from parsers.notes_parser import NotesParser
from merger.merge import MergeEngine
from utils.projection import project_profile

def print_text_profile(data: Dict[str, Any]):
    print("=" * 60)
    print("             CANDIDATE GOLD PROFILE CARD")
    print("=" * 60)
    
    name = data.get("full_name") or data.get("name") or "Unknown"
    headline = data.get("headline") or "N/A"
    cid = data.get("candidate_id") or data.get("id") or "N/A"
    conf = data.get("overall_confidence", 0.0)
    
    print(f"Name:       {name}")
    print(f"Headline:   {headline}")
    print(f"ID:         {cid}")
    print(f"Confidence: {int(conf * 100)}%")
    print("-" * 60)
    
    print("CONTACT INFO:")
    emails = data.get("emails") or data.get("contact_emails") or []
    if emails:
        print(f"  - Emails: {', '.join(emails)}")
    phones = data.get("phones") or data.get("mobile_numbers") or []
    if phones:
        print(f"  - Phones: {', '.join(phones)}")
        
    loc = data.get("location")
    if loc and isinstance(loc, dict):
        parts = [loc.get("city"), loc.get("region"), loc.get("country")]
        loc_str = ", ".join([p for p in parts if p])
        if loc_str:
            print(f"  - Location: {loc_str}")
    elif isinstance(loc, str):
         print(f"  - Location: {loc}")
         
    links = data.get("links") or {}
    if links and isinstance(links, dict) and any(links.values()):
        print("  - Links:")
        for k, v in links.items():
            if v:
                print(f"    * {k.title()}: {v}")
                
    print("-" * 60)
    
    skills = data.get("skills") or data.get("skills_list") or []
    if skills:
        print("SKILLS:")
        for sk in skills:
            if isinstance(sk, dict):
                name_sk = sk.get("name")
                cf = sk.get("confidence", 0.0)
                print(f"  - {name_sk} ({int(cf * 100)}% confidence)")
            else:
                print(f"  - {sk}")
        print("-" * 60)
        
    exp = data.get("experience") or data.get("history") or []
    if exp:
        print("EXPERIENCE:")
        for item in exp:
            comp = item.get("company", "Unknown")
            tit = item.get("title", "Unknown")
            start = item.get("start") or "N/A"
            end = item.get("end") or "N/A"
            print(f"  * {comp} — {tit} ({start} to {end})")
            sum_val = item.get("summary")
            if sum_val:
                print(f"    Summary: {sum_val}")
        print("-" * 60)
        
    edu = data.get("education") or data.get("studies") or []
    if edu:
        print("EDUCATION:")
        for item in edu:
            inst = item.get("institution", "Unknown")
            deg = item.get("degree") or "Degree N/A"
            fld = item.get("field")
            ey = item.get("end_year")
            fld_str = f" in {fld}" if fld else ""
            ey_str = f" (Graduated: {ey})" if ey else ""
            print(f"  * {inst} — {deg}{fld_str}{ey_str}")
        print("-" * 60)
        
    prov = data.get("provenance") or []
    if prov:
        print("PROVENANCE LOG (Traceability):")
        for item in prov:
            fld = item.get("field")
            src = item.get("source")
            meth = item.get("method")
            print(f"  - [{fld}] sourced from '{src}' via {meth}")
            
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Multi-source Candidate Data Transformer CLI")
    parser.add_argument("--csv", nargs="*", help="Paths to recruiter CSV files", default=[])
    parser.add_argument("--resume", nargs="*", help="Paths to resume PDF files", default=[])
    parser.add_argument("--ats", nargs="*", help="Paths to ATS JSON blobs", default=[])
    parser.add_argument("--notes", nargs="*", help="Paths to recruiter notes TXT files", default=[])
    parser.add_argument("--config", help="Path to runtime projection config JSON", default=None)
    parser.add_argument("--output", help="Path to output JSON file", default=None)
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output display format")

    args = parser.parse_args()

    raw_candidates = []

    for csv_path in args.csv:
        try:
            parser_obj = CSVParser(csv_path)
            raw_candidates.extend(parser_obj.parse())
        except Exception as e:
            print(f"Error parsing CSV file {csv_path}: {e}", file=sys.stderr)

    for resume_path in args.resume:
        try:
            parser_obj = ResumeParser(resume_path)
            raw_candidates.extend(parser_obj.parse())
        except Exception as e:
            print(f"Error parsing resume PDF {resume_path}: {e}", file=sys.stderr)

    for ats_path in args.ats:
        try:
            parser_obj = ATSParser(ats_path)
            raw_candidates.extend(parser_obj.parse())
        except Exception as e:
            print(f"Error parsing ATS JSON {ats_path}: {e}", file=sys.stderr)

    for notes_path in args.notes:
        try:
            parser_obj = NotesParser(notes_path)
            raw_candidates.extend(parser_obj.parse())
        except Exception as e:
            print(f"Error parsing notes TXT {notes_path}: {e}", file=sys.stderr)

    if not raw_candidates:
        print("No candidate data was parsed. Please provide at least one input source.", file=sys.stderr)
        sys.exit(1)

    merge_engine = MergeEngine()
    try:
        merged_profiles = merge_engine.merge_candidates(raw_candidates)
    except Exception as e:
        print(f"Error during candidate merging: {e}", file=sys.stderr)
        sys.exit(1)

    config = {}
    if args.config:
        try:
            with open(args.config, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error loading config file {args.config}: {e}", file=sys.stderr)
            sys.exit(1)

    projected_outputs = []
    for profile in merged_profiles:
        try:
            projected = project_profile(profile, config)
            projected_outputs.append(projected)
        except Exception as e:
            print(f"Error during candidate projection: {e}", file=sys.stderr)
            sys.exit(1)

    output_data = projected_outputs[0] if len(projected_outputs) == 1 else projected_outputs

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(json.dumps(output_data, indent=4))
            print(f"Successfully wrote output to {args.output}")
        except Exception as e:
            print(f"Error writing to output file {args.output}: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Screen print logic
    if not args.output or args.format == "text":
        if args.format == "text":
            if isinstance(output_data, list):
                for single in output_data:
                    print_text_profile(single)
            else:
                print_text_profile(output_data)
        else:
            print(json.dumps(output_data, indent=4))

if __name__ == "__main__":
    main()