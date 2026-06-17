from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
from typing import Iterable

from PIL import Image, ImageFilter, ImageOps, UnidentifiedImageError

SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".txt"}


@dataclass(slots=True)
class OcrRecord:
    source_file: str
    file_type: str
    text: str
    property_name: str = ""
    address: str = ""
    price: str = ""
    land_area: str = ""
    building_area: str = ""
    layout: str = ""
    built_date: str = ""
    transport: str = ""
    phone: str = ""
    url: str = ""
    warnings: str = ""

    def to_row(self) -> dict[str, str]:
        return asdict(self)


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[\t\u3000]+", " ", text)
    text = re.sub(r"[ ]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def find_documents(input_dir: Path) -> list[Path]:
    if not input_dir.exists():
        return []
    return sorted(
        path
        for path in input_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def _grab_label_line(text: str, labels: Iterable[str]) -> str:
    for label in labels:
        pattern = rf"(?:^|\n)\s*{label}\s*[:：]?\s*(.+)"
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            value = match.group(1).splitlines()[0].strip(" 　:-：")
            if value:
                return value
    return ""


def _first_regex(text: str, patterns: Iterable[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip(" 　:-：")
    return ""


def extract_property_fields(text: str) -> dict[str, str]:
    """Extract common real-estate fields using conservative regex rules."""
    compact = normalize_text(text)

    property_name = _grab_label_line(compact, ["物件名", "名称", "建物名", "マンション名"])
    address = _grab_label_line(compact, ["所在地", "住所", "所在地住所"])
    transport = _grab_label_line(compact, ["交通", "アクセス", "最寄駅", "沿線"])
    layout = _grab_label_line(compact, ["間取り", "間取"])
    built_date = _grab_label_line(compact, ["築年月", "建築年月", "完成年月", "竣工"])

    price = _grab_label_line(compact, ["価格", "販売価格", "賃料", "月額賃料"])
    if not price:
        price = _first_regex(
            compact,
            [
                r"([0-9０-９][0-9０-９,，.]*\s*(?:万円|円|千円))",
                r"((?:税込|税別)?\s*[0-9０-９][0-9０-９,，.]*\s*万)",
            ],
        )

    land_area = _grab_label_line(compact, ["土地面積", "敷地面積"])
    if not land_area:
        land_area = _first_regex(compact, [r"土地面積\s*[:：]?\s*([0-9０-９,.]+\s*(?:㎡|m2|m²|坪))"])

    building_area = _grab_label_line(compact, ["建物面積", "延床面積", "専有面積"])
    if not building_area:
        building_area = _first_regex(
            compact,
            [r"(?:建物面積|延床面積|専有面積)\s*[:：]?\s*([0-9０-９,.]+\s*(?:㎡|m2|m²|坪))"],
        )

    phone = _first_regex(
        compact,
        [r"((?:0\d{1,4}|０\d{1,4})[-ー−]\d{1,4}[-ー−]\d{3,4})"],
    )
    url = _first_regex(compact, [r"(https?://[^\s\)）]+)"])

    return {
        "property_name": property_name,
        "address": address,
        "price": price,
        "land_area": land_area,
        "building_area": building_area,
        "layout": layout,
        "built_date": built_date,
        "transport": transport,
        "phone": phone,
        "url": url,
    }


def _preprocess_image(image: Image.Image) -> Image.Image:
    image = image.convert("L")
    width, height = image.size
    if max(width, height) < 1800:
        image = image.resize((width * 2, height * 2))
    image = ImageOps.autocontrast(image)
    return image.filter(ImageFilter.SHARPEN)


def _ocr_image_object(image: Image.Image, languages: str) -> str:
    import pytesseract

    processed = _preprocess_image(image)
    return pytesseract.image_to_string(processed, lang=languages, config="--oem 3 --psm 6")


def _ocr_image_file(path: Path, languages: str) -> str:
    with Image.open(path) as image:
        return _ocr_image_object(image, languages)


def _extract_text_pdf(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    parts: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            parts.append(f"\n--- page {index} ---\n{text}")
    return normalize_text("\n".join(parts))


def _ocr_pdf(path: Path, languages: str, max_pages: int) -> str:
    import fitz

    doc = fitz.open(path)
    parts: list[str] = []
    for page_index in range(min(len(doc), max_pages)):
        page = doc[page_index]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        page_text = _ocr_image_object(image, languages)
        if page_text.strip():
            parts.append(f"\n--- ocr page {page_index + 1} ---\n{page_text}")
    return normalize_text("\n".join(parts))


def extract_file(
    path: Path,
    *,
    languages: str = "jpn+eng",
    max_pdf_pages: int = 8,
    enable_ocr: bool = True,
) -> OcrRecord:
    suffix = path.suffix.lower()
    warnings: list[str] = []
    text = ""

    try:
        if suffix == ".txt":
            text = path.read_text(encoding="utf-8", errors="ignore")
        elif suffix == ".pdf":
            try:
                text = _extract_text_pdf(path)
            except Exception as exc:  # noqa: BLE001
                warnings.append(f"pdf_text_failed: {exc}")
            if enable_ocr and len(text.strip()) < 40:
                try:
                    ocr_text = _ocr_pdf(path, languages=languages, max_pages=max_pdf_pages)
                    text = normalize_text("\n".join(part for part in [text, ocr_text] if part))
                except Exception as exc:  # noqa: BLE001
                    warnings.append(f"pdf_ocr_failed: {exc}")
        elif suffix in {".png", ".jpg", ".jpeg", ".tif", ".tiff"}:
            if enable_ocr:
                try:
                    text = _ocr_image_file(path, languages=languages)
                except (UnidentifiedImageError, OSError) as exc:
                    warnings.append(f"image_open_failed: {exc}")
                except Exception as exc:  # noqa: BLE001
                    warnings.append(f"image_ocr_failed: {exc}")
            else:
                warnings.append("ocr_disabled")
        else:
            warnings.append("unsupported_extension")
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"extract_failed: {exc}")

    text = normalize_text(text)
    fields = extract_property_fields(text)
    return OcrRecord(
        source_file=str(path),
        file_type=suffix.lstrip("."),
        text=text,
        warnings="; ".join(warnings),
        **fields,
    )


def extract_documents(
    input_dir: Path,
    *,
    languages: str = "jpn+eng",
    max_pdf_pages: int = 8,
    enable_ocr: bool = True,
) -> list[OcrRecord]:
    records: list[OcrRecord] = []
    for path in find_documents(input_dir):
        records.append(
            extract_file(path, languages=languages, max_pdf_pages=max_pdf_pages, enable_ocr=enable_ocr)
        )
    return records
