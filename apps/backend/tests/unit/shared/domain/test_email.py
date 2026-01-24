"""
Unit tests for Email Value Object
Testing email validation, normalization, and equality
"""

import pytest

from app.shared.domain.email import Email


class TestEmailCreation:
    """Test email value object creation"""

    def test_create_valid_email(self):
        """Test creating email with valid address"""
        email = Email("test@example.com")

        assert email.value == "test@example.com"

    def test_create_email_with_uppercase(self):
        """Test that email is normalized to lowercase"""
        email = Email("TEST@EXAMPLE.COM")

        assert email.value == "test@example.com"

    def test_create_email_with_spaces(self):
        """Test that spaces are stripped"""
        email = Email("  test@example.com  ")

        assert email.value == "test@example.com"

    def test_create_email_with_plus_sign(self):
        """Test email with plus sign"""
        email = Email("test+tag@example.com")

        assert email.value == "test+tag@example.com"

    def test_create_email_with_dots(self):
        """Test email with dots in local part"""
        email = Email("first.last@example.com")

        assert email.value == "first.last@example.com"

    def test_create_email_with_subdomain(self):
        """Test email with subdomain"""
        email = Email("test@mail.example.com")

        assert email.value == "test@mail.example.com"

    def test_create_email_with_numbers(self):
        """Test email with numbers"""
        email = Email("user123@example123.com")

        assert email.value == "user123@example123.com"

    def test_create_email_with_hyphens(self):
        """Test email with hyphens in domain"""
        email = Email("test@my-domain.com")

        assert email.value == "test@my-domain.com"


class TestEmailValidation:
    """Test email validation rules"""

    def test_empty_email_raises_error(self):
        """Test that empty email raises ValueError"""
        with pytest.raises(ValueError, match="Email cannot be empty"):
            Email("")

    def test_email_without_at_sign_raises_error(self):
        """Test that email without @ raises ValueError"""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("testexample.com")

    def test_email_without_domain_raises_error(self):
        """Test that email without domain raises ValueError"""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("test@")

    def test_email_without_local_part_raises_error(self):
        """Test that email without local part raises ValueError"""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("@example.com")

    def test_email_without_tld_raises_error(self):
        """Test that email without TLD raises ValueError"""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("test@example")

    def test_email_with_single_char_tld_raises_error(self):
        """Test that single character TLD is invalid"""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("test@example.c")

    def test_email_with_spaces_in_middle_raises_error(self):
        """Test that spaces in middle of email raise ValueError"""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("test @example.com")

        with pytest.raises(ValueError, match="Invalid email format"):
            Email("test@ example.com")

    def test_email_with_invalid_characters_raises_error(self):
        """Test that invalid characters raise ValueError"""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("test!#$@example.com")

    def test_email_with_multiple_at_signs_raises_error(self):
        """Test that multiple @ signs raise ValueError"""
        with pytest.raises(ValueError, match="Invalid email format"):
            Email("test@@example.com")


class TestEmailEquality:
    """Test email equality and hashing"""

    def test_emails_with_same_value_are_equal(self):
        """Test that emails with same value are equal"""
        email1 = Email("test@example.com")
        email2 = Email("test@example.com")

        assert email1 == email2

    def test_emails_case_insensitive_equality(self):
        """Test that email equality is case insensitive"""
        email1 = Email("Test@Example.COM")
        email2 = Email("test@example.com")

        assert email1 == email2

    def test_emails_with_different_values_are_not_equal(self):
        """Test that emails with different values are not equal"""
        email1 = Email("test1@example.com")
        email2 = Email("test2@example.com")

        assert email1 != email2

    def test_email_not_equal_to_non_email(self):
        """Test that email is not equal to non-email object"""
        email = Email("test@example.com")

        assert email != "test@example.com"
        assert email != 123
        assert email != None

    def test_email_hash(self):
        """Test that email can be hashed"""
        email = Email("test@example.com")

        # Should not raise
        hash(email)

    def test_emails_with_same_value_have_same_hash(self):
        """Test that emails with same value have same hash"""
        email1 = Email("test@example.com")
        email2 = Email("TEST@EXAMPLE.COM")

        assert hash(email1) == hash(email2)

    def test_email_can_be_used_in_set(self):
        """Test that email can be used in a set"""
        email1 = Email("test1@example.com")
        email2 = Email("test2@example.com")
        email3 = Email("TEST1@EXAMPLE.COM")  # Same as email1

        email_set = {email1, email2, email3}

        assert len(email_set) == 2  # email3 is duplicate of email1
        assert email1 in email_set
        assert email2 in email_set

    def test_email_can_be_used_as_dict_key(self):
        """Test that email can be used as a dictionary key"""
        email1 = Email("test1@example.com")
        email2 = Email("test2@example.com")

        email_dict = {email1: "value1", email2: "value2"}

        assert email_dict[email1] == "value1"
        assert email_dict[email2] == "value2"


class TestEmailRepresentation:
    """Test email string representations"""

    def test_email_str(self):
        """Test __str__ method returns email value"""
        email = Email("test@example.com")

        assert str(email) == "test@example.com"

    def test_email_repr(self):
        """Test __repr__ method"""
        email = Email("test@example.com")

        repr_str = repr(email)

        assert "Email" in repr_str
        assert "test@example.com" in repr_str


class TestEmailProperties:
    """Test email property access"""

    def test_value_property(self):
        """Test accessing email value through property"""
        email = Email("test@example.com")

        assert email.value == "test@example.com"

    def test_value_property_is_readonly(self):
        """Test that email value cannot be modified"""
        email = Email("test@example.com")

        with pytest.raises(AttributeError):
            email.value = "new@example.com"


class TestEmailEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_email_with_very_long_local_part(self):
        """Test email with long local part (valid)"""
        local_part = "a" * 64
        email = Email(f"{local_part}@example.com")

        assert email.value == f"{local_part}@example.com"

    def test_email_with_very_long_domain(self):
        """Test email with long domain (valid)"""
        domain = "a" * 63
        email = Email(f"test@{domain}.com")

        assert email.value == f"test@{domain}.com"

    def test_email_with_two_char_tld(self):
        """Test email with two character TLD (minimum valid)"""
        email = Email("test@example.co")

        assert email.value == "test@example.co"

    def test_email_with_multiple_subdomains(self):
        """Test email with multiple subdomains"""
        email = Email("test@mail.service.example.com")

        assert email.value == "test@mail.service.example.com"
