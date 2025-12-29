"""Services package for social module infrastructure."""

from app.modules.social.infrastructure.services.search_quota_service import (
    SearchQuotaModel,
    SearchQuotaService,
)

__all__ = ["SearchQuotaService", "SearchQuotaModel"]
