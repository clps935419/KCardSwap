# NextAuth.js 整合總結

## 🎯 完成的工作

### 1. NextAuth 核心設定
- ✅ 建立 NextAuth API route (`/api/auth/[...nextauth]/route.ts`)
- ✅ 設定 Google OAuth Provider
- ✅ 實作 callbacks 與後端 API 整合
- ✅ 建立型別定義與工具函式

### 2. 應用程式整合
- ✅ 在 `providers.tsx` 中加入 `SessionProvider`
- ✅ 建立 middleware 保護需要登入的路由
- ✅ 更新登入頁面使用 NextAuth 的 `signIn()`
- ✅ 更新 app layout 顯示使用者資訊與登出功能

### 3. 文件與測試
- ✅ 建立完整的 NextAuth 整合指南 (`NEXTAUTH_GUIDE.md`)
- ✅ 更新 README.md 說明 NextAuth 使用方式
- ✅ 建立測試頁面 (`/auth-test`) 用於驗證功能

### 4. 代碼品質
- ✅ 修正所有 Biome linting 錯誤
- ✅ 更新 biome.json 到最新版本
- ✅ TypeScript 型別檢查通過

## 📁 新增/修改的檔案

### 新增檔案
```
apps/web/
├── src/
│   ├── app/
│   │   ├── api/auth/[...nextauth]/route.ts      # NextAuth API route
│   │   └── (app)/auth-test/page.tsx             # 測試頁面
│   ├── lib/
│   │   └── auth/
│   │       ├── config.ts                        # NextAuth 設定
│   │       ├── utils.ts                         # 工具函式
│   │       ├── types.ts                         # 型別定義
│   │       └── index.ts                         # 匯出
│   └── middleware.ts                            # 路由保護中介軟體
├── NEXTAUTH_GUIDE.md                            # 完整使用指南
```

### 主要修改檔案
```
- src/app/providers.tsx               # 加入 SessionProvider
- src/app/(auth)/login/page.tsx       # 使用 NextAuth signIn()
- src/app/(app)/layout.tsx            # 顯示使用者資訊與登出
- README.md                           # 更新技術棧與使用說明
- biome.json                          # 更新到最新版本
```

## 🔧 設定需求

### 環境變數 (.env.local)
```env
# NextAuth
NEXTAUTH_SECRET=your-secret-here              # 使用 openssl rand -base64 32 生成
NEXTAUTH_URL=http://localhost:3000            # 前端 URL

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Google OAuth 設定
1. 前往 [Google Cloud Console](https://console.developers.google.com/)
2. 建立 OAuth 2.0 憑證
3. 設定授權的重新導向 URI：
   - 開發環境: `http://localhost:3000/api/auth/callback/google`
   - 正式環境: `https://yourdomain.com/api/auth/callback/google`

## 🧪 測試方式

### 1. 基本測試
```bash
cd apps/web
npm run dev
```

訪問 http://localhost:3000/auth-test 進行測試

### 2. 測試流程
1. 點擊「使用 Google 登入」
2. 完成 Google OAuth 授權
3. 檢查是否成功取得 session
4. 驗證使用者資訊是否正確顯示
5. 測試登出功能

### 3. 檢查 Session
在任何 Client Component 中：
```typescript
import { useSession } from 'next-auth/react'

const { data: session, status } = useSession()
console.log('Session:', session)
console.log('Status:', status)
```

## 🔐 安全性考量

✅ **已實作的安全措施**：
- Tokens 儲存在 httpOnly cookies（由後端設定）
- NextAuth 內建 CSRF 保護
- Session 使用 JWT strategy（無狀態）
- Middleware 自動保護需要登入的路由

⚠️ **注意事項**：
- 正式環境必須使用 HTTPS
- 定期更新 NEXTAUTH_SECRET
- 妥善保管 Google OAuth credentials
- 確保 Google OAuth redirect URI 設定正確

## 📚 架構說明

### 認證流程
```
1. 使用者點擊 Google 登入
   ↓
2. NextAuth 導向 Google OAuth
   ↓
3. Google 驗證並返回 ID token
   ↓
4. NextAuth JWT callback:
   - 發送 Google ID token 到後端 /api/v1/auth/google-login
   - 後端驗證 token 並創建/更新使用者
   - 後端返回 JWT tokens 並設定 httpOnly cookies
   - NextAuth 儲存使用者資訊到 JWT
   ↓
5. NextAuth Session callback:
   - 建立前端 session
   - 包含使用者 id, email 等資訊
   ↓
6. 使用者成功登入，可以使用 useSession() 存取 session
```

### Token 管理
- **NextAuth JWT**: 管理前端 session（7天有效期）
- **Backend Access Token**: 用於 API 請求（15分鐘有效期，httpOnly cookie）
- **Backend Refresh Token**: 用於更新 access token（7天有效期，httpOnly cookie）

Token 刷新由 `axios-interceptors.ts` 自動處理。

## 🔍 除錯技巧

### 啟用 Debug Mode
在 `.env.local` 中加入：
```env
NEXTAUTH_DEBUG=true
```

### 常見問題

**Q: 登入後沒有 session**
- 檢查 Google OAuth credentials 是否正確
- 檢查 redirect URI 是否符合
- 查看 browser console 和 server logs
- 確認後端 API 有正常回應

**Q: 401 錯誤**
- 檢查 cookies 是否正確設定
- 確認後端 CORS 設定
- 檢查 `withCredentials: true` 是否設定

**Q: Session 顯示但 API 請求失敗**
- 檢查 axios client 的 `withCredentials` 設定
- 確認後端 cookie domain 設定
- 檢查 CORS credentials 設定

## 📖 相關文件

- [NextAuth 整合指南](./NEXTAUTH_GUIDE.md) - 完整使用說明
- [README.md](./README.md) - 專案總覽
- [後端 README](../backend/README.md) - 後端 API 說明

## 🎓 學習資源

- [NextAuth.js 官方文件](https://next-auth.js.org/)
- [Google OAuth Provider](https://next-auth.js.org/providers/google)
- [Next.js App Router](https://nextjs.org/docs/app)

## ✨ 未來改進

建議的改進項目：
1. 加入錯誤處理頁面（自訂 error page）
2. 實作 refresh token rotation
3. 加入更多 OAuth providers（GitHub, Facebook 等）
4. 實作 email/password 登入（與 Google 並存）
5. 加入 session 過期提醒
6. 實作「記住我」功能

---

**實作完成日期**: 2026-01-26
**版本**: v1.0
**狀態**: ✅ Ready for Testing
