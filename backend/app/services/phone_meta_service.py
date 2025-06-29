import phonenumbers
from phonenumbers import carrier, geocoder, number_type, PhoneNumberType


def parse_phone(number: str) -> dict:
    """Return basic metadata about a phone number using phonenumbers."""
    data = {
        "phone": number,
        "valid": False,
        "country": "Unknown",
        "carrier": None,
        "line_type": None,
    }
    try:
        parsed = phonenumbers.parse(number, None)
        data["valid"] = phonenumbers.is_valid_number(parsed)
        data["country"] = geocoder.description_for_number(parsed, "en")
        data["carrier"] = carrier.name_for_number(parsed, "en") or None
        type_enum = number_type(parsed)
        data["line_type"] = PhoneNumberType._VALUES_TO_NAMES.get(type_enum)
    except phonenumbers.NumberParseException:
        pass
    return data
