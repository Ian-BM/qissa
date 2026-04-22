import re

AFRICAN_COUNTRY_CALLING_CODES = {
    "20", "211", "212", "213", "216", "218", "220", "221", "222", "223", "224",
    "225", "226", "227", "228", "229", "230", "231", "232", "233", "234", "235",
    "236", "237", "238", "239", "240", "241", "242", "243", "244", "245", "246",
    "248", "249", "250", "251", "252", "253", "254", "255", "256", "257", "258",
    "260", "261", "262", "263", "264", "265", "266", "267", "268", "269", "27",
    "290", "291", "297", "298", "299",
}

EAST_AFRICAN_COUNTRY_CHOICES = (
    ("+255", "Tanzania (+255)"),
    ("+254", "Kenya (+254)"),
    ("+256", "Uganda (+256)"),
    ("+250", "Rwanda (+250)"),
    ("+257", "Burundi (+257)"),
    ("+211", "South Sudan (+211)"),
    ("+251", "Ethiopia (+251)"),
    ("+252", "Somalia (+252)"),
    ("+253", "Djibouti (+253)"),
    ("+291", "Eritrea (+291)"),
    ("+243", "DR Congo (+243)"),
)

EAST_AFRICAN_COUNTRY_CODES = {code[1:] for code, _ in EAST_AFRICAN_COUNTRY_CHOICES}


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


def validate_east_african_phone(country_code: str, local_number: str) -> str:
    normalized_code = normalize_phone(country_code)
    if not re.fullmatch(r"\+[1-9]\d{1,3}", normalized_code):
        raise PhoneValidationError("Select a valid country code.")

    if normalized_code[1:] not in EAST_AFRICAN_COUNTRY_CODES:
        raise PhoneValidationError("Select an East African country code.")

    cleaned_local = re.sub(r"[\s\-()]+", "", (local_number or "").strip())
    if not cleaned_local:
        raise PhoneValidationError("Enter your phone number.")

    if cleaned_local.startswith("+") or cleaned_local.startswith("00"):
        raise PhoneValidationError("Enter the phone number without country code.")

    if cleaned_local.startswith("0"):
        cleaned_local = cleaned_local[1:]

    if not re.fullmatch(r"[1-9]\d{5,12}", cleaned_local):
        raise PhoneValidationError("Enter a valid phone number.")

    return validate_african_phone(f"{normalized_code}{cleaned_local}")