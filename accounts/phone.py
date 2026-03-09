import re

AFRICAN_COUNTRY_CALLING_CODES = {
    "20", "211", "212", "213", "216", "218", "220", "221", "222", "223", "224",
    "225", "226", "227", "228", "229", "230", "231", "232", "233", "234", "235",
    "236", "237", "238", "239", "240", "241", "242", "243", "244", "245", "246",
    "248", "249", "250", "251", "252", "253", "254", "255", "256", "257", "258",
    "260", "261", "262", "263", "264", "265", "266", "267", "268", "269", "27",
    "290", "291", "297", "298", "299",
}


class PhoneValidationError(ValueError):
    pass



def normalize_phone(phone: str) -> str:
    cleaned = re.sub(r"[\s\-()]+", "", (phone or "").strip())
    if cleaned.startswith("00"):
        cleaned = f"+{cleaned[2:]}"
    return cleaned



def validate_african_phone(phone: str) -> str:
    normalized = normalize_phone(phone)

    if not normalized.startswith("+"):
        raise PhoneValidationError("Use international format with country code, e.g. +2557XXXXXXXX.")

    if not re.fullmatch(r"\+[1-9]\d{8,14}", normalized):
        raise PhoneValidationError("Enter a valid international phone number.")

    digits = normalized[1:]
    if not any(digits.startswith(code) for code in sorted(AFRICAN_COUNTRY_CALLING_CODES, key=len, reverse=True)):
        raise PhoneValidationError("Only African country phone numbers are allowed.")

    return normalized
