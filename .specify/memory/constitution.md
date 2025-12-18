# KCardSwap 專案憲法
<!-- 韓國偶像小卡交換平台 -->

> **語言聲明**：本專案所有規格、計畫、任務文件皆以繁體中文產出。

## 核心原則

### I. API 優先開發
所有功能透過 RESTful API 對外暴露，遵循 OpenAPI 規範。FastAPI 自動生成 Swagger 文件。輪詢端點針對高效訊息檢索和成本效益進行最佳化。

### III. 測試優先開發（不可妥協）
- 後端：實作前必須先撰寫單元測試（pytest）和整合測試（pytest + testcontainers）
- 前端：關鍵使用者流程需要單元測試（Jest）和端到端測試（Detox）
- 後端測試覆蓋率必須超過 80%
- 前端核心業務邏輯測試覆蓋率必須超過 70%
- PR 核准前所有測試必須通過

### IV. 程式碼品質標準
- 後端：使用 Ruff 進行 linting 和格式化（透過 pre-commit hooks 強制執行）
- 前端：請閱讀前端README.md
- 所有程式碼必須通過 CI/CD 管道的自動化品質檢查
- 清晰、描述性的命名規範
- 針對複雜業務邏輯添加適當註解

### V. 安全優先方針
- JWT Bearer Token 認證，使用安全儲存（expo-secure-store）
- Refresh token 機制：Access Token（15 分鐘），Refresh Token（7 天）
- 防護 SQL 注入、XSS 攻擊
- 靜態和傳輸中的敏感資料加密
- Google Cloud Storage signed URLs 附帶過期時間策略
- 定期安全稽核和依賴套件更新

### VI. Domain-Driven Design Architecture（領域驅動設計架構）

後端必須採用 Domain-Driven Design (DDD) 架構模式，確保業務邏輯與技術細節分離。

#### 四層架構強制規定

所有後端專案必須遵循以下四層架構，各層有明確的職責與依賴方向：

```
┌─────────────────────────────────────┐
│   Presentation Layer (API/UI)      │  ← FastAPI Routers, Request/Response Models
├─────────────────────────────────────┤
│   Application Layer (Use Cases)    │  ← Application Services, DTOs, Command/Query Handlers
├─────────────────────────────────────┤
│   Domain Layer (Business Logic)    │  ← Entities, Value Objects, Domain Services, Domain Events
├─────────────────────────────────────┤
│   Infrastructure Layer (技術實作)   │  ← Database, External APIs, File Storage, Message Queue
└─────────────────────────────────────┘
```

**依賴規則（Dependency Rule）**：
- 外層可以依賴內層，內層不得依賴外層
- Domain Layer 必須完全獨立，不依賴任何框架或基礎設施
- 所有跨層通訊透過介面（Interface/Protocol）與依賴注入（Dependency Injection）

#### 核心設計模式

**Repository Pattern（倉儲模式）**
- Domain Layer 定義 Repository 介面（Protocol），Infrastructure Layer 提供實作
- Repository 負責聚合根（Aggregate Root）的持久化與查詢
- 禁止在 Domain Layer 直接使用 ORM 或 SQL

**Dependency Injection（依賴注入）**
- 使用 FastAPI 的 `Depends` 機制進行依賴注入
- 所有 Repository、Service、Use Case 透過建構函式注入
- 配置統一管理於 `dependencies.py`

**Use Case Pattern（用例模式）**
- 每個業務用例封裝為獨立的 Use Case 類別
- Use Case 協調 Domain Entities、Services、Repositories
- Use Case 不含技術細節，僅處理業務流程

**Domain Events（領域事件）**
- 使用事件驅動架構處理跨聚合的業務邏輯
- Domain Layer 定義事件，Infrastructure Layer 實作事件匯流排
- 事件處理非同步執行（避免阻塞主流程）

**CQRS Pattern（命令查詢職責分離）**
- 寫操作（Command）與讀操作（Query）分離
- Command 修改狀態並返回最少資訊
- Query 優化讀取效能（可繞過 Domain Layer 直接查詢）

**Value Objects（值物件）**
- 不可變物件，通過值比較相等性
- 封裝驗證邏輯（如 Email 格式、經緯度範圍）
- 可在多個 Entity 間共用

