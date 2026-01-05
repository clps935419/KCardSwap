# FastAPI DI 模式說明

## 問題說明

在 `nearby_router.py` 中有 2 個對 Identity 模組的引用（line 56-60），這些引用是 **FastAPI 依賴注入模式** 的正常使用方式。

## 程式碼分析

```python
async def get_profile_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> IProfileQueryService:
    """Dependency: Get profile query service"""
    # Import here to avoid circular dependency
    from app.modules.identity.application.services.profile_query_service_impl import (
        ProfileQueryServiceImpl,
    )
    from app.modules.identity.infrastructure.repositories.profile_repository_impl import (
        ProfileRepositoryImpl,
    )
    
    profile_repo = ProfileRepositoryImpl(session)
    return ProfileQueryServiceImpl(profile_repository=profile_repo)
```

## 為什麼這是可接受的？

### 1. 遵循依賴反轉原則 (Dependency Inversion Principle)
- **返回型別**: `IProfileQueryService` (介面)
- **消費者**: 只依賴介面，不依賴具體實作
- **符合 DIP**: 高層模組（Social router）依賴抽象（介面），不依賴細節（實作）

### 2. FastAPI 的依賴注入模式
這是 FastAPI 推薦的 dependency provider pattern：
```python
# Router 端點使用
@router.put("/location")
async def update_user_location(
    profile_service: Annotated[IProfileQueryService, Depends(get_profile_service)],
):
    # 這裡只看到介面，不知道具體實作
    await profile_service.update_user_location(...)
```

### 3. Import 放在函數內部
```python
# Import here to avoid circular dependency
from app.modules.identity.application.services...
```
- **原因**: 避免模組層級的循環依賴
- **好處**: 延遲載入，只在需要時才 import
- **慣例**: FastAPI 和 Python 社群的常見做法

## 與直接依賴的差異

### ❌ 不良做法（直接依賴）
```python
# 在 Social use case 中直接使用 Identity 的 repository
from app.modules.identity.infrastructure.repositories.subscription_repository_impl import SubscriptionRepositoryImpl

class SomeUseCase:
    def __init__(self):
        self.subscription_repo = SubscriptionRepositoryImpl(session)  # 直接依賴實作
```

### ✅ 良好做法（依賴介面）
```python
# 在 Social use case 中依賴介面
from app.shared.domain.contracts.i_subscription_query_service import ISubscriptionQueryService

class SomeUseCase:
    def __init__(self, subscription_service: ISubscriptionQueryService):  # 依賴介面
        self.subscription_service = subscription_service
```

## 架構層級分析

```
┌─────────────────────────────────────────────┐
│ Social Module (Presentation Layer)         │
│                                             │
│  Router → 使用 IProfileQueryService 介面    │
│              ↓                              │
│  FastAPI DI provider 函數                   │
│  - 組裝實作 (ProfileQueryServiceImpl)       │
│  - 返回介面型別                              │
└─────────────────────────────────────────────┘
                    ↓ 依賴介面
┌─────────────────────────────────────────────┐
│ Shared Layer (Contracts)                    │
│                                             │
│  IProfileQueryService 介面定義              │
└─────────────────────────────────────────────┘
                    ↑ 實作介面
┌─────────────────────────────────────────────┐
│ Identity Module (Application Layer)         │
│                                             │
│  ProfileQueryServiceImpl 服務實作           │
└─────────────────────────────────────────────┘
```

## 總結

這 2 個引用是：
1. ✅ **符合 DDD 原則** - 透過介面通訊
2. ✅ **符合 SOLID 原則** - 依賴反轉
3. ✅ **符合 FastAPI 最佳實踐** - Dependency injection pattern
4. ✅ **不違反模組邊界** - Social 模組只依賴 shared 契約
5. ✅ **組裝在正確位置** - Presentation layer 負責組裝依賴

## 比較：可接受 vs 技術債

| 項目 | nearby_router.py (可接受) | card_repository_impl.py (技術債) |
|------|---------------------------|----------------------------------|
| 層級 | Presentation (組裝層) | Infrastructure (資料層) |
| 引用類型 | Application Service | Database Model |
| 返回型別 | 介面 (IProfileQueryService) | 無 (直接 join) |
| 影響範圍 | 僅組裝邏輯 | 資料查詢邏輯 |
| 可測試性 | ✅ 高（可 mock 介面） | ⚠️ 低（硬編碼 join） |
| 可維護性 | ✅ 高 | ⚠️ 低 |
| 優先級 | ✅ 無需修改 | ⚠️ 建議重構 |

## 如果要進一步改進

可以將 provider 函數移到 shared 層或使用全域 DI 容器：

### Option 1: 移到 shared layer
```python
# app/shared/presentation/dependencies/services.py
async def get_profile_service(session: AsyncSession) -> IProfileQueryService:
    from app.modules.identity.application.services...
    profile_repo = ProfileRepositoryImpl(session)
    return ProfileQueryServiceImpl(profile_repository=profile_repo)

# Social router 使用
from app.shared.presentation.dependencies.services import get_profile_service
```

### Option 2: 使用全域 injector
```python
# 使用 app/injector.py 中的全域 injector
from app.injector import injector

async def get_profile_service(session: AsyncSession) -> IProfileQueryService:
    return injector.get(IProfileQueryService)
```

但這些改進是「錦上添花」，當前實作已經是良好的架構設計。
