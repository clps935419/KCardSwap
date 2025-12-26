"""
Card Validation Service - Domain service for card validation logic
Following DDD principles: Domain logic that doesn't fit in entities
"""

from typing import Set


class CardValidationService:
    """
    Domain service for card validation.
    Contains business rules that span multiple entities or are configuration-driven.
    """

    # Allowed image content types
    ALLOWED_CONTENT_TYPES: Set[str] = {
        "image/jpeg",
        "image/png",
    }

    # File extension mapping
    CONTENT_TYPE_EXTENSIONS = {
        "image/jpeg": [".jpg", ".jpeg"],
        "image/png": [".png"],
    }

    def validate_content_type(self, content_type: str) -> bool:
        """
        Validate if content type is allowed for card images.

        Args:
            content_type: MIME type of the file

        Returns:
            True if valid, False otherwise
        """
        return content_type.lower() in self.ALLOWED_CONTENT_TYPES

    def validate_file_size(self, size_bytes: int, max_size_bytes: int) -> bool:
        """
        Validate if file size is within limits.

        Args:
            size_bytes: Size of file in bytes
            max_size_bytes: Maximum allowed size

        Returns:
            True if valid, False otherwise
        """
        return 0 < size_bytes <= max_size_bytes

    def get_file_extension(self, content_type: str) -> str:
        """
        Get appropriate file extension for content type.

        Args:
            content_type: MIME type

        Returns:
            File extension (e.g., ".jpg")

        Raises:
            ValueError: If content type is not supported
        """
        content_type = content_type.lower()
        if content_type not in self.CONTENT_TYPE_EXTENSIONS:
            raise ValueError(f"Unsupported content type: {content_type}")

        # Return first extension in the list
        return self.CONTENT_TYPE_EXTENSIONS[content_type][0]

    def validate_upload_request(
        self,
        content_type: str,
        file_size_bytes: int,
        max_file_size_bytes: int,
    ) -> tuple[bool, str]:
        """
        Validate an upload request.

        Args:
            content_type: MIME type of the file
            file_size_bytes: Size of file in bytes
            max_file_size_bytes: Maximum allowed size

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check content type
        if not self.validate_content_type(content_type):
            allowed = ", ".join(self.ALLOWED_CONTENT_TYPES)
            return False, f"Invalid content type. Allowed: {allowed}"

        # Check file size
        if not self.validate_file_size(file_size_bytes, max_file_size_bytes):
            max_mb = max_file_size_bytes / (1024 * 1024)
            return False, f"File size exceeds limit of {max_mb:.1f}MB"

        return True, ""
