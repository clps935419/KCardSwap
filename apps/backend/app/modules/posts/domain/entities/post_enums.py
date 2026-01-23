"""
Post Enums - Category and Scope for V2 Posts

Following spec.md FR-002 (PostCategory) and FR-003 (PostScope)
"""

from enum import Enum


class PostCategory(str, Enum):
    """Post category enumeration (FR-002)"""

    TRADE = "trade"
    GIVEAWAY = "giveaway"
    GROUP = "group"
    SHOWCASE = "showcase"
    HELP = "help"
    ANNOUNCEMENT = "announcement"


class PostScope(str, Enum):
    """Post scope enumeration (FR-003)"""

    GLOBAL = "global"
    CITY = "city"
