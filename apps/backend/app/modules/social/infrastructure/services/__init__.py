"""Services package for social module infrastructure."""

from app.modules.social.infrastructure.services.search_quota_service import (
    SearchQuotaService,
    SearchQuotaModel,
)

__all__ = ["SearchQuotaService", "SearchQuotaModel"]