#### 測試策略

**測試金字塔**
```
        ╱╲
       ╱E2E╲         ← 少量端到端測試（完整流程）
      ╱──────╲
     ╱Integration╲   ← 適量整合測試（含 DB、外部服務）
    ╱────────────╲
   ╱   Unit Tests  ╲ ← 大量單元測試（Domain & Application）
  ╱────────────────╲
```

- **單元測試**：測試 Domain Entities、Value Objects、Domain Services（不依賴 DB）
- **整合測試**：測試 Repositories、Use Cases（使用測試資料庫）
- **端到端測試**：測試完整 API 流程（從 HTTP Request 到 Response）

**測試隔離**
- Domain Layer 測試完全獨立，不啟動 FastAPI 應用
- Repository 測試使用 Test Database（Docker PostgreSQL）
- 外部服務使用 Mock（Google OAuth、GCS、FCM）

#### 實作檢查清單

開發時必須確保以下項目：
- [ ] 所有 Domain Entities 不依賴 FastAPI、SQLAlchemy 或其他框架
- [ ] Repository 介面定義在 Domain Layer，實作在 Infrastructure Layer
- [ ] Use Cases 不包含 SQL 查詢或 HTTP 請求邏輯
- [ ] Routers 僅負責請求驗證與回應格式化，業務邏輯委派給 Use Cases
- [ ] ORM Models 與 Domain Entities 分離
- [ ] 所有跨層依賴透過介面（Protocol）與依賴注入
- [ ] Domain Events 用於處理跨聚合的副作用
- [ ] Value Objects 封裝驗證邏輯且不可變
- [ ] 單元測試覆蓋率達 80% 以上（Domain & Application Layer）

## 後端架構

### 技術堆疊
- **框架**：FastAPI
- **ORM**：SQLAlchemy
- **資料庫**：PostgreSQL（Google Cloud SQL）
- **遷移工具**：Alembic
- **API Gateway**：Kong Gateway (OSS) + Nginx（POC 階段）、Google Cloud API Gateway（正式環境）
- **訊息系統**：HTTP 輪詢（3-5 秒間隔）+ Firebase Cloud Messaging（FCM）
- **檔案儲存**：Google Cloud Storage（GCS）with CDN
- **身份驗證**：JWT Bearer Token、Google 登入（POC 階段）
- **部署平台**：Google Cloud Platform（Cloud Run 或 GKE）

### 架構模式
- 領域驅動設計（DDD）with 明確的限界上下文
- Repository 模式進行資料存取
- Service 層進行業務邏輯編排
- 依賴注入以提升可測試性

### API 設計標準
- RESTful 原則，資源導向的 URL
- 一致的回應格式和正確的 HTTP 狀態碼
- 自動生成 OpenAPI/Swagger 文件
- 為未來擴展準備的版本控制策略
- 輪詢端點使用基於時間戳的過濾進行最佳化
- GCS signed URL 生成以確保檔案上傳安全

### 測試需求
- 領域邏輯和服務的單元測試
- 使用 testcontainers 的整合測試
- API 端點測試（包含輪詢端點）
- Google Cloud Storage 整合測試
- Firebase Cloud Messaging 整合測試
- 最低 80% 程式碼覆蓋率

## 前端架構

### 技術堆疊
- **平台**：React Native with Expo（Managed Workflow）
- **UI 函式庫**：React Native Paper（Material Design）
- **狀態管理**：Zustand
- **導航**：React Navigation
- **建置與部署**：EAS Build、EAS Submit
- **測試**：Jest（單元測試）、Maestro 或 Detox（E2E）

### 原生功能整合（Expo SDK）
- **相機與相簿**：expo-image-picker，自動壓縮
- **推播通知**：expo-notifications + Firebase Cloud Messaging（FCM）
- **聊天系統**：HTTP 短輪詢（3-5 秒間隔）用於活躍聊天
- **安全儲存**：expo-secure-store 用於 JWT tokens
- **檔案上傳**：多圖上傳並自動壓縮至 Google Cloud Storage
  - 免費會員：每張最大 2MB，總容量 100MB
  - 付費會員：每張最大 5MB，總容量 1GB
