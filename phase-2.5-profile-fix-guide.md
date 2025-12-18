# Phase 2.5 Admin System Fix - 實施指南

## 問題總結

### 1. 管理員帳號 Profile API 404 錯誤
**原因**: `init_admin.py` 腳本在建立管理員帳號時，只建立了 `UserModel`，沒有建立對應的 `ProfileModel`。當管理員登入後呼叫 `/api/v1/profile/me` 端點時，因為找不到對應的 Profile 記錄而返回 404 錯誤。

**解決方案**: 更新 `init_admin.py`，在建立管理員帳號時同時建立對應的 `ProfileModel`，設定適當的預設值（nickname、bio、privacy_flags）。

### 2. ProfileModel 缺少獨立 ID 欄位
**原因**: `profiles` 表使用 `user_id` 作為主鍵，違反了專案規範「所有 ORM model 建立表都需要建立 id 欄位」。

**解決方案**: 
- 為 `ProfileModel` 添加獨立的 `id` 欄位作為主鍵（UUID 型別）
- 將 `user_id` 改為 UNIQUE 外鍵
- 建立 Alembic migration 來更新資料庫結構

## 檔案變更清單

### 1. 後端核心檔案

#### `apps/backend/scripts/init_admin.py`
- **變更**: 新增 ProfileModel 建立邏輯
- **影響**: 管理員初始化腳本現在會同時建立 User 和 Profile
```python
# 新增的程式碼片段
admin_profile = ProfileModel(
    user_id=admin_user.id,
    nickname=f"Admin ({email.split('@')[0]})",
    bio="System Administrator",
    privacy_flags={"nearby_visible": False, "show_online": False, "allow_stranger_chat": False},
)
```

#### `apps/backend/app/modules/identity/infrastructure/database/models/profile_model.py`
- **變更**: 添加 `id` 欄位作為主鍵，`user_id` 改為 unique foreign key
```python
id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), 
                 unique=True, nullable=False, index=True)
```

#### `apps/backend/app/modules/identity/domain/entities/profile.py`
- **變更**: Profile 實體新增 `id` 屬性
```python
def __init__(self, user_id: UUID, id: Optional[UUID] = None, ...):
    self._id = id or uuid.uuid4()
    self._user_id = user_id
```

#### `apps/backend/app/modules/identity/infrastructure/repositories/profile_repository_impl.py`
- **變更**: Repository 方法更新以處理 `id` 欄位
- **影響**: `save()` 和 `_to_entity()` 方法現在包含 `id` 欄位

#### `apps/backend/app/modules/identity/presentation/schemas/profile_schemas.py`
- **變更**: ProfileResponse schema 新增 `id` 欄位
```python
id: UUID = Field(..., description="Profile ID")
user_id: UUID = Field(..., description="User ID")
```

#### `apps/backend/app/modules/identity/presentation/routers/profile_router.py`
- **變更**: API 回應包含 `id` 欄位
- **影響**: GET /profile/me 和 PUT /profile/me 端點現在會返回 profile id

### 2. 資料庫遷移

#### `apps/backend/alembic/versions/004_add_profile_id.py` (新增)
- **用途**: 為 profiles 表添加 id 欄位的資料庫遷移
- **操作步驟**:
  1. 移除 `user_id` 的主鍵約束
  2. 新增 `id` 欄位（UUID, 自動產生預設值）
  3. 設定 `id` 為新的主鍵
  4. 設定 `user_id` 為 UNIQUE 約束
  5. 建立 `user_id` 索引

### 3. 文件更新

#### `.specify/memory/constitution.md`
- **新增章節**: 資料庫設計原則
- **內容**: 明確規定所有表必須有獨立的 `id` 主鍵欄位

#### `specs/001-kcardswap-complete-spec/data-model.md`
- **更新**: profiles 表結構說明
- **新增**: migration 004 的記錄

#### `apps/backend/tests/unit/domain/test_profile_entity.py`
- **修正**: import 路徑（從 `app.domain` 改為 `app.modules.identity.domain`）
- **新增**: 測試 `id` 欄位的存在性

## 部署步驟

### 本地開發環境

1. **拉取最新程式碼**
```bash
git pull origin <branch-name>
cd apps/backend
```

2. **執行資料庫遷移**
```bash
# 使用 Poetry
poetry run alembic upgrade head

# 或使用 Docker
docker compose exec backend alembic upgrade head
```

3. **重新初始化管理員帳號（如果需要）**
```bash
# 先刪除現有的管理員帳號（在資料庫中）
# 然後重新執行
poetry run python scripts/init_admin.py
```

4. **驗證變更**
```bash
# 測試管理員登入
curl -X POST http://localhost:8000/api/v1/auth/admin-login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@kcardswap.local","password":"your-password"}'

# 測試 Profile API（使用返回的 token）
curl -X GET http://localhost:8000/api/v1/profile/me \
  -H "Authorization: Bearer <access_token>"
```

### 正式環境

1. **備份資料庫**
```bash
pg_dump -h <host> -U <user> -d kcardswap > backup_$(date +%Y%m%d_%H%M%S).sql
```

2. **部署程式碼**
```bash
# 透過 CI/CD 或手動部署
git push origin main
```

3. **執行資料庫遷移**
```bash
# 在生產環境容器中執行
kubectl exec -it <backend-pod> -- alembic upgrade head

# 或透過 Cloud Run
gcloud run services update <service-name> --command alembic,upgrade,head
```

4. **驗證部署**
- 檢查現有管理員帳號是否能正常存取 Profile API
- 確認 API 回應包含 `id` 欄位
- 檢查應用程式日誌確認無錯誤

## 向後相容性

### API 相容性
✅ **完全相容**: 新增的 `id` 欄位不會破壞現有 API 消費者，因為：
- GET 端點會多返回一個 `id` 欄位（客戶端可以忽略）
- PUT 端點不需要傳遞 `id` 欄位
- `user_id` 仍然存在且功能不變

### 資料庫相容性
✅ **向前相容**: migration 會自動為現有記錄生成 UUID
❌ **不可回滾**: 一旦執行 upgrade，建議不要執行 downgrade（會遺失 id 資料）

## 注意事項

1. **現有管理員帳號**
   - 如果已經有管理員帳號但沒有 Profile，需要手動在資料庫中建立或重新執行 `init_admin.py`

2. **Migration 順序**
   - 必須按順序執行：001 → 002 → 003 → 004
   - 不要跳過任何 migration

3. **測試環境**
   - 建議先在測試環境執行完整流程
   - 確認無誤後再部署到正式環境

4. **Rollback 策略**
   - 如果遇到問題，從備份還原資料庫
   - 避免使用 `alembic downgrade`，除非確定不會遺失資料

## 驗證清單

- [ ] Migration 004 成功執行
- [ ] profiles 表有 `id` 欄位（UUID, PK）
- [ ] profiles 表的 `user_id` 有 UNIQUE 約束
- [ ] 管理員帳號有對應的 Profile 記錄
- [ ] GET /api/v1/profile/me 返回包含 `id` 的回應
- [ ] 新建立的管理員帳號會自動建立 Profile
- [ ] 所有現有測試通過
- [ ] API 文件（Swagger）顯示 `id` 欄位

## 相關文件

- [Database Migrations Guide](apps/backend/docs/database-migrations.md)
- [Identity Module API](apps/backend/docs/api/identity-module.md)
- [Data Model Specification](specs/001-kcardswap-complete-spec/data-model.md)
- [Project Constitution](.specify/memory/constitution.md)
