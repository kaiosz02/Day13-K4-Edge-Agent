from __future__ import annotations

import hashlib
import re

PII_PATTERNS: dict[str, str] = {
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    "phone_vn": r"(?<!\d)(?:\+84|0)(?:[ .-]?\d){9}(?!\d)",
    "cccd": r"\b\d{12}\b",
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    # Passport Việt Nam: bắt đầu bằng chữ cái + 8 chữ số
    "passport": r"\b[A-Z]{1,2}\d{7,8}\b",
    # Địa chỉ Việt Nam chứa từ khoá nhạy cảm kèm số
    "vn_address": r"(?i)(?:số\s+\d+[,\s]|đường\s+[\w\s]{2,30}(?:,|phường|quận|huyện|tỉnh|thành\s*phố))",
    # Ngày sinh dạng DD/MM/YYYY hoặc DD-MM-YYYY
    "date_of_birth": r"\b(?:0[1-9]|[12]\d|3[01])[/\-](?:0[1-9]|1[0-2])[/\-](?:19|20)\d{2}\b",
}


def scrub_text(text: str) -> str:
    safe = text
    for name, pattern in PII_PATTERNS.items():
        safe = re.sub(pattern, f"[REDACTED_{name.upper()}]", safe)
    return safe


def summarize_text(text: str, max_len: int = 80) -> str:
    safe = scrub_text(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")


def hash_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]