- **Deep Linking**：expo-linking 用於分享和通知
- **OAuth**：expo-auth-session with Google 登入
- **OTA 更新**：expo-updates 用於快速修復 bug，無需重新提交 App Store
- **背景任務**：expo-background-fetch 用於 app 在背景時同步訊息
- **定位**：expo-location 用於附近使用者搜尋功能

### 元件架構
- 函式式元件（Functional components）搭配 hooks
- 清晰的元件層級和可重用性
- 展示型元件（presentational）和容器型元件（container）分離
- 適當的 prop types 和 TypeScript 支援

### 測試需求
- 業務邏輯和工具函式的單元測試（Jest）
- 關鍵 UI 元件的元件測試（React Native Testing Library）
- 核心使用者流程的端到端測試，使用 Maestro（Expo 推薦）或 Detox
  - 註冊和 Google 登入流程
  - 使用 image picker 上傳小卡並壓縮
  - 瀏覽和篩選交換列表
  - 附近使用者搜尋
  - 聊天功能（含輪詢）
  - 推播通知處理
- 核心業務邏輯最低 70% 覆蓋率

## 基礎設施與 DevOps

### POC 階段部署（初期階段）
- **運算資源**：單一 GCE 實例（e2-medium，約 $24/月）
  - Kong Gateway（Docker 容器）- 開源 API Gateway
  - FastAPI 後端（Docker 容器）
  - PostgreSQL 資料庫（Docker 容器）- 同時供 Kong 和 FastAPI 使用
  - Nginx（Docker 容器）- SSL 終端 with Let's Encrypt HTTPS
  - Redis（可選，用於 Kong rate limiting 和快取）
- **檔案儲存**：Google Cloud Storage（GCS）
  - 單一儲存桶：kcardswap-images
  - 生命週期策略：免費使用者不活躍 90 天後自動刪除
  - CDN 快取：頻繁存取的圖片使用 Cache-Control headers
- **訊息推送**：Firebase Cloud Messaging（FCM）推播通知（免費方案）
- **備份策略**：
  - 每日自動備份 PostgreSQL 至 Cloud Storage（cron job）
  - 備份保留期：開發期 7 天，上線後 30 天
  - 備份腳本使用 gzip 壓縮
- **安全性**：
  - 防火牆規則：僅開放 80（HTTP）、443（HTTPS）、22（SSH 管理）
  - PostgreSQL port 5432 不對外開放
  - 僅允許 SSH key 認證（停用密碼登入）
- **監控**：
  - GCP Monitoring 監控 VM 指標（CPU、記憶體、磁碟使用量）
  - 磁碟使用率 > 80% 時告警
  - CPU 使用率 > 90% 持續 5 分鐘時告警
  - PostgreSQL 慢查詢日誌記錄

**POC 階段預估成本（100-200 MAU）**：
- GCE e2-medium：$24/月
- Cloud Storage（10GB 圖片）：$2-5/月
- Firebase FCM：免費方案
- **總計**：約 $30/月

### 正式環境部署（Post-POC，>500 MAU）
- **運算資源**：Google Cloud Run 或 Google Kubernetes Engine（GKE）
  - 基於流量自動擴展
  - 零停機部署
- **資料庫**：Google Cloud SQL for PostgreSQL
  - 每日自動備份
  - 時間點恢復（Point-in-time recovery）
  - 自動安全性修補
  - 高可用性選項（關鍵階段）
- **檔案儲存**：Google Cloud Storage（GCS）
  - 不同使用者層級和內容類型使用獨立儲存桶
  - 自動圖片最佳化和 CDN 分發
  - 免費會員不活躍 90 天後自動清理的生命週期策略
- **API Gateway**：Google Cloud API Gateway 或 Kong Enterprise on GKE
  - 進階 API 管理功能（版本控制、流量控管、分析）
  - 自動擴展和高可用性
  - 與 GCP 服務深度整合
- **訊息推送**：Firebase Cloud Messaging（FCM）推播通知
- **監控**：Google Cloud Monitoring and Logging
- **部署**：透過 Cloud Run 或 GKE 的滾動更新策略

