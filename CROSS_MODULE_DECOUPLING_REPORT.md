# Cross-Module Dependency Decoupling - Implementation Report

## 執行日期
2026-01-05

## 概述
本次重構完成了 KCardSwap 後端 Identity、Social、Posts 三大模組間的依賴解耦，將直接的 Domain/Infrastructure 依賴改為透過 shared 層的介面契約，並將認證邏輯移至 shared/gateway 層。

## 重構目標
遵循 Domain-Driven Design (DDD) 原則，確保各 Bounded Context 之間的鬆耦合，提升系統的可維護性和可測試性。

## 實施階段

### Phase 1: 盤點現有跨模組依賴 ✅

#### Social → Identity 依賴點
1. `app/modules/social/module.py:9` - 直接實例化 `SubscriptionRepositoryImpl`
2. `app/modules/social/application/use_cases/nearby/update_user_location_use_case.py:7` - 使用 `IProfileRepository`
3. `app/modules/social/infrastructure/repositories/card_repository_impl.py:166` - 直接 join `ProfileModel`
4. `app/modules/social/presentation/routers/nearby_router.py:8,10` - 使用 `IProfileRepository`, `ProfileRepositoryImpl`
5. `app/modules/social/presentation/routers/*.py` (8 routers) - 使用 `get_current_user_id` from Identity

#### Posts → Identity 依賴點
1. `app/modules/posts/module.py:9` - 直接實例化 `SubscriptionRepositoryImpl`
2. `app/modules/posts/application/use_cases/create_post_use_case.py` - 使用 `ISubscriptionRepository`
3. `app/modules/posts/presentation/routers/posts_router.py` - 使用 `get_current_user_id` from Identity

#### Posts → Social 依賴點
1. `app/modules/posts/module.py:39,42` - 直接實例化 `ChatRoomRepositoryImpl`, `FriendshipRepositoryImpl`
2. `app/modules/posts/application/use_cases/accept_interest_use_case.py` - 使用 Social 的 domain entities 和 repositories

### Phase 2: 在 shared 層建立抽象介面 ✅

建立目錄: `app/shared/domain/contracts/`

#### 新增介面契約
1. **ISubscriptionQueryService** (`i_subscription_query_service.py`)
   - `is_user_subscribed(user_id: UUID) -> bool`
   - `get_subscription_info(user_id: UUID) -> Optional[SubscriptionInfo]`
   - DTO: `SubscriptionInfo`

2. **IProfileQueryService** (`i_profile_query_service.py`)
   - `get_user_location(user_id: UUID) -> Optional[UserLocationInfo]`
   - `get_user_profile(user_id: UUID) -> Optional[UserProfileInfo]`
   - `update_user_location(user_id: UUID, lat: float, lng: float) -> bool`
   - DTOs: `UserLocationInfo`, `UserProfileInfo`

3. **IUserBasicInfoService** (`i_user_basic_info_service.py`)
   - `get_user_basic_info(user_id: UUID) -> Optional[UserBasicInfo]`
   - DTO: `UserBasicInfo`

4. **IFriendshipService** (`i_friendship_service.py`)
   - `get_friendship(user_id: UUID, friend_id: UUID) -> Optional[FriendshipDTO]`
   - `are_friends(user_id: UUID, friend_id: UUID) -> bool`
   - `create_friendship(user_id: UUID, friend_id: UUID, auto_accept: bool) -> FriendshipDTO`
   - DTOs: `FriendshipDTO`, `FriendshipStatusDTO`

5. **IChatRoomService** (`i_chat_room_service.py`)
   - `get_or_create_chat_room(user1_id: UUID, user2_id: UUID) -> ChatRoomDTO`
   - `get_chat_room_between_users(user1_id: UUID, user2_id: UUID) -> Optional[ChatRoomDTO]`
   - DTO: `ChatRoomDTO`

### Phase 3: 移動認證依賴到 shared/gateway ✅

#### 新增檔案
- `app/shared/presentation/dependencies/auth.py`
- `app/shared/presentation/dependencies/__init__.py`

#### 移動的功能
```python
# From: app/modules/identity/presentation/dependencies/auth_deps.py
# To: app/shared/presentation/dependencies/auth.py

- get_current_user_id(credentials, jwt_service) -> UUID
- get_current_user(user_id) -> UUID
- get_optional_current_user_id(credentials, jwt_service) -> Optional[UUID]
```

#### 更新的 Routers (9 個)
**Social Module:**
1. `cards_router.py`
2. `chat_router.py`
3. `friends_router.py`
4. `nearby_router.py`
5. `rating_router.py`
6. `report_router.py`
7. `trade_router.py`

**Posts Module:**
8. `posts_router.py`

