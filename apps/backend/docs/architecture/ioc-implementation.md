# IoC Container 規範（精簡版）

本文件只定義**一套**實作方式與**一個**端到端範例。

## 目標

- 路由（Presentation）不直接 `new` repository / service / use case。
- Use Case（Application）只依賴 Domain 介面（抽象），Infrastructure 提供實作。
- request-scope 依賴（特別是 DB session）由 FastAPI `Depends()` 管理；IoC container 不管理 session 生命週期。

## 本文件規範：一律使用 Provide + @inject

本專案的 IoC/DI 規範固定採用 `dependency-injector` 的 **wiring** 機制：

- 依賴取得：`Provide[...]`
- 注入啟用：`@inject`
- 啟動時 wiring：在 `app/main.py` 的 lifespan 呼叫 `container.wire(...)`

因此本文件的所有範例都以 **Provide + @inject** 為前提，不提供其他替代寫法。

## 專案約定（放哪裡、誰負責什麼）

## 命名規範（介面/實作）

為了降低 wiring / import / typing 錯誤率，本專案後端採用以下一致命名：

- **Repository 介面（Domain）**：一律使用 `I` 前綴
    - 例：`ICardRepository`, `ISubscriptionRepository`, `ITradeRepository`
- **Repository 實作（Infrastructure）**：一律使用 `Impl` 後綴
    - 例：`SQLAlchemyCardRepositoryImpl`, `SubscriptionRepositoryImpl`
- **檔名**：
    - Repository 介面放在 `app/modules/<module>/domain/repositories/i_<name>_repository.py`
    - Repository 實作放在 `app/modules/<module>/infrastructure/repositories/<name>_repository_impl.py`

> 備註：若同一個 repository 存在多種儲存後端（SQLAlchemy / Redis / External API），
> 建議在類別名稱保留前綴（例如 `SQLAlchemy...`）以避免混淆，但仍需以 `Impl` 結尾。

- `app/container.py`
  - 匯總 shared providers 與各模組 container。
  - 只宣告 providers，不在這裡做任何「啟動副作用」。
- `app/modules/<module>/container.py`（必須）
    - 模組內的**組裝規則**（高內聚）：repo factory / use case factory 等都定義在這裡。
    - 重點：這裡是在「宣告 providers（工廠/單例）」，不是在處理 request-scope（例如 session）。
- `app/modules/<module>/presentation/dependencies/*.py`
    - **唯一**負責把 request-scope（例如 `AsyncSession`）接起來：從 container 取出 factory，帶入 session，產生 use case 實例。
    - 重點：這裡不是「組裝容器」，容器的組裝已經在 `app/modules/<module>/container.py` 完成；這裡是在「解析/產生實例」。
- `app/modules/<module>/presentation/routers/*.py`
  - 路由只 `Depends(get_<use_case>)`（低耦合）。

## Main（`app/main.py`）的角色與要設定什麼

`app/main.py` 是 **composition root**：負責「啟動時把各部件接起來」，但不承擔 request-scope 的組裝工作。

你需要做的設定（以 IoC/DI 角度）：

- 建立 FastAPI app（`create_application()`）
- 把 IoC container 掛到 app（例如 `app.container = container` 或 `app.state.container = container`）
- 註冊各模組 router（`app.include_router(...)`）
- 在 lifespan：
  - startup：`container.wire(...)`
  - shutdown：`container.unwire()`

不建議放在 main 的事情：

- DB schema 初始化（本專案交給 Alembic migrations；不要在 lifespan `init_db()`）
- 在 router 內組 repo/service/use case（組裝在 `presentation/dependencies`）

最短示意：

```python
# app/main.py（示意）
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.container import container


@asynccontextmanager
async def lifespan(app: FastAPI):
    container.wire(packages=[
        "app.modules",
        "app.shared",
    ])
    yield
    container.unwire()


def create_application() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.container = container
    # app.include_router(...)
    return app
```

## 端到端範例（唯一範例）：Social / UploadCard

### 1) 模組 container：宣告 providers

