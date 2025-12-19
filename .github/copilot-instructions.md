# KCardSwap Development Guidelines

請依據此專案的speckit指令所產生的規範與需求，協助完成相關開發任務。

<!-- MANUAL ADDITIONS START -->
請使用中文回答問題

AI 執行專案相關任務時，請先讀取 `apps` 目錄下各服務的 `README.md`，以取得該服務的運行與設定說明。

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

<!-- MANUAL ADDITIONS END -->