### 本地開發環境
- **工具**：Docker + Docker Compose
- **API Gateway**：Kong Gateway（本地容器）
- **資料庫**：PostgreSQL 容器（Kong + FastAPI 共用）
- **檔案儲存**：GCS emulator 或本地檔案系統（開發用）
- **測試**：Firebase emulator suite 用於 FCM 測試

### CI/CD 管道
- **平台**：GitHub Actions
- **觸發條件**：PR 提交時自動觸發
- **檢查項目**：
  - 後端：Ruff linting、pytest 測試、覆蓋率報告
  - 前端：Biome linting、Jest 測試、Maestro/Detox E2E 測試
- **部署**：
  - 後端：合併至 main 後自動部署至 GCP Cloud Run
  - 行動應用：使用 EAS Build 自動建置（無需 Mac 即可建置 iOS）
  - 分發：透過 EAS Submit 分發至 TestFlight（iOS）和 Internal Testing（Android）
  - OTA 更新：使用 expo-updates 進行非原生程式碼變更

## 開發工作流程

### Git 策略
簡化版 GitHub Flow：
- **main**：隨時可部署的正式環境分支
- **feature/xxx**：功能開發分支
- **hotfix/xxx**：緊急 bug 修復分支
- 所有變更透過 Pull Request 並經過必要審查

### 分支命名規範
- `feature/user-authentication`（功能/使用者認證）
- `feature/card-upload`（功能/小卡上傳）
- `bugfix/image-compression`（錯誤修復/圖片壓縮）
- `hotfix/critical-security-patch`（熱修復/關鍵安全性修補）

### 程式碼審查流程

#### 自動化檢查（必須通過）
1. 後端：Ruff 風格檢查、pytest 測試、覆蓋率 > 80%
2. 前端：Biome 風格檢查、Jest 測試、Maestro/Detox E2E 測試
3. Expo：EAS Build 預覽建置通過
4. 無合併衝突
5. 所有 CI/CD 管道檢查皆為綠燈

#### 人工審查檢查清單
- **功能性**：符合需求、邊界情況已處理
- **程式碼品質**：可讀性高、命名清晰、註解適當
- **架構**：遵循 DDD（後端）和元件模式（前端）
- **安全性**：無 SQL 注入風險、XSS 防護、安全 token 處理、GCS signed URLs 正確配置
- **效能**：無 N+1 查詢、React Native 高效渲染、輪詢間隔最佳化
- **原生功能**：相機、推播通知、輪詢機制、GCS 上傳、定位服務正常運作
- **成本最佳化**：圖片壓縮正常運作、儲存生命週期策略已就緒
- **文件**：README 已更新、API 文件最新、PR 描述清晰

#### 審查流程
1. 開發者在本地執行 pre-commit hooks
2. Push 觸發 GitHub Actions 自動化測試
3. 根據檢查清單進行自我審查後再請求審查
4. 所有檢查通過後核准合併
5. 每週進行程式碼品質和技術債務審查會議

## 文件標準

### 必要文件
### README 結構
1. 專案概述和目標
2. 先決條件（Node.js、Expo CLI、EAS CLI、Docker、GCP 帳號）
3. GCP 設定指南：
   - Cloud SQL PostgreSQL 實例建立
   - Cloud Storage bucket 配置
   - Firebase 專案設定（用於 FCM）
   - Service account 和憑證
   - IAM 角色和權限
4. 安裝說明（後端 + Expo app）
5. 本地執行：
   - 後端：Docker Compose with GCS emulator
   - 前端：`expo start` 或 `npx expo start`
6. 執行測試（pytest、Jest、Maestro）
7. 建置和部署流程：
   - 後端：Cloud Run 或 GKE 部署
   - 前端：EAS Build、EAS Submit、OTA 更新
8. 架構概述（DDD 後端、Expo 前端、GCP 基礎設施）
9. 成本估算和最佳化策略
10. 貢獻指南

## POC 階段優先事項

### 核心功能（MVP）
1. 使用者註冊/登入 with Google 登入
2. 小卡上傳，自動壓縮並儲存至 GCS
3. 瀏覽交換列表，支援篩選（距離、偶像、卡片類型）
4. 附近使用者搜尋，基於位置的篩選
5. 一對一聊天，使用 HTTP 輪詢（3-5 秒間隔）
6. 新訊息和交換請求的推播通知
7. 基本使用者個人檔案和好友管理

