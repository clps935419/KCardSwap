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

- `app/container.py`
  - 匯總 shared providers 與各模組 container。
  - 只宣告 providers，不在這裡做任何「啟動副作用」。
- `app/modules/<module>/container.py`（建議）
  - 模組內的組裝規則（高內聚）：repo factory / use case factory 等。
- `app/modules/<module>/presentation/dependencies/*.py`
  - **唯一**負責把 request-scope（例如 `AsyncSession`）接起來，組出 use case。
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
from app.modules.social.infrastructure.repositories.card_repository_impl import CardRepositoryImpl


class SocialModuleContainer(containers.DeclarativeContainer):
    shared = providers.DependenciesContainer()

    # repo 需要 request-scope session：用 Factory，session 由呼叫端傳入
    card_repository = providers.Factory(CardRepositoryImpl)

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
- 在這裡完成 repo/use case 組裝
- router 只拿到 use case

```python
# app/modules/social/presentation/dependencies/use_cases.py（示意）
from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.social.application.use_cases.cards.upload_card import UploadCardUseCase
from app.modules.social.domain.repositories.card_repository import CardRepository
from app.shared.infrastructure.database.connection import get_db_session


@inject
def get_upload_card_use_case(
    session: AsyncSession = Depends(get_db_session),
  repo_factory=Provide["container.social.card_repository"],
  use_case_factory=Provide["container.social.upload_card_use_case_factory"],
) -> UploadCardUseCase:
  card_repo: CardRepository = repo_factory(session)
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
