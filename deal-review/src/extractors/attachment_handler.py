import logging
import os
from pathlib import Path
from typing import Optional

from .brochure_extractor import BrochureExtractor
from .green_street_extractor import GreenStreetExtractor
from .market_data_extractor import MarketDataExtractor
from .site_plan_extractor import SitePlanExtractor
from .underwriting_extractor import UnderwritingExtractor

logger = logging.getLogger(__name__)

IMAGE_MEDIA_TYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "tiff": "image/tiff",
    "webp": "image/webp",
}


def classify_and_extract(file_path: str) -> tuple[dict, str]:
    """
    Given a path to an attachment file, classify it and run the
    appropriate extractor. Returns (extracted_dict, source_label).

    source_label is "uw" for underwriting models (triggers force-overwrite
    on DealRecord financial fields) or a descriptive string otherwise.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Attachment not found: {file_path}")

    content = path.read_bytes()
    name_lower = path.name.lower()
    ext = path.suffix.lstrip(".").lower()

    logger.info(f"Processing attachment: {path.name} ({len(content):,} bytes)")

    if ext == "pdf":
        extractor, source = _classify_pdf(name_lower)
        result = extractor.extract_from_pdf(content)

    elif ext in IMAGE_MEDIA_TYPES:
        logger.info(f"  → SitePlanExtractor (image)")
        extractor = SitePlanExtractor()
        source = "site_plan"
        result = extractor.extract_from_image(content, IMAGE_MEDIA_TYPES[ext])

    elif ext in ("xlsx", "xls"):
        extractor, source = _classify_excel(name_lower, content)
        result = extractor.extract_from_excel(content)

    else:
        logger.warning(f"  Unrecognised extension '{ext}', skipping {path.name}")
        return {}, "unknown"

    if "_parse_error" in result:
        logger.warning(f"  Extraction parse error for {path.name}: {result['_parse_error'][:200]}")

    return result, source


def _classify_pdf(name: str) -> tuple:
    if any(kw in name for kw in ("brochure", "om ", "offering", "memo", " om.")):
        logger.info("  → BrochureExtractor (PDF)")
        return BrochureExtractor(), "brochure"
    if any(kw in name for kw in ("site", "plan", "survey", "plat")):
        logger.info("  → SitePlanExtractor (PDF)")
        return SitePlanExtractor(), "site_plan"
    if any(kw in name for kw in ("market", "research", "report", "cbre", "jll", "cushman")):
        logger.info("  → MarketDataExtractor (PDF)")
        return MarketDataExtractor(), "market"
    if any(kw in name for kw in ("model", "uw", "underwrite", "proforma", "pro forma", "pro_forma")):
        logger.info("  → UnderwritingExtractor (PDF)")
        return UnderwritingExtractor(), "uw"
    # Default: treat unknown PDFs as brochures
    logger.info("  → BrochureExtractor (PDF, default fallback)")
    return BrochureExtractor(), "brochure"


def _classify_excel(name: str, content: bytes) -> tuple:
    if any(kw in name for kw in ("green", "gs ", "greenstreet", "green_street")):
        logger.info("  → GreenStreetExtractor (Excel)")
        return GreenStreetExtractor(), "green_street"
    if any(kw in name for kw in ("model", "uw", "underwrite", "proforma", "pro forma", "pro_forma")):
        logger.info("  → UnderwritingExtractor (Excel)")
        return UnderwritingExtractor(), "uw"
    if any(kw in name for kw in ("market", "research", "report")):
        logger.info("  → MarketDataExtractor (Excel)")
        return MarketDataExtractor(), "market"
    # Default Excel fallback: try underwriting
    logger.info("  → UnderwritingExtractor (Excel, default fallback)")
    return UnderwritingExtractor(), "uw"
