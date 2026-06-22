from django.test import TestCase

from .phone import (
    PhoneValidationError,
    normalize_phone,
    phone_lookup_variants,
    validate_phone,
)


class PhoneValidationTests(TestCase):
    def test_normalize_strips_spaces(self):
        self.assertEqual(normalize_phone(" 0754 938 633 "), "0754938633")

    def test_convert_00_prefix(self):
        self.assertEqual(validate_phone("00254712345678"), "+254712345678")

    def test_accept_local_number_without_country_code(self):
        self.assertEqual(validate_phone("0754938633"), "0754938633")

    def test_accept_international_number(self):
        self.assertEqual(validate_phone("+255754938633"), "+255754938633")

    def test_reject_invalid_number(self):
        with self.assertRaises(PhoneValidationError):
            validate_phone("123")

    def test_reject_non_african_country_code(self):
        with self.assertRaises(PhoneValidationError):
            validate_phone("+447911123456")

    def test_phone_lookup_variants_from_local(self):
        self.assertEqual(
            phone_lookup_variants("0754938633"),
            ["0754938633", "+255754938633"],
        )

    def test_phone_lookup_variants_from_international(self):
        self.assertEqual(
            phone_lookup_variants("+255754938633"),
            ["+255754938633", "0754938633"],
        )
