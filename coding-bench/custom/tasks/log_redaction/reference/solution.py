import re


def _mask_email(match):
    name, domain = match.group(1), match.group(2)
    return f"{name[:1]}***@{domain}"


def _mask_key(match):
    value = match.group(0)
    return f"{value[:3]}...{value[-4:]}"


def _mask_card(match):
    value = match.group(0)
    return f"{value[:4]}********{value[-4:]}"


def redact(text):
    text = re.sub(r"\b([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b", _mask_email, text)
    text = re.sub(r"Bearer\s+[A-Za-z0-9._-]+", "Bearer [REDACTED]", text)
    text = re.sub(r"\bsk-[A-Za-z0-9]{12,}\b", _mask_key, text)
    text = re.sub(r"\b\d{16}\b", _mask_card, text)
    return text
