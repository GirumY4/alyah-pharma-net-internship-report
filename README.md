# Alyah Pharma Net Internship Report

A Python-based project for building a professional internship report and PDF document for the Alyah Pharma Net platform.

This repository packages the internship report into structured Markdown parts, merges them into a single document, and renders a polished PDF using ReportLab. It is designed to keep the report content modular, maintainable, and easy to review.

## Overview

Alyah Pharma Net is a B2B2C multi-tenant SaaS pharmaceutical logistics platform designed for Ethiopian pharmacies and consumers. This project documents the internship experience, company background, project work, and conclusions in a structured academic report format.

The report build pipeline is:

parts/*.md -> build/merged_report.md -> dist/*.pdf

## Features

- Modular report authoring using separate Markdown files
- Automated merge of report sections into a single document
- PDF generation with ReportLab
- Automatic page numbering and document styling
- Table of contents and list-of-figures support
- Part-based report structure with cover page and academic formatting
- Validation command to catch placeholders and missing images

## Project Structure

```text
.
├── assets/
│   └── images/
├── build/
├── config/
│   ├── __init__.py
│   └── report_config.py
├── dist/
├── parts/
│   ├── 01_front_matter.md
│   ├── 02_company_background.md
│   ├── 03_internship_experience.md
│   ├── 04_project_work.md
│   ├── 05_conclusion.md
│   ├── 06_references.md
│   └── 07_appendices.md
├── .gitignore
├── build_report.py
├── requirements.txt
├── README.md
└── LICENSE (if added later)
```

## Why This Repository Exists

This repository is intended to:

- keep the internship report content separated into logical chapters
- allow fast revisions to individual sections without editing a single huge file
- generate a professional PDF output suitable for academic or internship submission
- centralize report metadata such as author, company, institution, and document title

## Tech Stack

- Python 3
- ReportLab
- Matplotlib
- Markdown-based report authoring
- Optional Pillow support for image processing

## Requirements

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Report metadata and output configuration are defined in:

- `config/report_config.py`

This file controls:

- university and department details
- hosting company and project title
- author and mentor information
- report part titles and filenames
- output PDF filename

## Build and Run

The main script is:

```bash
python build_report.py
```

Available commands:

```bash
python build_report.py check
python build_report.py merge
python build_report.py pdf
python build_report.py all
```

### Command Behavior

- `check` — scans report parts for placeholder TODOs, missing images, and conventions
- `merge` — combines all part files into `build/merged_report.md`
- `pdf` — renders the merged Markdown into a PDF in `dist/`
- `all` — runs the full check + merge + PDF workflow

## Output

After a successful PDF build, the report is generated in:

```text
dist/Alyah_Pharma_Net_Internship_Report.pdf
```

## Report Content Overview

The report includes the following major sections:

1. Front matter
2. Company background
3. Internship experience
4. Project work
5. Conclusion and recommendations
6. References
7. Appendices

## Contributing

Contributions are welcome. To improve the project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Validate with the project commands
5. Submit a pull request

## Notes

- The repository currently does not include a license file.
- The project is structured for academic document generation and is not a general-purpose web app.
- For major content edits, update the relevant Markdown files in `parts/` and rebuild the PDF.

## Contact

Project repository:

- GitHub: https://github.com/GirumY4/alyah-pharma-net-internship-report

## License

No license has been specified in the repository at this time.