```python
# app/modules/social/container.py（示意）
from dependency_injector import containers, providers

from app.modules.social.application.use_cases.cards.upload_card import UploadCardUseCase
from app.modules.social.domain.services.card_validation_service import CardValidationService
from app.modules.social.infrastructure.repositories.card_repository_impl import (
    SQLAlchemyCardRepositoryImpl,
)


class SocialModuleContainer(containers.DeclarativeContainer):
    shared = providers.DependenciesContainer()

    # repo 需要 request-scope session：用 Factory，session 由呼叫端傳入
    card_repository = providers.Factory(SQLAlchemyCardRepositoryImpl)

    validation_service = providers.Factory(CardValidationService)

    # use case 的固定依賴（不含 session）在這裡宣告
    upload_card_use_case_factory = providers.Factory(
        UploadCardUseCase,
        validation_service=validation_service,
        gcs_service=shared.gcs_storage_provider,
    )
```

### 2) App container：匯總 shared + module

```python
# app/container.py（示意）
from dependency_injector import containers, providers

from app.config import settings
from app.modules.social.container import SocialModuleContainer
from app.shared.infrastructure.database.connection import db_connection
from app.shared.infrastructure.external.gcs_storage_service import gcs_storage_service
from app.shared.infrastructure.security.jwt_service import jwt_service
from app.shared.infrastructure.security.password_hasher import password_hasher


class SharedContainer(containers.DeclarativeContainer):
    config = providers.Singleton(lambda: settings)
    db_connection_provider = providers.Singleton(lambda: db_connection)
    jwt_service_provider = providers.Singleton(lambda: jwt_service)
    password_hasher_provider = providers.Singleton(lambda: password_hasher)
    gcs_storage_provider = providers.Singleton(lambda: gcs_storage_service)


class ApplicationContainer(containers.DeclarativeContainer):
    shared = providers.Container(SharedContainer)
    social = providers.Container(SocialModuleContainer, shared=shared)


container = ApplicationContainer()
```

### 3) 模組 dependencies：把 session 串進來，回傳 use case

重點：
- `AsyncSession` 由 `Depends(get_db_session)` 提供
- 在這裡把「request-scope 的 session」接到「container 內宣告的 factories」
- router 只拿到 use case

```python
# app/modules/social/presentation/dependencies/use_cases.py（示意）
from collections.abc import Callable

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.container import container
from app.modules.social.application.use_cases.cards.upload_card import UploadCardUseCase
from app.modules.social.domain.repositories.i_card_repository import ICardRepository
from app.shared.infrastructure.database.connection import get_db_session


@inject
def get_upload_card_use_case(
    session: AsyncSession = Depends(get_db_session),
    repo_factory: Callable[[AsyncSession], ICardRepository] = Provide[
        container.social.card_repository
    ],
    use_case_factory: Callable[..., UploadCardUseCase] = Provide[
        container.social.upload_card_use_case_factory
    ],
) -> UploadCardUseCase:
    # 這裡不是組裝容器：容器已在 module container 宣告好 providers
    # 這裡是「解析 providers 並產生本次 request 的 use case 實例」
    card_repo = repo_factory(session)
    return use_case_factory(card_repo=card_repo)
```

### 4) Router：只 Depends(use case)

```python
# app/modules/social/presentation/routers/cards_router.py（示意）
from fastapi import Depends

from app.modules.social.application.use_cases.cards.upload_card import UploadCardUseCase
from app.modules.social.presentation.dependencies.use_cases import get_upload_card_use_case


@router.post("/upload-url")
async def get_upload_url(
    use_case: UploadCardUseCase = Depends(get_upload_card_use_case),
):
    return await use_case.execute(...)
```

## 啟動流程（本專案現況）

- DB schema 由 Alembic migrations 管理，不在 FastAPI lifespan 內 `init_db()`
  - Docker：`apps/backend/start.sh` 會執行 `alembic upgrade head`
  - 本機：啟動前先跑 `poetry run alembic upgrade head`

## 補充（只留一段）

- 測試想替換依賴時，可用 `container.override(...)` 或替換對應 provider。