所有 router 從:
```python
from app.modules.identity.presentation.dependencies.auth_deps import get_current_user_id
```
改為:
```python
from app.shared.presentation.dependencies.auth import get_current_user_id
```

### Phase 4: 在 Identity BC 實作介面 ✅

#### 新增服務實作
目錄: `app/modules/identity/application/services/`

1. **SubscriptionQueryServiceImpl** (`subscription_query_service_impl.py`)
   - 實作 `ISubscriptionQueryService`
   - 依賴: `ISubscriptionRepository`

2. **ProfileQueryServiceImpl** (`profile_query_service_impl.py`)
   - 實作 `IProfileQueryService`
   - 依賴: `IProfileRepository`

3. **UserBasicInfoServiceImpl** (`user_basic_info_service_impl.py`)
   - 實作 `IUserBasicInfoService`
   - 依賴: `IProfileRepository`

#### DI 註冊 (`identity/module.py`)
```python
@provider
def provide_subscription_query_service(
    self, session: AsyncSession
) -> ISubscriptionQueryService:
    subscription_repo = SubscriptionRepositoryImpl(session)
    return SubscriptionQueryServiceImpl(subscription_repository=subscription_repo)

@provider
def provide_profile_query_service(
    self, session: AsyncSession
) -> IProfileQueryService:
    profile_repo = ProfileRepositoryImpl(session)
    return ProfileQueryServiceImpl(profile_repository=profile_repo)

@provider
def provide_user_basic_info_service(
    self, session: AsyncSession
) -> IUserBasicInfoService:
    profile_repo = ProfileRepositoryImpl(session)
    return UserBasicInfoServiceImpl(profile_repository=profile_repo)
```

### Phase 5: 在 Social BC 實作介面 ✅

#### 新增服務實作
目錄: `app/modules/social/application/services/`

1. **FriendshipServiceImpl** (`friendship_service_impl.py`)
   - 實作 `IFriendshipService`
   - 依賴: `IFriendshipRepository`
   - 負責 entity → DTO 轉換

2. **ChatRoomServiceImpl** (`chat_room_service_impl.py`)
   - 實作 `IChatRoomService`
   - 依賴: `IChatRoomRepository`
   - 負責 entity → DTO 轉換

#### DI 註冊 (`social/module.py`)
```python
@provider
def provide_friendship_service(self, session: AsyncSession) -> IFriendshipService:
    friendship_repo = FriendshipRepositoryImpl(session)
    return FriendshipServiceImpl(friendship_repository=friendship_repo)

@provider
def provide_chat_room_service(self, session: AsyncSession) -> IChatRoomService:
    chat_room_repo = ChatRoomRepositoryImpl(session)
    return ChatRoomServiceImpl(chat_room_repository=chat_room_repo)
```

### Phase 6: 重構 Social 模組依賴 ✅

#### 更新的檔案

1. **social/module.py**
   - 移除: `from app.modules.identity.infrastructure.repositories.subscription_repository_impl`
   - 新增: `from app.shared.domain.contracts.i_subscription_query_service`
   - 更新 providers 使用注入的 `ISubscriptionQueryService`

2. **update_user_location_use_case.py**
   ```python
   # Before
   from app.modules.identity.domain.repositories.i_profile_repository import IProfileRepository
   def __init__(self, profile_repository: IProfileRepository)
   
   # After
   from app.shared.domain.contracts.i_profile_query_service import IProfileQueryService
   def __init__(self, profile_service: IProfileQueryService)
   ```

3. **nearby_router.py**
   - 新增 `get_profile_service()` dependency provider
   - 更新使用 `IProfileQueryService` 而非直接 repository

### Phase 7: 重構 Posts 模組依賴 ✅

#### 更新的檔案

1. **posts/module.py**
   - 移除直接實例化 repositories
   - 注入服務介面: `ISubscriptionQueryService`, `IFriendshipService`, `IChatRoomService`

2. **create_post_use_case.py**
   ```python
   # Before
   from app.modules.identity.domain.repositories.i_subscription_repository import ISubscriptionRepository
   subscription = await self.subscription_repository.get_by_user_id(owner_id)
   is_premium = subscription and subscription.is_premium()
   
   # After
   from app.shared.domain.contracts.i_subscription_query_service import ISubscriptionQueryService
   subscription_info = await self.subscription_repository.get_subscription_info(user_uuid)
   is_premium = subscription_info and subscription_info.is_active and subscription_info.plan_type == "premium"
   ```

3. **accept_interest_use_case.py**
   ```python
   # Before
   from app.modules.social.domain.repositories.i_friendship_repository import IFriendshipRepository
   from app.modules.social.domain.repositories.i_chat_room_repository import IChatRoomRepository
   
   # After
   from app.shared.domain.contracts.i_friendship_service import IFriendshipService
   from app.shared.domain.contracts.i_chat_room_service import IChatRoomService
   ```

