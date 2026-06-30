# 🚀 Multi-Source Candidate Data Transformer

A modular Python-based data transformation pipeline built for the **Eightfold Engineering Internship Assignment (Jul–Dec 2026)**.

The system ingests candidate information from multiple structured and unstructured sources, normalizes inconsistent data, resolves conflicts, merges duplicate profiles, tracks provenance, assigns confidence scores, and generates a configurable canonical candidate profile.

---

## ✨ Features

- Supports multiple data sources
  - Recruiter CSV
  - ATS JSON
  - Resume PDF
  - Recruiter Notes (.txt)

- Data Normalization
  - Phone numbers (E.164)
  - Dates (YYYY-MM)
  - Locations (ISO-3166 Country Codes)
  - Canonical skill mapping

- Intelligent Candidate Matching
  - Email matching
  - Phone matching
  - Candidate ID matching
  - Union-Find (Disjoint Set Union) based grouping

- Merge & Conflict Resolution
  - Source priority based conflict handling
  - Duplicate removal
  - Canonical profile generation

- Provenance Tracking
  - Records the origin of every field
  - Tracks extraction method

- Confidence Scoring
  - Field-level confidence
  - Overall profile confidence

- Runtime Configurable Output
  - Select output fields
  - Rename fields
  - Include/Exclude provenance
  - Include/Exclude confidence
  - Missing value strategies

- Schema Validation using Pydantic

---

# 📂 Project Structure

```text
Eightfold/
│
├── input/
├── merger/
├── normalizers/
├── output/
├── parsers/
├── tests/
├── utils/
├── validator/
│
├── main.py
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/tan20704/Eightfold_Candidate_Transformer.git
```

Move into the project directory

```bash
cd Eightfold_Candidate_Transformer
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Usage

## Default Pipeline

```bash
python main.py \
--csv input/recruiter.csv \
--resume input/resume.pdf \
--output output/profile.json
```

---

## Custom Output Configuration

```bash
python main.py \
--csv input/recruiter.csv \
--resume input/resume.pdf \
--config input/custom_config.json
```

---

# 🧪 Run Tests

```bash
python -m unittest discover -s tests
```

---

# 🔄 Pipeline Workflow

```text
Input Sources
      │
      ▼
Source Detection
      │
      ▼
Parsing & Extraction
      │
      ▼
Normalization
      │
      ▼
Candidate Matching
      │
      ▼
Merge Engine
      │
      ▼
Confidence Calculation
      │
      ▼
Provenance Tracking
      │
      ▼
Schema Validation
      │
      ▼
Projection Layer
      │
      ▼
Canonical JSON Output
```

---

# ⚖️ Merge Policy

| Field | Strategy |
|--------|----------|
| Candidate ID | Structured Source |
| Full Name | Highest Priority Source |
| Emails | Merge + Deduplicate |
| Phones | Normalize + Deduplicate |
| Skills | Canonical Union |
| Experience | Highest Confidence |
| Education | Highest Confidence |

---

# 📌 Edge Cases Handled

- Missing or malformed input files
- Duplicate candidate records
- Transitive candidate matching
- Multiple phone number formats
- Different date formats
- Skill synonym mapping
- Conflicting field values
- Missing field handling (`null`, `omit`, `error`)
- Provenance remapping during projection

---

# 🛠 Technologies Used

- Python 3
- Pandas
- PyMuPDF
- Pydantic
- Phonenumbers
- Dateparser

---

# 📄 Assignment Deliverables

- ✅ Technical Design Document
- ✅ Multi-source Parsing
- ✅ Data Normalization
- ✅ Candidate Matching
- ✅ Merge Engine
- ✅ Provenance Tracking
- ✅ Confidence Scoring
- ✅ Runtime Configurable Output
- ✅ Schema Validation
- ✅ Unit Tests
- ✅ Sample Input & Output

---

# 👩‍💻 Author

**Tanya Verma**

Chandigarh University

Built as part of the **Eightfold Engineering Internship Assignment (Jul–Dec 2026)**.