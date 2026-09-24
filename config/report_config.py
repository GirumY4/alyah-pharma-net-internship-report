# config/report_config.py
"""Central metadata for the internship report cover page and build rules."""

REPORT = {
    "university": "Bahir Dar University",
    "institute": "Bahir Dar Institute of Technology",
    "faculty": "Faculty of Electrical and Computer Engineering",
    "department": "Department of Computer Engineering",
    "hosting_company": "Alyah Software Development PLC (Alyah Technologies Group)",
    "project_title": "Alyah Pharma Net — B2B2C Multi-Tenant SaaS "
                     "Pharmaceutical Logistics Platform",
    "project_short": "Alyah Pharma Net — Internship Report",
    "author": "Girum Yasab",
    "id_no": "BDU1506302",
    "mentor": "Siranesh G.",
    "company_supervisor": "Ermias Antigegn",
    "submission_date": "September 21, 2026",
}

PART_TITLES = [
    "Chapter One — Company Background",
    "Chapter Two — Internship Experience",
    "Chapter Three — Project Work",
    "Chapter Four — General Conclusion and Recommendation",
    "References",
    "Appendices",
]

PART_FILES = [
    "01_front_matter.md",
    "02_company_background.md",
    "03_internship_experience.md",
    "04_project_work.md",
    "05_conclusion.md",
    "06_references.md",
    "07_appendices.md",
]

PAGE_BUDGETS = {1: 7, 2: 7, 3: 12, 4: 20, 5: 2, 6: 2, 7: 12}

OUTPUT_NAME = "Alyah_Pharma_Net_Internship_Report.pdf"