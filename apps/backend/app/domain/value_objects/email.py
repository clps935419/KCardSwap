"""
Email Value Object - Immutable email representation
"""
import re


class Email:
    """
    Email value object - immutable and self-validating
    """
    
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def __init__(self, value: str):
        self._value = value.lower().strip()
        self._validate()
    
    def _validate(self):
        """Validate email format"""
        if not self.EMAIL_PATTERN.match(self._value):
            raise ValueError(f"Invalid email format: {self._value}")
    
    @property
    def value(self) -> str:
        return self._value
    
    def __str__(self) -> str:
        return self._value
    
    def __eq__(self, other):
        if not isinstance(other, Email):
            return False
        return self._value == other._value
    
    def __hash__(self):
        return hash(self._value)
    
    def __repr__(self):
        return f"Email({self._value})"