### 基礎設施設定
- Google Cloud Platform：
  - Cloud SQL PostgreSQL 用於資料庫
  - Cloud Storage 用於圖片託管 with CDN
  - Cloud Run 用於後端部署
  - Firebase 用於推播通知（FCM）
- 本地開發：Docker Compose with GCS emulator
- 前端 Expo 開發伺服器（`expo start`）
- GitHub Actions CI/CD 管道整合 GCP 部署和 EAS Build
- 透過 EAS Submit 分發至 TestFlight（iOS）和 Internal Testing（Android）
- OTA 更新配置以實現快速迭代

### 成功標準
- 使用者可透過 Google 註冊和驗證
- 使用者可上傳和瀏覽小卡，壓縮正常運作
- 使用者可在指定半徑內找到附近使用者
- 使用者可聊天，訊息延遲 3-5 秒（POC 可接受）
- 推播通知在 app 於背景時可靠運作
## 治理

### 憲法權威
本憲法高於所有其他開發實踐和指導方針。所有程式碼審查、PR 和架構決策必須驗證是否符合這些原則。

### 修訂流程
1. 提出修訂案並附上清晰的理由
2. 團隊討論並達成共識
3. 更新憲法並增加版本號
4. 向所有團隊成員傳達變更
5. 更新相關文件和流程

### 執行
- 所有 PR 必須證明遵守憲法原則
- 違規必須提供文件化的理由說明
- 定期稽核以確保持續合規
- 新團隊成員必須審閱並確認憲法

**版本**：1.2.0 | **批准日期**：2025-12-10 | **最後修訂**：2025-12-10
5. Update related documentation and processes
---

## 附錄：技術實作細節

### 聊天系統架構（輪詢 + 推播通知）

#### 活躍聊天（App 前景 - 聊天畫面開啟）
```
- HTTP 短輪詢：GET /api/chats/{chat_id}/messages?since={timestamp}
- 輪詢間隔：3-5 秒
- 使用基於時間戳的過濾進行高效查詢
- 使用者離開聊天畫面時自動停止輪詢
- 錯誤時使用指數退避（exponential backoff）
```

#### 背景/關閉 App
```
- Firebase Cloud Messaging（FCM）推播通知
- 伺服器在新訊息時發送 FCM 通知
- 使用者點擊通知 → 開啟聊天並獲取訊息
- 更新 badge 計數器
```

#### 訊息儲存與同步
```
- 所有訊息持久化儲存於 Cloud SQL PostgreSQL
- 支援離線訊息佇列和重試機制
- 支援多裝置同步
- 訊息傳遞狀態追蹤（已發送、已送達、已讀）
```adge counter updates
```
### 圖片儲存策略（Google Cloud Storage）

#### 上傳流程
1. 前端：expo-image-picker 拍攝/選擇圖片
2. 前端：根據使用者層級壓縮圖片：
   - 免費會員：最大 2MB，品質 80%
   - 付費會員：最大 5MB，品質 90%
3. 前端：向後端請求 signed URL
4. 後端：生成 GCS signed URL（15 分鐘過期）
5. 前端：透過 signed URL 直接上傳至 GCS
6. 後端：儲存圖片 metadata（GCS URL、大小、尺寸、user_id）至資料庫
7. 後端：生成縮圖（200x200）用於列表檢視

#### 儲存組織架構
```
Bucket: kcardswap-images-production
├── users/
│   └── {user_id}/
│       ├── avatar.jpg
│       └── avatar_thumb.jpg
├── cards/
│   └── {card_id}/
│       ├── original.jpg
│       └── thumbnail.jpg
└── temp/
    └── {upload_id}.jpg (24 小時後自動刪除)
