from app.config import get_settings


def normalize_note_id(note_id: str) -> str:
    return note_id.strip()


def is_note_id_allowed(note_id: str) -> bool:
    settings = get_settings()
    normalized = normalize_note_id(note_id)
    if not normalized:
        return False
    if settings.note_auth_mode.lower() == "open":
        return True
    return normalized in settings.allowlist
