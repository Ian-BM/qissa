from django.test import TestCase

from .phone import PhoneValidationError, normalize_phone, validate_african_phone


class PhoneValidationTests(TestCase):
    def test_normalize_keeps_e164(self):
        self.assertEqual(normalize_phone(" +255 712-345-678 "), "+255712345678")

    def test_convert_00_prefix(self):
        self.assertEqual(validate_african_phone("00254712345678"), "+254712345678")

    def test_reject_without_country_code(self):
        with self.assertRaises(PhoneValidationError):
            validate_african_phone("0712345678")

    def test_reject_non_african_country_code(self):
        with self.assertRaises(PhoneValidationError):
            validate_african_phone("+447911123456")
