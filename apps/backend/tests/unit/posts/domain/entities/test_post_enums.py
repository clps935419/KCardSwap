"""
Unit tests for Post Enums

Tests the post category and scope enums.
"""

import pytest

from app.modules.posts.domain.entities.post_enums import PostCategory, PostScope


class TestPostCategory:
    """Test PostCategory enum"""

    def test_all_categories_exist(self):
        """Test that all categories are defined"""
        # Assert
        assert PostCategory.TRADE == "trade"
        assert PostCategory.GIVEAWAY == "giveaway"
        assert PostCategory.GROUP == "group"
        assert PostCategory.SHOWCASE == "showcase"
        assert PostCategory.HELP == "help"
        assert PostCategory.ANNOUNCEMENT == "announcement"

    def test_category_from_string(self):
        """Test creating category from string"""
        # Act & Assert
        assert PostCategory("trade") == PostCategory.TRADE
        assert PostCategory("giveaway") == PostCategory.GIVEAWAY
        assert PostCategory("group") == PostCategory.GROUP

    def test_category_value(self):
        """Test getting category value"""
        # Act & Assert
        assert PostCategory.TRADE.value == "trade"
        assert PostCategory.SHOWCASE.value == "showcase"

    def test_category_invalid_value(self):
        """Test that invalid value raises error"""
        # Act & Assert
        with pytest.raises(ValueError):
            PostCategory("invalid_category")

    def test_category_list_all(self):
        """Test listing all categories"""
        # Act
        categories = list(PostCategory)

        # Assert
        assert len(categories) == 6
        assert PostCategory.TRADE in categories
        assert PostCategory.GIVEAWAY in categories
        assert PostCategory.GROUP in categories
        assert PostCategory.SHOWCASE in categories
        assert PostCategory.HELP in categories
        assert PostCategory.ANNOUNCEMENT in categories

    def test_category_equality(self):
        """Test category equality"""
        # Assert
        assert PostCategory.TRADE == PostCategory.TRADE
        assert PostCategory.TRADE != PostCategory.GIVEAWAY

    def test_category_is_string(self):
        """Test that category inherits from str"""
        # Assert
        assert isinstance(PostCategory.TRADE, str)
        assert isinstance(PostCategory.GIVEAWAY.value, str)

    def test_category_in_list(self):
        """Test checking if category is in list"""
        # Arrange
        valid_categories = [PostCategory.TRADE, PostCategory.GIVEAWAY]

        # Act & Assert
        assert PostCategory.TRADE in valid_categories
        assert PostCategory.SHOWCASE not in valid_categories


class TestPostScope:
    """Test PostScope enum"""

    def test_all_scopes_exist(self):
        """Test that all scopes are defined"""
        # Assert
        assert PostScope.GLOBAL == "global"
        assert PostScope.CITY == "city"

    def test_scope_from_string(self):
        """Test creating scope from string"""
        # Act & Assert
        assert PostScope("global") == PostScope.GLOBAL
        assert PostScope("city") == PostScope.CITY

    def test_scope_value(self):
        """Test getting scope value"""
        # Act & Assert
        assert PostScope.GLOBAL.value == "global"
        assert PostScope.CITY.value == "city"

    def test_scope_invalid_value(self):
        """Test that invalid value raises error"""
        # Act & Assert
        with pytest.raises(ValueError):
            PostScope("invalid_scope")

    def test_scope_list_all(self):
        """Test listing all scopes"""
        # Act
        scopes = list(PostScope)

        # Assert
        assert len(scopes) == 2
        assert PostScope.GLOBAL in scopes
        assert PostScope.CITY in scopes

    def test_scope_equality(self):
        """Test scope equality"""
        # Assert
        assert PostScope.GLOBAL == PostScope.GLOBAL
        assert PostScope.GLOBAL != PostScope.CITY

    def test_scope_is_string(self):
        """Test that scope inherits from str"""
        # Assert
        assert isinstance(PostScope.GLOBAL, str)
        assert isinstance(PostScope.CITY.value, str)

    def test_scope_in_conditional(self):
        """Test using scope in conditional"""
        # Arrange
        scope = PostScope.GLOBAL

        # Act & Assert
        if scope == PostScope.GLOBAL:
            assert True
        else:
            assert False, "Scope should be GLOBAL"


class TestPostEnumsIntegration:
    """Test integration between enums"""

    def test_category_and_scope_combinations(self):
        """Test valid combinations of category and scope"""
        # Arrange
        valid_combinations = [
            (PostCategory.TRADE, PostScope.CITY),
            (PostCategory.TRADE, PostScope.GLOBAL),
            (PostCategory.SHOWCASE, PostScope.GLOBAL),
            (PostCategory.GROUP, PostScope.CITY),
        ]

        # Act & Assert
        for category, scope in valid_combinations:
            assert isinstance(category, PostCategory)
            assert isinstance(scope, PostScope)

    def test_enums_are_different_types(self):
        """Test that PostCategory and PostScope are different types"""
        # Assert
        assert PostCategory.TRADE != PostScope.GLOBAL
        assert type(PostCategory.TRADE) != type(PostScope.GLOBAL)
