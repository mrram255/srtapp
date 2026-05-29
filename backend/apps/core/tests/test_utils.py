import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.core.utils import (
    generate_unique_code,
    format_indian_currency,
    calculate_age,
    mask_aadhaar,
    get_client_ip,
    generate_qr_code,
)


class GenerateUniqueCodeTest(TestCase):
    def test_generates_code_with_prefix(self):
        code = generate_unique_code("ENR", 6)
        self.assertTrue(code.startswith("ENR"))

    def test_generated_code_is_string(self):
        code = generate_unique_code("TEST", 8)
        self.assertIsInstance(code, str)

    def test_two_codes_are_different(self):
        code1 = generate_unique_code("A", 8)
        code2 = generate_unique_code("A", 8)
        self.assertNotEqual(code1, code2)

    def test_prefix_appears_in_code(self):
        code = generate_unique_code("ENRL", 4)
        self.assertIn("ENRL", code)

    def test_code_is_not_empty(self):
        code = generate_unique_code("X", 6)
        self.assertTrue(len(code) > 0)


class FormatIndianCurrencyTest(TestCase):
    def test_formats_large_number(self):
        result = format_indian_currency(123456)
        self.assertIn("₹", result)
        self.assertIn("1,23,456", result)

    def test_formats_zero(self):
        result = format_indian_currency(0)
        self.assertIn("0", result)

    def test_formats_decimal(self):
        result = format_indian_currency(Decimal("1234.50"))
        self.assertIn("₹", result)

    def test_formats_string_amount(self):
        result = format_indian_currency("5000")
        self.assertIn("₹", result)

    def test_formats_one_lakh(self):
        result = format_indian_currency(100000)
        self.assertIn("1,00,000", result)

    def test_formats_ten_rupees(self):
        result = format_indian_currency(10)
        self.assertIn("10", result)


class CalculateAgeTest(TestCase):
    def test_calculate_age_twenty_years(self):
        dob = date.today().replace(year=date.today().year - 20)
        age = calculate_age(dob)
        self.assertIn(age, [19, 20])

    def test_calculate_age_newborn(self):
        dob = date.today()
        age = calculate_age(dob)
        self.assertEqual(age, 0)

    def test_calculate_age_returns_int(self):
        dob = date(2000, 1, 1)
        age = calculate_age(dob)
        self.assertIsInstance(age, int)

    def test_calculate_age_is_positive(self):
        dob = date(1990, 6, 15)
        age = calculate_age(dob)
        self.assertGreater(age, 0)

    def test_calculate_age_specific_year(self):
        dob = date(2000, 1, 1)
        age = calculate_age(dob)
        self.assertGreaterEqual(age, 24)


class MaskAadhaarTest(TestCase):
    def test_masks_valid_12_digit_aadhaar(self):
        result = mask_aadhaar("123456781234")
        self.assertEqual(result, "XXXX-XXXX-1234")

    def test_masked_shows_last_4(self):
        result = mask_aadhaar("999988881234")
        self.assertIn("1234", result)

    def test_masked_hides_first_8(self):
        result = mask_aadhaar("123456789012")
        self.assertNotIn("12345678", result)
        self.assertIn("XXXX", result)

    def test_valid_aadhaar_returns_string(self):
        result = mask_aadhaar("123456789012")
        self.assertIsInstance(result, str)

    def test_invalid_aadhaar_raises_validation_error(self):
        """Short aadhaar should raise ValidationError — this is correct behavior"""
        with self.assertRaises(ValidationError):
            mask_aadhaar("1234")

    def test_non_12_digit_raises_error(self):
        with self.assertRaises(ValidationError):
            mask_aadhaar("123")


class GetClientIPTest(TestCase):
    def test_gets_ip_from_remote_addr(self):
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get("/")
        request.META["REMOTE_ADDR"] = "192.168.1.1"
        ip = get_client_ip(request)
        self.assertEqual(ip, "192.168.1.1")

    def test_gets_ip_from_forwarded_header(self):
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get("/")
        request.META["HTTP_X_FORWARDED_FOR"] = "10.0.0.1, 192.168.1.1"
        ip = get_client_ip(request)
        self.assertEqual(ip, "10.0.0.1")

    def test_returns_string_or_none(self):
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get("/")
        ip = get_client_ip(request)
        self.assertTrue(ip is None or isinstance(ip, str))


class GenerateQRCodeTest(TestCase):
    def test_generates_qr_bytes(self):
        data = "https://srtapp.example.com/verify/ABC123"
        result = generate_qr_code(data)
        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 0)

    def test_qr_code_not_empty(self):
        result = generate_qr_code("test-data-123")
        self.assertTrue(len(result) > 100)

    def test_different_data_different_qr(self):
        r1 = generate_qr_code("data-one")
        r2 = generate_qr_code("data-two")
        self.assertNotEqual(r1, r2)
