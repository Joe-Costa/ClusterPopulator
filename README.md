# ClusterPopulator

Generate realistic business file structures with sample data. Creates directories and files that simulate a typical enterprise file share for more realistic product demos.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
# Basic usage: generate 100 files
python -m cluster_populator ./output 100

# Deep structure with year folders
python -m cluster_populator ./output 500 --depth 3

# Preview without creating files
python -m cluster_populator ./output 50 --preview

# Reproducible output with seed
python -m cluster_populator ./output 100 --seed 12345

# Force Windows-compatible filenames (when generating on Mac/Linux)
python -m cluster_populator ./output 100 --windows
```

## Options

| Option | Description |
|--------|-------------|
| `path` | Output directory for generated files |
| `count` | Number of files to generate (1-10000) |
| `-d, --depth` | Directory depth: 1=flat, 2=subdirs, 3=with years (default: 2) |
| `-s, --seed` | Random seed for reproducible output |
| `-c, --concurrency` | Parallel file generation tasks (default: 10) |
| `-p, --preview` | Preview structure without creating files |
| `-w, --windows` | Force Windows-compatible filenames |
| `-q, --quiet` | Suppress progress output |
| `--platform-info` | Show platform detection info |

## Directory Structure

Files are organized by department with realistic subdirectories:

```
output/
  Finance/
    Invoices/, Reports/, Budgets/, Tax/, Payroll/, Audits/
  Human_Resources/
    Policies/, Onboarding/, Training/, Recruiting/, Benefits/
  Marketing/
    Campaigns/, Collateral/, Analytics/, Brand/, Content/
  Sales/
    Proposals/, Contracts/, Pipeline/, Accounts/, Quotes/
  Operations/
    Procedures/, Inventory/, Logistics/, Vendors/, Quality/
  Legal/
    Contracts/, Compliance/, Agreements/, NDAs/, IP/
  IT/
    Documentation/, Configurations/, Logs/, Projects/, Security/
  Executive/
    Strategy/, Board_Materials/, Memos/, Reports/, Investors/
```

## File Types

| Extension | Content |
|-----------|---------|
| `.docx` | Memos, policies, contracts, reports |
| `.xlsx` | Financial data, employee lists, invoices |
| `.pdf` | Reports, contracts, policies |
| `.pptx` | Presentations |
| `.csv` | Data exports |
| `.json` | Configuration files, data |
| `.xml` | Configuration, data exports |
| `.txt` | Memos, meeting notes, logs |
| `.html` | Reports |
| `.md` | Meeting notes, project docs |

## Cross-Platform Support

- **Windows**: Filename sanitization enabled automatically
- **macOS/Linux**: Use `--windows` flag when generating files for Windows targets

Sanitization removes invalid characters (`< > : " / \ | ? * &`) and handles reserved names (`CON`, `PRN`, `COM1`, etc.).

## Performance

Generates ~150 files/second using async parallel processing.
