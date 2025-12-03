"""Content generators for document text."""

import random
from faker import Faker


class ContentGenerator:
    """Generate realistic business content for documents."""

    LOREM_IPSUM = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod "
        "tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, "
        "quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo "
        "consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse "
        "cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat "
        "non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    )

    LOREM_PARAGRAPHS = [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
        "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
        "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
        "Curabitur pretium tincidunt lacus. Nulla gravida orci a odio. Nullam varius, turpis et commodo pharetra.",
        "Est eros bibendum elit, nec luctus magna felis sollicitudin mauris. Integer in mauris eu nibh euismod gravida.",
        "Duis ac tellus et risus vulputate vehicula. Donec lobortis risus a elit. Etiam tempor ultrices risus.",
        "Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas.",
        "Proin pharetra nonummy pede. Mauris et orci. Aenean nec lorem. In porttitor rhoncus mattis.",
        "Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum.",
    ]

    def __init__(self, seed: int | None = None):
        """Initialize content generator with optional seed for reproducibility."""
        self.fake = Faker()
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)

    def lorem_paragraphs(self, count: int = 3) -> str:
        """Generate multiple lorem ipsum paragraphs."""
        paragraphs = random.choices(self.LOREM_PARAGRAPHS, k=count)
        return "\n\n".join(paragraphs)

    def lorem_sentences(self, count: int = 5) -> str:
        """Generate lorem ipsum sentences."""
        return self.fake.paragraph(nb_sentences=count)

    def business_memo(self) -> dict:
        """Generate a business memo structure."""
        return {
            "to": self.fake.name(),
            "from": self.fake.name(),
            "date": self.fake.date_this_year().isoformat(),
            "subject": self.fake.catch_phrase(),
            "body": self.lorem_paragraphs(3),
        }

    def meeting_notes(self) -> dict:
        """Generate meeting notes structure."""
        attendees = [self.fake.name() for _ in range(random.randint(3, 8))]
        return {
            "title": f"Meeting: {self.fake.bs().title()}",
            "date": self.fake.date_this_year().isoformat(),
            "time": self.fake.time(),
            "attendees": attendees,
            "agenda": [self.fake.sentence() for _ in range(random.randint(3, 6))],
            "notes": self.lorem_paragraphs(2),
            "action_items": [
                {"task": self.fake.sentence(), "owner": random.choice(attendees)}
                for _ in range(random.randint(2, 5))
            ],
        }

    def invoice_data(self) -> dict:
        """Generate invoice data."""
        items = []
        for _ in range(random.randint(2, 8)):
            qty = random.randint(1, 100)
            price = round(random.uniform(10.0, 500.0), 2)
            items.append({
                "description": self.fake.catch_phrase(),
                "quantity": qty,
                "unit_price": price,
                "total": round(qty * price, 2),
            })
        subtotal = sum(item["total"] for item in items)
        tax = round(subtotal * 0.08, 2)
        return {
            "invoice_number": f"INV-{self.fake.random_number(digits=6)}",
            "date": self.fake.date_this_year().isoformat(),
            "due_date": self.fake.date_between(start_date="today", end_date="+30d").isoformat(),
            "vendor": {
                "name": self.fake.company(),
                "address": self.fake.address(),
                "phone": self.fake.phone_number(),
            },
            "customer": {
                "name": self.fake.company(),
                "address": self.fake.address(),
                "contact": self.fake.name(),
            },
            "items": items,
            "subtotal": subtotal,
            "tax": tax,
            "total": round(subtotal + tax, 2),
        }

    def employee_record(self) -> dict:
        """Generate employee record data."""
        return {
            "employee_id": f"EMP-{self.fake.random_number(digits=5)}",
            "name": self.fake.name(),
            "email": self.fake.company_email(),
            "department": random.choice([
                "Finance", "Human Resources", "Marketing", "Sales",
                "Operations", "IT", "Legal", "Executive"
            ]),
            "title": self.fake.job(),
            "hire_date": self.fake.date_between(start_date="-10y", end_date="today").isoformat(),
            "salary": round(random.uniform(45000, 180000), 2),
            "phone": self.fake.phone_number(),
            "address": self.fake.address(),
        }

    def project_data(self) -> dict:
        """Generate project data."""
        return {
            "project_id": f"PRJ-{self.fake.random_number(digits=4)}",
            "name": self.fake.catch_phrase(),
            "description": self.lorem_paragraphs(1),
            "status": random.choice(["Planning", "In Progress", "On Hold", "Completed"]),
            "start_date": self.fake.date_between(start_date="-1y", end_date="today").isoformat(),
            "target_date": self.fake.date_between(start_date="today", end_date="+1y").isoformat(),
            "budget": round(random.uniform(10000, 500000), 2),
            "manager": self.fake.name(),
            "team_members": [self.fake.name() for _ in range(random.randint(3, 10))],
        }

    def contract_data(self) -> dict:
        """Generate contract data."""
        return {
            "contract_id": f"CTR-{self.fake.random_number(digits=6)}",
            "title": f"{self.fake.bs().title()} Agreement",
            "party_a": self.fake.company(),
            "party_b": self.fake.company(),
            "effective_date": self.fake.date_this_year().isoformat(),
            "expiration_date": self.fake.date_between(start_date="+1y", end_date="+3y").isoformat(),
            "value": round(random.uniform(5000, 1000000), 2),
            "terms": self.lorem_paragraphs(4),
        }

    def financial_report_data(self) -> dict:
        """Generate financial report data."""
        revenue = round(random.uniform(100000, 10000000), 2)
        expenses = round(revenue * random.uniform(0.5, 0.9), 2)
        return {
            "period": f"Q{random.randint(1, 4)} {self.fake.year()}",
            "revenue": revenue,
            "expenses": expenses,
            "net_income": round(revenue - expenses, 2),
            "categories": {
                "Sales": round(revenue * random.uniform(0.4, 0.6), 2),
                "Services": round(revenue * random.uniform(0.2, 0.4), 2),
                "Other": round(revenue * random.uniform(0.05, 0.2), 2),
            },
            "expense_breakdown": {
                "Salaries": round(expenses * 0.45, 2),
                "Operations": round(expenses * 0.25, 2),
                "Marketing": round(expenses * 0.15, 2),
                "Other": round(expenses * 0.15, 2),
            },
        }

    def spreadsheet_data(self, rows: int = 20, cols: int = 5) -> list[list]:
        """Generate generic spreadsheet data."""
        headers = [self.fake.word().title() for _ in range(cols)]
        data = [headers]
        for _ in range(rows):
            row = []
            for _ in range(cols):
                cell_type = random.choice(["text", "number", "date", "currency"])
                if cell_type == "text":
                    row.append(self.fake.word())
                elif cell_type == "number":
                    row.append(random.randint(1, 1000))
                elif cell_type == "date":
                    row.append(self.fake.date_this_year().isoformat())
                else:
                    row.append(round(random.uniform(10, 10000), 2))
            data.append(row)
        return data

    def presentation_content(self, slides: int = 8) -> list[dict]:
        """Generate presentation slide content."""
        slide_data = []
        slide_data.append({
            "title": self.fake.catch_phrase(),
            "subtitle": self.fake.company(),
            "type": "title",
        })
        for i in range(1, slides - 1):
            slide_type = random.choice(["bullet", "content", "two_column"])
            if slide_type == "bullet":
                slide_data.append({
                    "title": self.fake.bs().title(),
                    "bullets": [self.fake.sentence() for _ in range(random.randint(3, 6))],
                    "type": "bullet",
                })
            elif slide_type == "content":
                slide_data.append({
                    "title": self.fake.bs().title(),
                    "content": self.lorem_paragraphs(1),
                    "type": "content",
                })
            else:
                slide_data.append({
                    "title": self.fake.bs().title(),
                    "left": [self.fake.sentence() for _ in range(3)],
                    "right": [self.fake.sentence() for _ in range(3)],
                    "type": "two_column",
                })
        slide_data.append({
            "title": "Thank You",
            "subtitle": self.fake.catch_phrase(),
            "type": "title",
        })
        return slide_data

    def policy_document(self) -> dict:
        """Generate policy document content."""
        sections = []
        for i in range(random.randint(4, 8)):
            sections.append({
                "heading": f"{i + 1}. {self.fake.bs().title()}",
                "content": self.lorem_paragraphs(2),
            })
        return {
            "title": f"{random.choice(['Company', 'Corporate', 'Employee'])} {random.choice(['Policy', 'Guidelines', 'Procedures'])}: {self.fake.bs().title()}",
            "effective_date": self.fake.date_this_year().isoformat(),
            "version": f"{random.randint(1, 5)}.{random.randint(0, 9)}",
            "purpose": self.lorem_paragraphs(1),
            "scope": self.fake.paragraph(),
            "sections": sections,
            "approved_by": self.fake.name(),
        }

    def log_entries(self, count: int = 50) -> list[dict]:
        """Generate log entries."""
        levels = ["INFO", "DEBUG", "WARNING", "ERROR"]
        weights = [60, 20, 15, 5]
        entries = []
        for _ in range(count):
            entries.append({
                "timestamp": self.fake.date_time_this_month().isoformat(),
                "level": random.choices(levels, weights=weights)[0],
                "source": random.choice(["app", "database", "network", "auth", "api"]),
                "message": self.fake.sentence(),
            })
        return sorted(entries, key=lambda x: x["timestamp"])