```

#### 成本最佳化策略
- 免費會員：帳號不活躍 90 天後自動清理圖片
- 頻繁存取的圖片使用 CDN 快取（Cache-Control: max-age=86400）
- 列表檢視生成縮圖以減少頻寬（縮小 80%）
- 暫存上傳的生命週期策略（24 小時後刪除）
- 上傳前壓縮（客戶端使用 expo-image-manipulator）
- 停用物件版本控制以節省儲存成本

#### 安全性與存取控制
- 帶過期時間的 Signed URLs（上傳 15 分鐘，檢視 1 小時）
- 物件層級 IAM 權限（預設為私有）
- 為 Expo app 網域配置 CORS
- Content-Type 驗證（僅允許 image/jpeg、image/png）
- 檔案大小驗證（後端雙重檢查）
- 上傳檔案病毒掃描（可選，Cloud Security Scanner）
- Object versioning disabled to save storage costs
### 會員分級系統

#### 免費會員限制
- 每日上傳：3 張小卡
- 每日發布：2 則交換貼文
- 附近搜尋：每日 5 次
- 好友上限：20 位好友
- 活躍聊天室：同時 5 個
- 圖片儲存：每張 2MB，總計 100MB
- 推播通知：僅關鍵通知（訊息、交換請求）

#### 付費會員權益（NT$ 99/月 或 NT$ 990/年）
- 無限每日上傳
- 無限交換貼文發布
- 無限附近搜尋
- 無限好友數量
- 無限聊天室數量
- 圖片儲存：每張 5MB，總計 1GB
- 推播通知：所有功能（附近新卡片、喜愛偶像更新）
- 搜尋結果優先顯示
- 進階篩選（稀有度、年份、特定專輯）
- 無限交換歷史記錄
- 專屬付費會員徽章ings
- Unlimited nearby searches
### 定位功能

#### 附近使用者搜尋
- 使用 expo-location 取得 GPS 座標
- 隱私保護：僅顯示區域/地區（例如「台北市大安區」）
- 距離篩選：1km / 5km / 10km / 全部
- 搜尋結果顯示：
  - 使用者名稱、頭像、距離
  - 可交換小卡數量
  - 使用者評分（基於完成的交換次數）
  - 線上狀態

#### 地理位置隱私
- 使用者可啟用「隱身模式」（無法被搜尋）
- 僅在 app 活躍時更新位置
- 顯示大約距離（例如「1-3 公里」）
- 可選擇手動設定位置而不使用 GPS

### 交換流程與評分系統

#### 交換提案
1. 使用者 A 在聊天中發起交換
2. 選擇自己的卡片 + 目標使用者的卡片
3. 使用者 B 收到通知和提案
4. 使用者 B 可以接受、拒絕或反提案
5. 雙方確認 → 建立交換記錄

#### 面對面見面
1. 使用者透過聊天約定時間和地點
2. 雙方在 app 中標記「交換完成」
3. 可選：上傳見面證明照片

#### 評分系統
- 交換完成後給予 5 星評分
- 可選文字回饋
- 評分顯示於使用者個人檔案
- 低評分使用者標記為待審查

#### 檢舉與安全
- 檢舉按鈕用於詐騙、騷擾、假卡
- 封鎖使用者功能
- 管理員審查系統用於被檢舉使用者
- 多次檢舉自動暫停帳號
- Optional text feedback
- Ratings visible on user profile
- Users with low ratings flagged for review

#### Report & Safety
- Report button for scams, harassment, fake cards
- Block user feature
- Admin review system for reported users
- Automatic suspension for multiple reports

### API Gateway 架構（Kong Gateway）

#### POC 階段架構
```
[Expo App]
    ↓ HTTPS (443)
[Nginx - SSL Termination]
    ↓ HTTP (8000)
[Kong Gateway]
    ├─ JWT Plugin（驗證 Access Token）
    ├─ Rate Limiting Plugin（免費/付費分級限流）
    ├─ CORS Plugin（Expo app CORS 配置）
    ├─ Request/Response Logging Plugin
    ├─ IP Restriction Plugin（可選，封鎖惡意 IP）
    ↓ HTTP (8080)
[FastAPI Backend]
    ↓
