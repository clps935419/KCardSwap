# KCardSwap Development Guidelines

請依據此專案的speckit指令所產生的規範與需求，協助完成相關開發任務。

<!-- MANUAL ADDITIONS START -->
請使用中文回答問題

AI 執行專案相關任務時，請先讀取 `apps` 目錄下各服務的 `README.md`，以取得該服務的運行與設定說明。

## Speckit 報告位置

Speckit 在 implement 階段產生的報告，請直接寫入 `reports/` 目錄。

## Mobile 開發規範

### 必須遵守的規則

1. **UI 框架**: 必須使用 Gluestack UI 元件
   - 從 `@/src/shared/ui/components` 導入 UI 元件
   - 禁止使用原生 React Native 的 `View`, `Text`, `TouchableOpacity`, `ActivityIndicator`
   - 使用 Tailwind CSS `className` 而非 `StyleSheet`
   - 可用元件: `Box`, `Text`, `Pressable`, `Spinner`, `Button`, `ButtonText`, `Input`, `Heading`, `Card` 等

2. **路徑別名**: 必須使用 `@/` 路徑別名，禁止使用相對路徑
   - ✅ 正確: `import { apiClient } from '@/src/shared/api/client'`
   - ✅ 正確: `import { useMyCards } from '@/src/features/cards/hooks/useCards'`
   - ✅ 正確: `import type { Card } from '@/src/features/cards/types'`
   - ❌ 錯誤: `import { apiClient } from '../../../shared/api/client'`
   - ❌ 錯誤: `import { useMyCards } from '../hooks/useCards'`
   - ❌ 錯誤: `import type { Card } from '../types'`

3. **實作流程**:
   - Step 1: 閱讀 `apps/mobile/README.md` 確認 UI 框架和技術棧
   - Step 2: 閱讀 `apps/mobile/TECH_STACK.md` 了解開發規範
   - Step 3: 參考現有 feature (如 `profile`) 的程式碼風格
   - Step 4: 開始實作，確保使用 Gluestack UI 和路徑別名

### 範例參考

參考 `src/features/profile/` 目錄下的檔案，它們正確使用了：
- Gluestack UI 元件
- `@/` 路徑別名
- Tailwind CSS className

## Web 開發規範

### 必須遵守的規則

1. **流程**:
    - Step 1: 閱讀 `apps/web/README.md` 確認運行方式與技術棧
    - Step 2: 閱讀 `apps/web/TECH_STACK.md`（若存在）了解開發規範
    - Step 3: 參考現有 `apps/web` 內的 page/component 程式碼風格

2. **React/Next.js 效能規範**:
    - 需優先遵循已安裝的 `vercel-react-best-practices` skill 內容。
    - 若需查詢完整規範，請參考：
       https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices
    - 重要方向包含（依影響度）：
       - Eliminating Waterfalls（`async-*`）
       - Bundle Size Optimization（`bundle-*`）
       - Server-Side Performance（`server-*`）
       - Client-Side Data Fetching（`client-*`）
       - Re-render Optimization（`rerender-*`）
       - Rendering Performance（`rendering-*`）
       - JavaScript Performance（`js-*`）
       - Advanced Patterns（`advanced-*`）

## 後端開發規範

### OpenAPI 規格生成

**重要**: `generate_openapi.py` 腳本可獨立執行，不需要完整的 Poetry 環境。

```bash
# 方法 1: 直接使用 Python 執行（推薦給 AI agent）
cd apps/backend
pip3 install fastapi pydantic sqlalchemy injector asyncpg python-jose passlib bcrypt email-validator google-auth google-cloud-storage firebase-admin httpx python-multipart
python3 scripts/generate_openapi.py

# 方法 2: 使用 Makefile（從專案根目錄）
make generate-openapi

# 方法 3: 使用 Poetry（完整環境）
cd apps/backend
poetry run python scripts/generate_openapi.py
```

生成後的 `openapi/openapi.json` 用於：
- 前端 SDK 生成 (`cd apps/mobile && npm run sdk:generate`)
- API 文件同步
- 型別安全驗證

**SDK 生成流程**:
1. 後端修改 API → 執行 `python3 scripts/generate_openapi.py`
2. 產生 `openapi/openapi.json`
3. 前端執行 `npm run sdk:generate` 產生型別安全的 SDK
4. 前端使用生成的 SDK，不要手動撰寫 API 呼叫

<!-- MANUAL ADDITIONS END -->
