# Identity 模組單元測試

這個目錄包含 Identity 模組的完整單元測試套件。

## 測試概覽

總共 **133 個測試案例**，涵蓋 Identity 模組的核心功能。

### 測試結構

```
tests/unit/identity/
├── domain/
│   └── entities/
│       ├── test_user.py           # User Entity 測試 (22 測試)
│       ├── test_profile.py        # Profile Entity 測試 (35 測試)
│       ├── test_refresh_token.py  # RefreshToken Entity 測試 (24 測試)
│       └── test_subscription.py   # Subscription Entity 測試 (30 測試)
└── infrastructure/
    └── security/
        └── test_password_service.py  # PasswordService 測試 (22 測試)
```

## 測試涵蓋範圍

### Domain Entities (111 測試)

#### 1. User Entity (22 測試)
- **建立測試**: Google OAuth、密碼認證、自訂 ID、時間戳記、Email 正規化
- **驗證測試**: Email 格式、空 Email、缺少認證方法、無效角色、有效角色
- **業務邏輯**: 管理員檢查、Email 更新、Email 正規化和驗證
- **相等性**: ID 比較、非 User 物件比較、雜湊、字串表示
- **屬性**: 唯讀屬性驗證

#### 2. Profile Entity (35 測試)
- **建立測試**: 最小欄位、完整欄位、預設隱私設定
- **驗證測試**: 暱稱長度、個人簡介長度、緯度/經度範圍
- **更新測試**: 完整更新、部分更新、驗證、偏好設定合併
- **隱私設定**: 更新設定、附近可見性、線上狀態、陌生人聊天
- **位置管理**: 位置更新、驗證、檢查位置、隱身模式
- **相等性和屬性**: User ID 比較、屬性複製、唯讀驗證

#### 3. RefreshToken Entity (24 測試)
- **建立測試**: 最小欄位、完整欄位、預設撤銷狀態
- **驗證測試**: 空 token、None 檢查、過期時間驗證
- **業務邏輯**: 過期檢查、有效性檢查、撤銷功能
- **相等性**: ID 比較、雜湊、字串表示
- **屬性**: 完整屬性存取、唯讀驗證

#### 4. Subscription Entity (30 測試)
- **建立測試**: 免費訂閱、付費訂閱、時間戳記、待處理、已過期
- **狀態檢查**: 啟用檢查、付費檢查、過期檢查
- **過期邏輯**: 應該過期檢查、不同狀態的行為
- **狀態轉換**: 標記過期、啟用付費、停用
- **生命週期**: 完整付費生命週期、續訂、重新啟用

### Infrastructure Services (22 測試)

#### PasswordService (22 測試)
- **初始化**: 服務建立
- **雜湊功能**: 一般密碼、空字串、特殊字元、Unicode、長密碼
- **驗證功能**: 成功/失敗、空值、特殊字元、Unicode、大小寫敏感
- **整合測試**: 雜湊與驗證流程、多次呼叫
- **錯誤處理**: 例外傳播
- **使用模式**: 管理員認證、使用者註冊、密碼變更、多次失敗嘗試

## 執行測試

### 執行所有 Identity 單元測試
```bash
cd apps/backend
python3 -m pytest tests/unit/identity/ -v
```

### 執行特定測試檔案
```bash
# User Entity 測試
python3 -m pytest tests/unit/identity/domain/entities/test_user.py -v

# Profile Entity 測試
python3 -m pytest tests/unit/identity/domain/entities/test_profile.py -v

# RefreshToken Entity 測試
python3 -m pytest tests/unit/identity/domain/entities/test_refresh_token.py -v

# Subscription Entity 測試
python3 -m pytest tests/unit/identity/domain/entities/test_subscription.py -v

# PasswordService 測試
python3 -m pytest tests/unit/identity/infrastructure/security/test_password_service.py -v
```

### 執行特定測試類別
```bash
python3 -m pytest tests/unit/identity/domain/entities/test_user.py::TestUserValidation -v
```

### 執行特定測試案例
```bash
python3 -m pytest tests/unit/identity/domain/entities/test_user.py::TestUserValidation::test_invalid_email_format -v
```

## 測試設計原則

### 1. 模組優先方法
測試從最核心的業務邏輯（Domain Entities）開始，確保領域模型的正確性。

### 2. 全面涵蓋
- 正常流程測試
- 邊界條件測試
- 錯誤處理測試
- 業務規則驗證

### 3. 獨立性
每個測試都是獨立的，不依賴其他測試的執行順序或狀態。

### 4. 清晰命名
測試名稱清楚描述測試內容，例如：
- `test_create_user_with_google_id` - 測試使用 Google ID 建立使用者
- `test_invalid_email_format` - 測試無效的 Email 格式
- `test_is_premium_for_active_premium` - 測試啟用付費訂閱的付費狀態

### 5. 測試組織
使用測試類別組織相關測試，例如：
- `TestUserCreation` - 使用者建立相關測試
- `TestUserValidation` - 使用者驗證相關測試
- `TestUserBusinessLogic` - 使用者業務邏輯測試

## 測試結果

```
====================== 133 passed, 340 warnings in 0.16s =======================
```

所有測試均通過 ✅

## 依賴項

測試使用以下套件：
- `pytest` - 測試框架
- `pytest-asyncio` - 異步測試支援

模擬依賴：
- `unittest.mock` - Python 內建模擬功能

## 維護指南

### 新增測試
1. 在適當的目錄下建立或更新測試檔案
2. 使用描述性的測試類別和函數名稱
3. 遵循現有的測試結構和命名慣例
4. 確保測試獨立且可重複執行

### 測試失敗處理
1. 檢查失敗訊息和堆疊追蹤
2. 確認是測試問題還是程式碼問題
3. 更新測試或修復程式碼
4. 重新執行測試確認修復

### 程式碼覆蓋率
可以使用 `pytest-cov` 檢查覆蓋率：
```bash
python3 -m pytest tests/unit/identity/ --cov=app.modules.identity --cov-report=html
```

## 未來改進

- [ ] 新增 Use Cases 的單元測試
- [ ] 新增 Repository 介面的單元測試
- [ ] 新增外部服務的單元測試
- [ ] 提高程式碼覆蓋率到 90% 以上
- [ ] 新增效能測試
- [ ] 新增安全性測試

## 貢獻

歡迎提交新的測試案例或改進現有測試！請確保：
- 測試清晰且有意義
- 遵循專案的測試風格
- 所有測試都能通過
- 保持測試的獨立性
