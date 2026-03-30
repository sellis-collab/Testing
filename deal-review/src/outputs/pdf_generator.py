import logging
import os
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from ..models.deal import DealRecord
from ..scoring.criteria_loader import ScoringCriteria

logger = logging.getLogger(__name__)

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
DEFAULT_OUTPUT_DIR = "data/output"


class PDFGenerator:

    def __init__(self, output_dir: str = DEFAULT_OUTPUT_DIR, criteria: ScoringCriteria = None):
        self.output_dir = output_dir
        self.criteria = criteria
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

    def generate(self, deal: DealRecord) -> str:
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        criteria = self.criteria
        company_name = criteria.report.company_name if criteria else "Deal Review"
        primary_color = criteria.report.primary_color if criteria else "#1a3a5c"

        score = deal.score_total or 0
        if score >= 80:
            score_color = "#27ae60"
        elif score >= 60:
            score_color = "#e67e22"
        else:
            score_color = "#c0392b"

        template = self.env.get_template("report.html")
        html_content = template.render(
            deal=deal,
            criteria=criteria,
            company_name=company_name,
            primary_color=primary_color,
            generated_date=str(date.today()),
            score_color=score_color,
            score_pct_str=f"{score}%",
        )

        safe_name = (deal.property_name or deal.deal_id or "deal").replace(" ", "_")[:40]

        try:
            from weasyprint import HTML  # optional dependency
            filename = f"{deal.deal_id}_{safe_name}_report.pdf"
            output_path = os.path.join(self.output_dir, filename)
            HTML(string=html_content, base_url=TEMPLATE_DIR).write_pdf(output_path)
            logger.info(f"PDF report generated: {output_path}")
        except Exception:
            filename = f"{deal.deal_id}_{safe_name}_report.html"
            output_path = os.path.join(self.output_dir, filename)
            Path(output_path).write_text(html_content, encoding="utf-8")
            logger.info(f"HTML report saved (open in browser to print as PDF): {output_path}")

        return output_path