### Phase 8: 測試與驗證 ✅

#### 測試更新

**Posts Module Tests** - 100% 通過
- 更新 69 個測試以配合新的服務介面
- 主要變更: mock `ISubscriptionQueryService` 返回 `SubscriptionInfo` DTO
- 結果: ✅ 69/69 tests passing

**Social Module Tests** - 85% 通過
- 更新部分測試配合新介面
- 修復測試匯入錯誤
- 結果: ✅ 297/349 tests passing

#### 測試結果摘要
```
Posts Module:   69 passed  (100%)
Social Module: 297 passed, 15 failed, 37 errors (85%)
Total:         366 passed
```

## 架構改進

### Before: 緊耦合架構
```
┌─────────────┐      ┌──────────────┐
│   Posts     │─────→│  Identity    │
│             │      │  (Repo/Model)│
└─────────────┘      └──────────────┘
       │                    ↑
       │                    │
       ↓                    │
┌─────────────┐             │
│   Social    │─────────────┘
│             │
└─────────────┘
```

### After: 鬆耦合架構
```
┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│   Posts     │─────→│    Shared    │←─────│  Identity    │
│             │      │  (Contracts) │      │  (Services)  │
└─────────────┘      └──────────────┘      └──────────────┘
       ↓                    ↑                       
┌─────────────┐             │                       
│   Social    │─────────────┘                       
│  (Services) │                                     
└─────────────┘                                     
```

## 技術債務

### 1. card_repository_impl.py 的 ProfileModel join

**問題描述:**
`find_nearby_cards` 方法直接 join `ProfileModel` 取得用戶位置與暱稱

```python
# Line 166-204
from app.modules.identity.infrastructure.database.models.profile_model import ProfileModel

query = (
    select(CardModel, ProfileModel)
    .join(ProfileModel, CardModel.owner_id == ProfileModel.user_id)
    ...
)
```

**影響:**
- 唯一剩餘的跨模組 DB 層直接依賴
- 違反了 bounded context 獨立性原則

**建議解決方案:**
1. **Option 1: Use Case 層組合**
   - 在 `SearchNearbyCardsUseCase` 中分別查詢 cards 和 profiles
   - 在應用層組合資料
   - 優點: 完全解耦，清晰的架構
   - 缺點: 可能增加 DB 查詢次數

2. **Option 2: Read Model/Projection**
   - 建立專用的 nearby search read model
   - 使用 event sourcing 更新 denormalized view
   - 優點: 性能最佳
   - 缺點: 需要額外的同步機制

3. **Option 3: CQRS Pattern**
   - 查詢端使用獨立的 read database
   - 包含所需的 denormalized 資料
   - 優點: 查詢性能優，架構清晰
   - 缺點: 增加系統複雜度

**優先級:** Low
**理由:** 不影響功能正確性，僅影響架構純度

### 2. 剩餘測試失敗

**問題:**
- 15 個測試: enum 名稱變更 (如 `idol_name` → `idol`)
- 37 個測試: 匯入錯誤或參數名稱變更

**優先級:** Medium
**預估工時:** 2-3 小時

## 成果總結

### 定量成果
- ✅ 新增 5 個共享介面契約
- ✅ 實作 5 個服務實作類別
- ✅ 重構 3 個模組的 DI 配置
- ✅ 更新 9 個 router 檔案
- ✅ 更新 4 個 use case 檔案
- ✅ 修復 69 個 Posts 測試
- ✅ 366 個測試通過

### 定性成果
1. **模組獨立性提升**
   - 各 BC 可獨立開發、測試、部署
   - 減少跨模組變更的影響範圍

2. **可測試性改善**
   - 使用介面依賴，易於 mock 和測試
   - 測試不需要啟動多個模組

3. **可維護性增強**
   - 清晰的模組邊界
   - 明確的依賴方向
   - 易於理解和修改

4. **擴展性提升**
   - 新增 BC 時遵循相同模式
   - 服務可以輕鬆替換實作

## 後續建議

### 短期 (1-2 週)
1. 修復剩餘 52 個測試案例
2. 執行完整的整合測試
3. 更新 API 文件

### 中期 (1 個月)
1. 重構 `card_repository` 的 ProfileModel join
2. 增加服務層的單元測試
3. 性能測試與優化

### 長期 (3 個月)
1. 考慮引入 CQRS 模式
2. 實作 event-driven architecture
3. 建立架構決策記錄 (ADR)

## 參考資料

- [Domain-Driven Design](https://www.domainlanguage.com/ddd/)
- [Bounded Context Pattern](https://martinfowler.com/bliki/BoundedContext.html)
- [Anti-Corruption Layer](https://docs.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer)
- [Dependency Inversion Principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle)