[PostgreSQL]
```

#### Kong Gateway 核心功能

**1. JWT 認證自動化**
- Kong JWT Plugin 自動驗證 Bearer Token
- 無效或過期 token 自動返回 401
- 減少 FastAPI 認證負擔

**2. 會員分級限流**
```yaml
# 免費會員限流配置
Rate Limiting:
  - 每日上傳小卡：3 次/天（POST /api/v1/cards）
  - 每日發布貼文：2 次/天（POST /api/v1/posts）
  - 附近搜尋：5 次/天（GET /api/v1/users/nearby）
  - 一般 API：100 次/分鐘

# 付費會員限流配置
Rate Limiting:
  - 上傳小卡：無限制
  - 發布貼文：無限制
  - 附近搜尋：無限制
  - 一般 API：1000 次/分鐘
```

**3. API 版本管理**
```
路由規則：
  /api/v1/* → FastAPI Backend v1
  /api/v2/* → FastAPI Backend v2（未來擴展）
```

**4. CORS 自動處理**
- 自動為 Expo app 配置 CORS headers
- 支援 expo.dev 和自訂網域
- 預檢請求（OPTIONS）自動處理

**5. 日誌與監控整合**
- 所有 API 請求自動記錄至 GCP Logging
- 記錄內容：請求路徑、方法、狀態碼、延遲、user_id
- 支援錯誤追蹤和效能分析

#### Kong 部署配置（Docker Compose）

```yaml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - kong
    restart: always

  kong:
    image: kong:3.4-alpine
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: postgres
      KONG_PG_DATABASE: kong
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: ${KONG_DB_PASSWORD}
      KONG_PROXY_LISTEN: 0.0.0.0:8000
      KONG_ADMIN_LISTEN: 127.0.0.1:8001
      KONG_PROXY_ACCESS_LOG: /dev/stdout
      KONG_ADMIN_ACCESS_LOG: /dev/stdout
      KONG_PROXY_ERROR_LOG: /dev/stderr
      KONG_ADMIN_ERROR_LOG: /dev/stderr
    depends_on:
      - postgres
      - kong-migration
    restart: always

  kong-migration:
    image: kong:3.4-alpine
    command: kong migrations bootstrap
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: postgres
      KONG_PG_DATABASE: kong
      KONG_PG_USER: kong
      KONG_PG_PASSWORD: ${KONG_DB_PASSWORD}
    depends_on:
      - postgres
    restart: on-failure

  fastapi:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://user:pass@postgres/kcardswap
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
    depends_on:
      - postgres
    restart: always

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_MULTIPLE_DATABASES: kong,kcardswap
    volumes:
      - pg_data:/var/lib/postgresql/data
      - ./init-multi-db.sh:/docker-entrypoint-initdb.d/init-multi-db.sh
    restart: always

volumes:
  pg_data:
```

#### Kong 插件配置範例

**JWT 認證插件**
```bash
curl -X POST http://localhost:8001/services/fastapi-service/plugins \
  --data "name=jwt" \
  --data "config.secret_is_base64=false" \
  --data "config.key_claim_name=sub"
```

**Rate Limiting 插件（免費會員）**
```bash
curl -X POST http://localhost:8001/services/fastapi-service/routes/upload-card/plugins \
  --data "name=rate-limiting" \
  --data "config.minute=null" \
  --data "config.day=3" \
  --data "config.policy=local"
```

**CORS 插件**
```bash
curl -X POST http://localhost:8001/services/fastapi-service/plugins \
  --data "name=cors" \
  --data "config.origins=*" \
  --data "config.methods=GET,POST,PUT,DELETE,PATCH,OPTIONS" \
  --data "config.headers=Authorization,Content-Type" \
  --data "config.credentials=true" \
  --data "config.max_age=3600"
```

#### 成本與效能

**POC 階段成本（Kong 免費）**
- GCE e2-medium：$24/月（不變）
- Kong Gateway (OSS)：免費
- PostgreSQL（Kong + FastAPI 共用）：包含在 GCE 成本中
- **總計**：約 $30/月

**效能優勢**
- Kong 使用 Nginx + OpenResty（Lua），效能極高
- 單機可處理 10,000+ req/s
- 對於 POC 階段（100-200 MAU）綽綽有餘

**升級路徑**
- POC 成功後可升級至 Kong Enterprise（付費版）
- 或遷移至 Google Cloud API Gateway
- Kong 配置可導出為 OpenAPI 規範，便於遷移
