"""Realistic filename generator for business documents."""

import random
from datetime import datetime, timedelta
from faker import Faker

from ..utils.platform import sanitize_filename, sanitize_directory_name, is_windows


class FilenameGenerator:
    """Generate realistic business filenames."""

    DEPARTMENT_FILE_PATTERNS = {
        "Finance": {
            "prefixes": [
                "Invoice", "Budget", "Expense_Report", "Financial_Statement",
                "Quarterly_Report", "Annual_Report", "Balance_Sheet", "Cash_Flow",
                "Revenue_Analysis", "Cost_Analysis", "Forecast", "Audit_Report",
                "Tax_Return", "Payroll", "AP_Report", "AR_Report", "GL_Entry",
                "Bank_Reconciliation", "Variance_Report", "PnL_Statement"
            ],
            "content_types": {
                ".xlsx": ["financial", "invoice", "data"],
                ".pdf": ["report", "invoice"],
                ".docx": ["report", "memo"],
                ".csv": ["invoices", "data"],
                ".json": ["invoice", "config"],
            }
        },
        "Human_Resources": {
            "prefixes": [
                "Employee_Handbook", "Onboarding_Checklist", "Performance_Review",
                "Job_Description", "Offer_Letter", "Benefits_Summary", "Policy",
                "Training_Manual", "Attendance_Record", "Leave_Request", "Exit_Interview",
                "Compensation_Plan", "Org_Chart", "Recruitment_Plan", "Interview_Notes",
                "Background_Check", "Reference_Check", "Disciplinary_Action", "Promotion_Letter"
            ],
            "content_types": {
                ".xlsx": ["employees", "data"],
                ".pdf": ["policy", "memo"],
                ".docx": ["policy", "contract", "memo"],
                ".csv": ["employees", "data"],
                ".json": ["employee", "config"],
            }
        },
        "Marketing": {
            "prefixes": [
                "Campaign_Brief", "Marketing_Plan", "Brand_Guidelines", "Social_Media_Calendar",
                "Content_Strategy", "SEO_Report", "Analytics_Report", "Press_Release",
                "Email_Template", "Newsletter", "Case_Study", "Customer_Survey",
                "Market_Research", "Competitor_Analysis", "Product_Launch", "Ad_Copy",
                "Media_Kit", "Event_Plan", "ROI_Analysis", "Audience_Insights"
            ],
            "content_types": {
                ".xlsx": ["data", "financial"],
                ".pdf": ["report", "memo"],
                ".docx": ["memo", "policy"],
                ".pptx": ["presentation"],
                ".csv": ["data"],
                ".json": ["config"],
                ".html": ["report"],
            }
        },
        "Sales": {
            "prefixes": [
                "Proposal", "Quote", "Contract", "Sales_Report", "Pipeline_Report",
                "Account_Plan", "Territory_Plan", "Commission_Report", "Forecast",
                "RFP_Response", "Pricing_Sheet", "Product_Catalog", "Customer_Profile",
                "Sales_Deck", "Competitive_Intel", "Win_Loss_Analysis", "Deal_Summary",
                "Partnership_Agreement", "Renewal_Notice", "Upsell_Opportunity"
            ],
            "content_types": {
                ".xlsx": ["data", "financial"],
                ".pdf": ["contract", "invoice", "report"],
                ".docx": ["contract", "memo", "policy"],
                ".pptx": ["presentation"],
                ".csv": ["data"],
                ".json": ["config"],
            }
        },
        "Operations": {
            "prefixes": [
                "SOP", "Process_Document", "Workflow", "Inventory_Report", "Shipping_Log",
                "Vendor_List", "Quality_Report", "Safety_Manual", "Maintenance_Schedule",
                "Equipment_List", "Facility_Plan", "Capacity_Plan", "Supply_Chain_Report",
                "Logistics_Plan", "Compliance_Checklist", "Incident_Report", "Audit_Checklist",
                "KPI_Dashboard", "Efficiency_Report", "Resource_Allocation"
            ],
            "content_types": {
                ".xlsx": ["data", "employees"],
                ".pdf": ["policy", "report"],
                ".docx": ["policy", "memo"],
                ".csv": ["data"],
                ".json": ["config"],
                ".xml": ["config", "data"],
            }
        },
        "Legal": {
            "prefixes": [
                "Contract", "NDA", "Terms_of_Service", "Privacy_Policy", "Compliance_Report",
                "Legal_Opinion", "Trademark_Filing", "Patent_Application", "Litigation_Summary",
                "Settlement_Agreement", "Lease_Agreement", "Employment_Agreement", "License_Agreement",
                "Vendor_Agreement", "Partnership_Agreement", "Amendment", "Addendum",
                "Power_of_Attorney", "Corporate_Resolution", "Due_Diligence"
            ],
            "content_types": {
                ".pdf": ["contract", "policy"],
                ".docx": ["contract", "policy", "memo"],
                ".xlsx": ["data"],
                ".json": ["config"],
            }
        },
        "IT": {
            "prefixes": [
                "System_Architecture", "Network_Diagram", "Security_Policy", "Backup_Plan",
                "Disaster_Recovery", "Change_Request", "Incident_Report", "Configuration",
                "API_Documentation", "User_Guide", "Admin_Guide", "Release_Notes",
                "Test_Plan", "Bug_Report", "Feature_Spec", "Database_Schema",
                "Deployment_Guide", "Runbook", "Monitoring_Report", "Access_Log"
            ],
            "content_types": {
                ".json": ["config", "log"],
                ".xml": ["config", "data"],
                ".csv": ["data"],
                ".md": ["notes", "project"],
                ".txt": ["log", "notes"],
                ".pdf": ["policy", "report"],
                ".docx": ["policy", "memo"],
                ".xlsx": ["data"],
                ".html": ["report"],
            }
        },
        "Executive": {
            "prefixes": [
                "Board_Presentation", "Strategic_Plan", "Executive_Summary", "Quarterly_Review",
                "Annual_Report", "Investor_Update", "M&A_Analysis", "Due_Diligence",
                "Risk_Assessment", "Succession_Plan", "Corporate_Strategy", "Market_Analysis",
                "Competitive_Landscape", "Growth_Initiative", "Transformation_Plan", "KPI_Summary",
                "Stakeholder_Report", "Vision_Statement", "Mission_Update", "Leadership_Memo"
            ],
            "content_types": {
                ".pptx": ["presentation"],
                ".pdf": ["report", "memo"],
                ".docx": ["report", "memo", "policy"],
                ".xlsx": ["financial", "data"],
            }
        },
    }

    SUBDIRECTORIES = {
        "Finance": ["Invoices", "Reports", "Budgets", "Tax", "Payroll", "Audits"],
        "Human_Resources": ["Policies", "Onboarding", "Payroll", "Training", "Recruiting", "Benefits"],
        "Marketing": ["Campaigns", "Collateral", "Analytics", "Brand", "Events", "Content"],
        "Sales": ["Proposals", "Contracts", "Pipeline", "Presentations", "Accounts", "Quotes"],
        "Operations": ["Procedures", "Inventory", "Logistics", "Vendors", "Quality", "Safety"],
        "Legal": ["Contracts", "Compliance", "Agreements", "NDAs", "Litigation", "IP"],
        "IT": ["Documentation", "Configurations", "Logs", "Projects", "Security", "Infrastructure"],
        "Executive": ["Strategy", "Board_Materials", "Memos", "Reports", "Investors", "Planning"],
    }

    FILE_EXTENSIONS = [".docx", ".xlsx", ".pdf", ".txt", ".json", ".csv", ".pptx", ".xml", ".html", ".md"]

    EXTENSION_WEIGHTS = {
        ".docx": 20,
        ".xlsx": 20,
        ".pdf": 25,
        ".txt": 5,
        ".json": 5,
        ".csv": 8,
        ".pptx": 8,
        ".xml": 3,
        ".html": 3,
        ".md": 3,
    }

    def __init__(self, seed: int | None = None, sanitize_for_windows: bool | None = None):
        """
        Initialize filename generator.

        Args:
            seed: Random seed for reproducibility
            sanitize_for_windows: If True, always sanitize for Windows. If False, never.
                                 If None (default), auto-detect based on current platform.
        """
        self.fake = Faker()
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)

        # Determine sanitization mode
        if sanitize_for_windows is None:
            self._sanitize_for_windows = is_windows()
        else:
            self._sanitize_for_windows = sanitize_for_windows

    def _generate_date_string(self) -> str:
        """Generate a date string for filenames."""
        formats = [
            "%Y%m%d",
            "%Y-%m-%d",
            "%Y_%m_%d",
            "%m%d%Y",
            "%Y%m",
            "Q%q_%Y",
        ]
        date = self.fake.date_between(start_date="-2y", end_date="today")
        fmt = random.choice(formats)
        if "%q" in fmt:
            quarter = (date.month - 1) // 3 + 1
            return fmt.replace("%q", str(quarter)).replace("%Y", str(date.year))
        return date.strftime(fmt)

    def _generate_version_string(self) -> str:
        """Generate a version string for filenames."""
        formats = [
            f"v{random.randint(1, 5)}.{random.randint(0, 9)}",
            f"v{random.randint(1, 10)}",
            f"rev{random.randint(1, 20)}",
            f"draft{random.randint(1, 5)}",
            "final",
            "approved",
        ]
        return random.choice(formats)

    def generate_filename(self, department: str, extension: str | None = None) -> tuple[str, str]:
        """
        Generate a realistic filename for a department.

        Returns:
            Tuple of (filename, content_type for file generation)
        """
        if department not in self.DEPARTMENT_FILE_PATTERNS:
            department = random.choice(list(self.DEPARTMENT_FILE_PATTERNS.keys()))

        dept_config = self.DEPARTMENT_FILE_PATTERNS[department]

        if extension is None:
            available_extensions = list(dept_config["content_types"].keys())
            weights = [self.EXTENSION_WEIGHTS.get(ext, 5) for ext in available_extensions]
            extension = random.choices(available_extensions, weights=weights)[0]

        prefix = random.choice(dept_config["prefixes"])

        components = [prefix]

        pattern = random.choice(["date", "version", "date_version", "name", "simple"])

        if pattern == "date":
            components.append(self._generate_date_string())
        elif pattern == "version":
            components.append(self._generate_version_string())
        elif pattern == "date_version":
            components.append(self._generate_date_string())
            components.append(self._generate_version_string())
        elif pattern == "name":
            name = self.fake.last_name()
            components.append(name)
            if random.random() > 0.5:
                components.append(self._generate_date_string())

        filename = "_".join(components) + extension

        # Sanitize filename for Windows if needed
        filename = sanitize_filename(filename, for_windows=self._sanitize_for_windows)

        content_types = dept_config["content_types"].get(extension, ["memo"])
        content_type = random.choice(content_types)

        return filename, content_type

    def get_subdirectory(self, department: str) -> str:
        """Get a random subdirectory for a department."""
        if department in self.SUBDIRECTORIES:
            subdir = random.choice(self.SUBDIRECTORIES[department])
            return sanitize_directory_name(subdir, for_windows=self._sanitize_for_windows)
        return ""

    def get_departments(self) -> list[str]:
        """Get list of all departments."""
        return list(self.DEPARTMENT_FILE_PATTERNS.keys())

    def get_extensions_for_department(self, department: str) -> list[str]:
        """Get available extensions for a department."""
        if department in self.DEPARTMENT_FILE_PATTERNS:
            return list(self.DEPARTMENT_FILE_PATTERNS[department]["content_types"].keys())
        return self.FILE_EXTENSIONS
