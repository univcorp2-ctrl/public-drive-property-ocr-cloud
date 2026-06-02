from pathlib import Path

from PIL import Image, UnidentifiedImageError

from app.config import get_settings


def _image_metadata(path: Path) -> str:
    try:
        with Image.open(path) as image:
            return f"画像サイズ: {image.width}x{image.height}px / format={image.format}"
    except (UnidentifiedImageError, OSError):
        return "画像メタ情報: 読み取り不可または画像以外のファイル"


def _try_pytesseract(path: Path) -> str:
    try:
        import pytesseract  # type: ignore[import-not-found]

        with Image.open(path) as image:
            return pytesseract.image_to_string(image, lang="jpn+eng").strip()
    except Exception as exc:  # pragma: no cover - optional integration path
        return f"pytesseract OCR失敗: {exc}"


def extract_text(path: Path, manual_text: str = "") -> str:
    """Extract text from an uploaded file.

    The default engine is deterministic and CI-friendly. Production OCR can be swapped by
    setting OCR_ENGINE=pytesseract and installing the native tesseract runtime, or by replacing
    this module with a cloud OCR adapter.
    """

    settings = get_settings()
    parts: list[str] = []
    cleaned_manual = manual_text.strip()
    if cleaned_manual:
        parts.append(cleaned_manual)

    if settings.ocr_engine.lower() == "pytesseract":
        ocr_text = _try_pytesseract(path)
        if ocr_text:
            parts.append(ocr_text)

    parts.append(_image_metadata(path))

    if not cleaned_manual and settings.ocr_engine.lower() == "fallback":
        parts.append(
            "OCR補助テキストが未入力です。実運用ではGoogle Vision、Azure AI Vision、"
            "AWS Textract、pytesseract等のOCRプロバイダに差し替えてください。"
        )

    return "\n".join(parts)
