# IoC Container 實作說明

## 概述

本專案已實作完整的 **IoC (Inversion of Control) 容器**，遵循 **依賴反轉原則 (Dependency Inversion Principle, DIP)**，確保上層不依賴下層的具體實作，而是依賴抽象介面。

## 問題背景

原始實作中存在以下問題：
- **違反 DIP**：Application Layer 和 Presentation Layer 直接依賴 Infrastructure Layer 的具體實作類別
- **緊耦合**：路由直接實例化 `SQLAlchemyUserRepository` 等具體類別
- **測試困難**：無法輕鬆替換依賴進行單元測試

## 解決方案

採用 **dependency-injector** 套件實作 IoC 容器，配合 FastAPI 的依賴注入系統。

### 架構改進

#### 1. 依賴層次（遵循 DIP）

```
Presentation Layer (Routes)
    ↓ 依賴
Application Layer (Use Cases)
    ↓ 依賴
Domain Layer (Interfaces)
    ↑ 實作
Infrastructure Layer (Implementations)
```

#### 2. 核心元件

##### Container (`app/container.py`)
集中管理所有依賴的註冊與生命週期：

```python
class Container(containers.DeclarativeContainer):
    # 配置
    config = providers.Singleton(Settings)
    
    # Infrastructure Services (Singleton - 整個應用共享)
    google_oauth_service = providers.Singleton(GoogleOAuthService)
    jwt_service = providers.Singleton(JWTService)
    
    # Repositories (Factory - 每次注入創建新實例)
    user_repository = providers.Factory(
        SQLAlchemyUserRepository,
        session=db_session
    )
    profile_repository = providers.Factory(
        SQLAlchemyProfileRepository,
        session=db_session
    )
```

##### Dependency Providers (`app/presentation/dependencies/ioc_dependencies.py`)
提供 FastAPI 路由使用的依賴注入函數：

```python
def get_user_repository(
    session: AsyncSession = Depends(get_session)
) -> IUserRepository:
    """返回介面而非具體實作"""
    return SQLAlchemyUserRepository(session)
```

#### 3. 使用範例

##### Before (違反 DIP)
```python
@router.post("/google")
async def login_with_google(
    session: AsyncSession = Depends(get_db_session)
):
    # ❌ 直接依賴具體實作
    user_repo = SQLAlchemyUserRepository(session)
    profile_repo = SQLAlchemyProfileRepository(session)
    google_oauth = GoogleOAuthService()
    jwt_service = JWTService()
```

##### After (遵循 DIP)
```python
@router.post("/google")
async def login_with_google(
    user_repo: IUserRepository = Depends(get_user_repository),
    profile_repo: IProfileRepository = Depends(get_profile_repository),
    google_oauth: GoogleOAuthService = Depends(get_google_oauth_service),
    jwt_service: JWTService = Depends(get_jwt_service)
):
    # ✅ 依賴注入，接收介面而非具體實作
```

## 實作細節

### 1. Use Cases 更新

所有 Use Case 現在依賴介面而非具體實作：

```python
class LoginWithGoogleUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,  # ✅ 介面
        profile_repo: IProfileRepository,  # ✅ 介面
        google_oauth_service: GoogleOAuthService,
        jwt_service: JWTService,
        session: AsyncSession
    ):
        ...
```

### 2. 路由更新

所有路由使用依賴注入獲取依賴：

```python
@router.get("/me")
async def get_my_profile(
    user_id: UUID = Depends(get_current_user_id),
    profile_repo: IProfileRepository = Depends(get_profile_repository)  # ✅ 注入
):
    use_case = GetProfileUseCase(profile_repo=profile_repo)
    ...
```

### 3. Container 初始化

在 `main.py` 的 lifespan 事件中初始化並綁定容器：

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化資料庫
    await init_db()
    
    # 綁定容器到模組（啟用自動注入）
    container.wire(modules=[
        "app.presentation.routers.auth_router",
        "app.presentation.routers.profile_router",
        "app.presentation.dependencies.auth_dependencies",
        "app.presentation.dependencies.ioc_dependencies"
    ])
    
    yield
    
    # 清理
    container.unwire()
```

## 優勢

### 1. 遵循 SOLID 原則
- ✅ **依賴反轉原則 (DIP)**：高層不依賴低層實作
- ✅ **單一職責原則 (SRP)**：容器負責依賴管理
- ✅ **開放封閉原則 (OCP)**：易於擴展新實作

### 2. 提升可測試性
```python
# 測試時可輕鬆替換依賴
mock_repo = MockUserRepository()
use_case = LoginWithGoogleUseCase(
    user_repo=mock_repo,  # 注入 Mock
    ...
)
```

### 3. 靈活性
- 切換資料庫實作（SQL → NoSQL）只需修改容器配置
- 不影響 Use Cases 和 Routes

### 4. 集中管理
- 所有依賴生命週期在 Container 統一管理
- Singleton vs Factory 模式清晰定義

## 依賴生命週期

| 類型 | 生命週期 | 範例 |
|------|---------|------|
| **Singleton** | 整個應用共享單一實例 | JWTService, GoogleOAuthService |
| **Factory** | 每次注入創建新實例 | Repositories (需要 session) |
| **Resource** | 管理生命週期資源 | Database Session |

## 套件資訊

- **dependency-injector** (v4.41.0+)
  - 官方文檔：https://python-dependency-injector.ets-labs.org/
  - FastAPI 整合範例：https://python-dependency-injector.ets-labs.org/examples/fastapi.html

## 後續改進建議

1. **配置外部化**：將配置移至環境變數或設定檔
2. **更多 Provider 類型**：根據需求使用 Callable, List, Dict providers
3. **測試支援**：使用 `container.override()` 簡化測試
4. **非同步工廠**：支援非同步初始化的依賴

## 總結

本實作完整解決了原有的依賴耦合問題，透過 IoC 容器實現了：
- ✅ 依賴反轉 (上層依賴抽象)
- ✅ 關注點分離 (各層職責清晰)
- ✅ 高可測試性 (依賴可替換)
- ✅ 高可維護性 (集中管理)

這是 DDD 架構的最佳實踐，確保系統的長期可維護性與擴展性。
