"""
Deal Review Orchestrator
========================
Entry point for processing an industrial real estate deal.

Usage (command line):
    python -m src.orchestrator \
        --subject "Eastgate Logistics Park — Deal Opportunity" \
        --attachments path/to/brochure.pdf path/to/uw_model.xlsx

Usage (from Python / Claude prompt):
    from src.orchestrator import process_deal
    result = process_deal(
        subject="Eastgate Logistics Park",
        attachment_paths=["brochure.pdf", "uw_model.xlsx"],
        email_body="Optional body text from the email",
    )
    print(result)
"""

import argparse
import logging
import os
import sys
import uuid
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from .extractors.attachment_handler import classify_and_extract
from .models.deal import DealRecord
from .outputs.excel_generator import ExcelGenerator
from .outputs.pdf_generator import PDFGenerator
from .scoring.criteria_loader import CriteriaLoader
from .scoring.deal_scorer import DealScorer

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "data/output")


def process_deal(
    subject: str,
    attachment_paths: list[str],
    email_body: str = "",
    received_date: date = None,
    output_dir: str = OUTPUT_DIR,
) -> dict:
    """
    Full pipeline for a single deal.

    Parameters
    ----------
    subject          : Email subject line (used as fallback property name)
    attachment_paths : List of local file paths to attachments
    email_body       : Optional plain-text email body (may contain summary data)
    received_date    : Date email was received (defaults to today)
    output_dir       : Where to write PDF and Excel outputs

    Returns
    -------
    dict with keys: deal_id, pdf_path, excel_path, recommendation, score_total, flags
    """
    deal_id = str(uuid.uuid4())[:8].upper()
    received_date = received_date or date.today()

    logger.info(f"=== Processing deal {deal_id}: {subject} ===")

    # --- 1. Build initial DealRecord ---
    deal = DealRecord(
        deal_id=deal_id,
        source_email_subject=subject,
        received_date=received_date,
        property_name=subject,  # will be overwritten by extractors
    )

    # If email body provided, add as extraction note
    if email_body.strip():
        deal.extraction_notes.append(f"EMAIL BODY: {email_body[:1000]}")

    # --- 2. Extract from each attachment ---
    if not attachment_paths:
        logger.warning("No attachments provided — scoring with empty data.")

    for file_path in attachment_paths:
        try:
            extracted, source = classify_and_extract(file_path)
            if extracted and "_parse_error" not in extracted:
                deal.merge(extracted, source=source)
                logger.info(f"  Merged {len(extracted)} fields from {Path(file_path).name} [{source}]")
            else:
                note = f"Extraction error for {Path(file_path).name}: {extracted.get('_parse_error', 'unknown')}"
                deal.extraction_notes.append(note)
                logger.warning(note)
        except FileNotFoundError as e:
            logger.error(str(e))
        except Exception as e:
            logger.error(f"Unexpected error processing {file_path}: {e}", exc_info=True)
            deal.extraction_notes.append(f"Error processing {Path(file_path).name}: {e}")

    # --- 3. Score the deal ---
    logger.info("Scoring deal...")
    criteria = CriteriaLoader().load()
    scorer = DealScorer(criteria)
    deal = scorer.score(deal)
    logger.info(f"  Score: {deal.score_total}% → {deal.recommendation}")

    # --- 4. Generate outputs ---
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    pdf_path = None
    try:
        pdf_gen = PDFGenerator(output_dir=output_dir, criteria=criteria)
        pdf_path = pdf_gen.generate(deal)
        logger.info(f"  PDF: {pdf_path}")
    except ImportError:
        logger.warning("WeasyPrint not installed — skipping PDF generation. Run: pip install weasyprint")
    except Exception as e:
        logger.error(f"PDF generation failed: {e}", exc_info=True)

    excel_path = None
    try:
        excel_path = ExcelGenerator(
            output_path=os.path.join(output_dir, "deal_log.xlsx")
        ).generate(deal)
        logger.info(f"  Excel: {excel_path}")
    except Exception as e:
        logger.error(f"Excel generation failed: {e}", exc_info=True)

    result = {
        "deal_id": deal.deal_id,
        "property_name": deal.property_name,
        "recommendation": deal.recommendation,
        "score_total": deal.score_total,
        "flags": deal.score_flags,
        "investment_thesis": deal.investment_thesis,
        "pdf_path": pdf_path,
        "excel_path": excel_path,
    }

    logger.info(f"=== Deal {deal_id} complete: {deal.recommendation} ({deal.score_total}%) ===")
    return result


def main():
    parser = argparse.ArgumentParser(description="Industrial Deal Review — CLI")
    parser.add_argument(
        "--subject", "-s", required=True,
        help="Email subject line (used as initial property name)"
    )
    parser.add_argument(
        "--attachments", "-a", nargs="*", default=[],
        help="Paths to attachment files (PDFs, Excel, images)"
    )
    parser.add_argument(
        "--body", "-b", default="",
        help="Optional email body text"
    )
    parser.add_argument(
        "--output-dir", "-o", default=OUTPUT_DIR,
        help=f"Output directory (default: {OUTPUT_DIR})"
    )
    args = parser.parse_args()

    result = process_deal(
        subject=args.subject,
        attachment_paths=args.attachments,
        email_body=args.body,
        output_dir=args.output_dir,
    )

    print("\n" + "=" * 60)
    print(f"Deal ID:        {result['deal_id']}")
    print(f"Property:       {result['property_name']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Score:          {result['score_total']}%")
    if result['flags']:
        print("Flags:")
        for f in result['flags']:
            print(f"  • {f}")
    if result['pdf_path']:
        print(f"PDF Report:     {result['pdf_path']}")
    if result['excel_path']:
        print(f"Excel Log:      {result['excel_path']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
