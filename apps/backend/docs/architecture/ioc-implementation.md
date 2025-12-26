# IoC Container 規範（python-injector 單一路線）

本文件僅定義一套實作方式，與 job-service 相同：使用 `python-injector`，不使用 `dependency-injector` 的 Provide/wire。保持路由與 use case 呼叫方式不變。

## 核心原則

- Router 不直接 new repo/service/use case，只透過依賴取得 use case。
- Use case 只依賴 Domain 介面；Infrastructure 提供實作。
- Request-scope（尤其 DB `AsyncSession`）由 FastAPI/middleware 控制生命週期，必要時在 dependency function 以 child injector 綁定 session。

## 組件角色

- `app/api/common/injector.py`（或後端對應路徑）：建立全域 `Injector`，組合所有 `Module`。
- `app/modules/<module>/module.py`：該模組的 `injector.Module`，用 `@provider` 回傳 use case / service；需要 repo 時可在 provider 內直接 new（吃 session）。
- `app/modules/<module>/presentation/dependencies/*.py`：
  - 不用 `Provide/@inject`。
  - 從全域 injector 取 use case：`injector.get(UseCase)`；若需 session，先用 child injector 綁定 `AsyncSession`。
- `app/main.py`：啟動時把 injector 掛到 `app.state`，註冊 routers，無需 `container.wire/unwire`。
- `app/container.py`（舊架構）：請移除或停用，不再使用 dependency-injector ApplicationContainer。改用全域 `Injector`（app/injector.py）聚合各 `Module`。

### app/injector.py 組裝示意

```python
# app/injector.py（示意，可依實際路徑命名）
from injector import Injector
from app.modules.identity.module import IdentityModule
from app.modules.posts.module import PostsModule
from app.modules.social.module import SocialModule
from app.shared.module import SharedModule  # 若有共用依賴可集中

injector = Injector(
	[
		SharedModule(),
		IdentityModule(),
		PostsModule(),
		SocialModule(),
	]
)
```

> 若沒有 shared module，可直接把各 BC module 放入列表；重點是用 Injector 聚合，不需舊的 ApplicationContainer。

## Main（組合根）示意

```python
from fastapi import FastAPI
from app.api.common.injector import injector
from app.api.routes import api_v1

def create_application() -> FastAPI:
	app = FastAPI()
	app.state.injector = injector
	app.mount("/api/v1", api_v1)
	return app
```

## Module 示意（provider 內 new repo，不獨立 repo provider）

```python
from injector import Module, provider
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.identity.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from app.modules.identity.infrastructure.repositories.refresh_token_repository_impl import RefreshTokenRepositoryImpl
from app.modules.identity.application.use_cases.auth.admin_login import AdminLoginUseCase

class IdentityModule(Module):
	@provider
	def provide_admin_login_use_case(self, session: AsyncSession) -> AdminLoginUseCase:
		user_repo = UserRepositoryImpl(session)
		refresh_repo = RefreshTokenRepositoryImpl(session)
		return AdminLoginUseCase(user_repository=user_repo, refresh_token_repository=refresh_repo)
```

## Dependency function 示意（保持 use case 呼叫方式）

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.common.injector import injector
from app.shared.infrastructure.database.connection import get_db_session
from app.modules.identity.application.use_cases.auth.admin_login import AdminLoginUseCase

async def get_admin_login_use_case(session: AsyncSession = Depends(get_db_session)) -> AdminLoginUseCase:
	# 將 request-scope session 綁到 child injector，再取 use case
	with injector.create_child_injector({AsyncSession: session}) as child:
		return child.get(AdminLoginUseCase)
```

## Request-scope 建議

- 若使用 `Depends(get_db_session)`，在 dependency function 內以 child injector 綁定 session，再取 use case。
- 若用 middleware 管理 session，也可在 middleware 建 child injector 並以 contextvar 傳遞，router 端直接 `injector.get(...)`。

## 遷移步驟（實作指引）

1) 建立全域 `Injector` 並組合各 Module（如 job）。
2) 為 identity 等模組撰寫 `module.py`，provider 內直接 new repo/use case（吃 session）。
3) 調整 dependencies 檔：改用 `injector.get(...)`；移除 Provide/@inject/wire。
4) main 掛載 injector，確保 session/middleware 與依賴取用一致。
