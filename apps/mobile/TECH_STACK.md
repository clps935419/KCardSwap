# KCardSwap Mobile - 前端技術文件 (Frontend Technical Documentation)

**Version:** 1.0.0  
**Last Updated:** 2025-12-18  
**Expo SDK:** 54.0.29  
**React Native:** 0.81.5

---

## 目錄 (Table of Contents)

1. [核心技術棧 (Core Tech Stack)](#核心技術棧-core-tech-stack)
2. [Expo 套件清單 (Expo Packages)](#expo-套件清單-expo-packages)
3. [狀態管理 (State Management)](#狀態管理-state-management)
4. [UI 與樣式 (UI & Styling)](#ui-與樣式-ui--styling)
5. [API 與網路 (API & Networking)](#api-與網路-api--networking)
6. [導航 (Navigation)](#導航-navigation)
7. [測試 (Testing)](#測試-testing)
8. [程式碼品質工具 (Code Quality Tools)](#程式碼品質工具-code-quality-tools)
9. [開發工具鏈 (Development Toolchain)](#開發工具鏈-development-toolchain)
10. [套件使用指南 (Package Usage Guide)](#套件使用指南-package-usage-guide)

---

## 核心技術棧 (Core Tech Stack)

### Framework & Runtime

| 套件             | 版本     | 用途                  | 文檔連結                                              |
| ---------------- | -------- | --------------------- | ----------------------------------------------------- |
| **Expo**         | ~54.0.29 | React Native 開發框架 | [docs.expo.dev](https://docs.expo.dev/)               |
| **React Native** | 0.81.5   | 跨平台移動應用框架    | [reactnative.dev](https://reactnative.dev/)           |
| **React**        | 19.1.0   | UI 函式庫             | [react.dev](https://react.dev/)                       |
| **TypeScript**   | ~5.9.2   | 靜態型別檢查          | [typescriptlang.org](https://www.typescriptlang.org/) |

### 架構特性

- ✅ **New Architecture Enabled** - 使用 React Native 新架構 (Fabric + Bridgeless)
- ✅ **TypeScript Strict Mode** - 完整型別安全
- ✅ **File-based Routing** - Expo Router 檔案導航
- ✅ **Modular Architecture** - 功能模組化設計

---

## In-App Purchases（Subscriptions / US6）

### POC 決議

- **需要 Expo Development Build**：IAP/Billing 依賴原生模組，Expo Go 不支援
- **套件選型（POC）**：`react-native-iap`（Android subscriptions）
- **購買成功判準**：App 端不可只以購買 UI/回呼成功視為 premium 生效；必須取得 `purchase_token` 後呼叫後端 `POST /api/v1/subscriptions/verify-receipt`，並以回傳 `entitlement_active=true` 更新權限與 UI
- **同步策略（無 RTDN）**：App 開啟/回前景呼叫 `GET /api/v1/subscriptions/status`；後端每日排程降級兜底
- **Restore（不新增 API）**：App 端 query 既有購買 → 逐一呼叫 `verify-receipt` 恢復 entitlement

---

## Expo 套件清單 (Expo Packages)

### 認證與安全 (Authentication & Security)

#### expo-auth-session (v7.0.10)

**用途:** Google OAuth 認證 (PKCE Flow)  
**使用場景:** US1 - Google 登入  
**關鍵功能:**

- Authorization Code Flow with PKCE
- 自動處理 redirect URI
- 支援 iOS/Android 深度連結

**使用範例:**

```typescript
import * as AuthSession from 'expo-auth-session';
import * as WebBrowser from 'expo-web-browser';

// 設定 PKCE 參數
const discovery = AuthSession.useAutoDiscovery('https://accounts.google.com');
const [request, response, promptAsync] = AuthSession.useAuthRequest(
  {
    clientId: 'YOUR_CLIENT_ID',
    redirectUri: AuthSession.makeRedirectUri({ scheme: 'kcardswap' }),
    scopes: ['openid', 'profile', 'email'],
    usePKCE: true, // 啟用 PKCE
  },
  discovery
);
```

#### expo-secure-store (v15.0.8)

**用途:** 加密儲存敏感資料 (Token)  
**使用場景:** Token 與用戶資料儲存  
**關鍵功能:**

- iOS Keychain / Android Keystore 加密
- 異步存取 API
- 自動處理平台差異

**已實作:** `src/shared/auth/session.ts`

#### expo-crypto (v15.0.8)

**用途:** 加密演算法支援  
**使用場景:** PKCE code verifier 生成、資料加密  
**關鍵功能:**

- SHA-256 雜湊
- 隨機數生成
- Base64 編碼

---

### 圖片與媒體 (Image & Media)

#### expo-image-picker (v17.0.10)

**用途:** 選擇圖片/拍照  
**使用場景:** US2 - 小卡上傳  
**關鍵功能:**

- 相機拍照
- 相簿選取
- 權限管理
- 圖片裁切

**使用範例:**

```typescript
import * as ImagePicker from 'expo-image-picker';

// 請求相機權限
const { status } = await ImagePicker.requestCameraPermissionsAsync();

// 選擇圖片
const result = await ImagePicker.launchImageLibraryAsync({
  mediaTypes: ImagePicker.MediaTypeOptions.Images,
  allowsEditing: true,
  aspect: [4, 3],
  quality: 0.8,
});

if (!result.canceled) {
  const imageUri = result.assets[0].uri;
  // 處理圖片...
}
```

#### expo-camera（相機預覽 + 自訂 overlay，引導框 POC）

**用途:** 自建相機畫面（Camera Preview），支援在拍照畫面上疊加「框線/角標/提示文字」等引導 UI。

**為什麼需要它（US2 拍照引導框）**

- `expo-image-picker` 的 `launchCameraAsync()` 走系統相機 UI，無法在「拍照當下」自訂疊加框線與提示。
- 若需求是「相機畫面出現框，使用者把卡片對齊框再拍照」，需使用 `expo-camera` 的 `CameraView` + React Native overlay（絕對定位）。

**POC 建議（固定提示 + 依框裁切，不做自動偵測）**

1. `CameraView` 全螢幕預覽
2. 用 `position: 'absolute'` 疊一個半透明 overlay，包含：框線、四角標記、提示文案（固定）
3. 按快門呼叫 `takePictureAsync()` 取得照片（uri + width/height）
4. 依框線區域裁切：用 `expo-image-manipulator` crop 出卡片圖

**關鍵技術點：座標映射（一定要寫清楚避免裁切歪）**

- 框線座標屬於「preview view 座標系」；照片裁切需要「照片像素座標系」。
- 建議將框線區域用相對比例保存（x/y/width/height 皆為 0..1，相對於 preview 內容區），再換算：
  - `cropX = x * photoWidth`
  - `cropY = y * photoHeight`
  - `cropW = width * photoWidth`
  - `cropH = height * photoHeight`
- **避免映射偏移**：盡量讓 preview 顯示比例與拍照輸出比例一致（例如固定 4:3 或 16:9），並避免 preview 使用 cover 造成畫面裁切；若 unavoidable，需要把 cover 的裁切偏移量納入換算。

> 目標是先做出「能引導對齊、裁切大致準」的 POC；後續若要做到自動偵測卡片邊緣/透視矯正，會需要更進階的 CV（例如 document scanner / VisionCamera + frame processor）。

#### expo-image-manipulator (v14.0.8)

**用途:** 圖片處理與壓縮  
**使用場景:** US2 - 圖片壓縮 (≤10MB)  
**關鍵功能:**

- 圖片縮放
- 格式轉換 (JPEG/PNG)
- 壓縮品質控制
- 裁切與旋轉

**使用範例:**

```typescript
import * as ImageManipulator from 'expo-image-manipulator';

// 壓縮圖片
const manipResult = await ImageManipulator.manipulateAsync(
  imageUri,
  [{ resize: { width: 1920 } }], // 縮放到寬度 1920px
  { compress: 0.7, format: ImageManipulator.SaveFormat.JPEG }
);

// 檢查檔案大小
const fileSize = manipResult.uri.length; // 簡化示例
if (fileSize > 10 * 1024 * 1024) {
  // 檔案超過 10MB，需要進一步壓縮
}
```

#### US2：Signed URL Upload（直傳 GCS）

**目標:** 小卡上傳採「先向後端取 Signed URL → 前端直傳雲端」模式，後端只負責簽名與建立卡片記錄。

**建議流程（最小可行）:**

1. 選擇圖片（拍照/相簿）
2. 本機壓縮/轉檔（JPEG/PNG，≤10MB）
3. 呼叫 `POST /cards/upload-url` 取得：`upload_url` + `method` + `required_headers` + `image_url`（使用 hey-api 的 TanStack Query mutation）
4. 依回應指定的 `method` 與 `required_headers`，使用獨立 `fetch()` 直接上傳到 `upload_url`
5. 上傳成功後刷新「我的卡冊」列表（`GET /cards/me`，使用 TanStack Query）

**重要注意:**

- **取得 Signed URL**（`POST /cards/upload-url`）**必須**走 hey-api 生成的 TanStack Query mutation（可享有 token / refresh / 型別安全）
- **直傳雲端的上傳請求**（對 `upload_url` 做 PUT/POST）**不可**走 SDK：
  - 使用獨立的 `fetch()`（或等價 HTTP client）
  - **完全依照後端回傳的 `method` 與 `required_headers`** 送出
  - 不可自動注入 Authorization 或其他非必要 header
- 上傳錯誤需分流處理：
  - 後端 API 錯誤（例如 422 配額/檔案過大）→ 走既有 `errorMapper`
  - Signed URL 上傳錯誤（例如 403/過期、網路中斷、timeout、5xx）→ 以 status + 可重試條件顯示對應訊息

#### US2：縮圖產生與本機快取（200x200）

**需求:** 產生 200x200 縮圖供卡冊列表快速載入；縮圖不上傳、不進後端 API 定義。

**建議行為:**

- 產生縮圖：固定 200x200；優先 WebP（若平台不支援，需定義 fallback 格式，例如 JPEG）
- 快取 key：建議用 `card_id` 或 `image_url` 雜湊，避免同名覆蓋
- 失效策略：刪卡時移除縮圖；若找不到縮圖則回退載入原圖（fallback）
- 容量策略：需定義上限（張數或總大小），避免無限成長（可先用最小可行策略，後續再優化）

---

### 定位服務 (Location Services)

#### expo-location (v19.0.8)

**用途:** 地理定位與權限管理  
**使用場景:** US3 - 附近小卡搜尋  
**關鍵功能:**

- 獲取當前位置
- 持續定位追蹤
- 權限請求與處理
- 地理編碼 (Geocoding)

**使用範例:**

```typescript
import * as Location from 'expo-location';

// 請求前景定位權限
const { status } = await Location.requestForegroundPermissionsAsync();
if (status !== 'granted') {
  console.error('定位權限被拒絕');
  return;
}

// 獲取當前位置
const location = await Location.getCurrentPositionAsync({
  accuracy: Location.Accuracy.Balanced,
});

const { latitude, longitude } = location.coords;
console.log(`座標: ${latitude}, ${longitude}`);
```

---

### 推播通知 (Push Notifications)

#### expo-notifications (v0.32.15)

**用途:** 推播通知 (FCM)  
**使用場景:** US4 - 聊天訊息通知  
**關鍵功能:**

- 本地通知
- 遠端推播 (FCM)
- 通知權限管理
- 通知點擊處理

**使用範例:**

```typescript
import * as Notifications from 'expo-notifications';

// 請求通知權限
const { status } = await Notifications.requestPermissionsAsync();

// 獲取推播 Token
const token = (await Notifications.getExpoPushTokenAsync()).data;
console.log('推播 Token:', token);

// 設定通知處理器
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

// 監聽通知點擊
Notifications.addNotificationResponseReceivedListener((response) => {
  const data = response.notification.request.content.data;
  // 導航至聊天室...
});
```

---

### 裝置資訊 (Device Information)

#### expo-device (v8.0.10)

**用途:** 裝置資訊與類型檢測  
**關鍵功能:**

- 裝置型號/品牌
- 系統版本
- 裝置類型 (手機/平板)
- 支援檢測

#### expo-application (v7.0.8)

**用途:** 應用程式資訊  
**關鍵功能:**

- App 版本
- Build 編號
- Bundle ID
- 安裝來源

---

### 路由與導航 (Routing & Navigation)

#### expo-router (v6.0.19)

**用途:** 檔案式路由導航  
**架構:**

```
app/
├── _layout.tsx          # 根布局 (Root Layout)
├── auth/
│   └── login.tsx       # 登入頁面
└── (tabs)/             # 主要 Tab 導航
    ├── _layout.tsx     # Tab 配置
    ├── index.tsx       # 首頁
    ├── cards.tsx       # 我的卡冊
    ├── nearby.tsx      # 附近搜尋
    └── profile.tsx     # 個人檔案
```

**特性:**

- ✅ 檔案即路由
- ✅ 自動型別推導
- ✅ Deep Linking 支援
- ✅ Tab/Stack 導航整合

**已實作:** `app/_layout.tsx` - 認證流程保護

---

### 其他核心套件 (Other Core Packages)

#### expo-constants (v18.0.12)

**用途:** 環境變數與常量  
**使用場景:** 讀取 `.env` 配置

#### expo-linking (v8.0.10)

**用途:** Deep Linking 處理  
**使用場景:** OAuth redirect, 推播導航

#### expo-status-bar (v3.0.9)

**用途:** 狀態欄樣式控制

#### @expo/vector-icons (v15.0.3)

**用途:** 圖示庫 (Ionicons, MaterialIcons 等)  
**使用場景:** Tab 圖示、UI 元件圖示

---

## 狀態管理 (State Management)

### Zustand (v5.0.9)

**用途:** 全域狀態管理 (Global State)  
**特性:**

- ✅ 輕量級 (~1KB)
- ✅ 無 Provider 包裹
- ✅ TypeScript 友善
- ✅ DevTools 支援

**已實作:** `src/shared/state/authStore.ts`

**使用範例:**

```typescript
import { create } from 'zustand';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  login: (user) => set({ user, isAuthenticated: true }),
  logout: () => set({ user: null, isAuthenticated: false }),
}));

// 在元件中使用
function ProfileScreen() {
  const { user, logout } = useAuthStore();
  // ...
}
```

### TanStack Query (v5.90.12)

**用途:** Server State 管理 (API 資料)  
**特性:**

- ✅ 自動快取
- ✅ 背景重新請求
- ✅ 樂觀更新
- ✅ 錯誤重試

**已配置:** `app/_layout.tsx` - QueryClientProvider

**使用範例:**

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// 查詢資料
function MyCardsScreen() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['cards'],
    queryFn: () => apiClient.get('/cards/me').then((res) => res.data),
  });

  if (isLoading) return <Loading />;
  if (error) return <Error />;

  return <CardList cards={data} />;
}

// 修改資料
function UploadCard() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (cardData) => apiClient.post('/cards/upload-url', cardData),
    onSuccess: () => {
      // 重新請求卡片列表
      queryClient.invalidateQueries({ queryKey: ['cards'] });
    },
  });

  return <UploadButton onPress={() => mutation.mutate(cardData)} />;
}
```

---

## UI 與樣式 (UI & Styling)

### Gluestack UI v3（主要 UI 元件系統）

**用途:** App 全域 UI 元件系統（Button、Card、Input、Toast、Overlay 等）  
**版本:** v3.0.11  
**原則:** 專案 UI 以 Gluestack 為主，不再導入其他 UI 框架（避免多套設計系統並存造成不一致）。

**安裝/初始化（CLI）:**

```bash
# 初始化 Gluestack UI（已完成）
npx gluestack-ui@latest init

# 新增元件
npx gluestack-ui@latest add <component-name>

# 例如：
npx gluestack-ui@latest add avatar
npx gluestack-ui@latest add modal
npx gluestack-ui@latest add toast
```

**已導入元件：**
- ✅ Button (Solid, Outline 等變體)
- ✅ Card (內容容器)
- ✅ Input (表單輸入)

**Provider 配置：**
```typescript
// app/_layout.tsx
import { GluestackUIProvider } from '@/components/ui/gluestack-ui-provider';

<GluestackUIProvider mode="light">
  {/* app content */}
</GluestackUIProvider>
```

**使用範例：**
```typescript
import { Button, ButtonText } from '@/src/shared/ui/components/Button';
import { Card } from '@/src/shared/ui/components/Card';
import { Input, InputField } from '@/src/shared/ui/components/Input';

function MyScreen() {
  return (
    <Card className="p-4">
      <Input>
        <InputField placeholder="Enter text..." />
      </Input>
      <Button variant="solid">
        <ButtonText>Submit</ButtonText>
      </Button>
    </Card>
  );
}
```

**Theme Tokens:**
主題代幣定義在 `src/shared/ui/theme/tokens.ts`：
- Colors (Primary, Secondary, Tertiary, Error, Success, Warning, Info)
- Spacing (0-64 scale based on 4px)
- Typography (Font families, sizes, weights, line heights)
- Border Radius
- Opacity

**文檔：**
- [Official Docs](https://gluestack.io/ui/docs/home/overview/introduction)
- [Components](https://gluestack.io/ui/docs/components/button/introduction)

### Styling Engine：Tailwind CSS + NativeWind（Gluestack 底層樣式引擎）

**用途:** 提供 tokens/utility class 與跨平台樣式能力，供 Gluestack 元件與專案樣式使用。  
**配置檔案:** `tailwind.config.js`, `global.css`

**使用範例（搭配 utility class）:**

```tsx
import { View, Text } from 'react-native';

export default function Card() {
  return (
    <View className="bg-white p-4 rounded-lg shadow-md">
      <Text className="text-xl font-bold text-gray-800">小卡標題</Text>
      <Text className="text-sm text-gray-600 mt-2">小卡描述...</Text>
    </View>
  );
}
```

### React Native Safe Area Context (v5.6.0)

**用途:** 安全區域處理 (Notch, 底部 Bar)  
**自動整合:** Expo Router

### React Native Screens (v4.16.0)

**用途:** 原生螢幕導航優化  
**自動整合:** Expo Router

---

## API 與網路 (API & Networking)

### Axios (v1.13.2)

**用途:** HTTP 客戶端  
**特性:**

- ✅ 攔截器 (Interceptors)
- ✅ 自動 Token 注入
- ✅ 401 自動重試
- ✅ 錯誤映射

**已實作:** `src/shared/api/client.ts`

**架構:**

```typescript
// Request Interceptor - 自動加入 Token
client.interceptors.request.use(async (config) => {
  const token = await getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response Interceptor - 處理 401 並 Refresh Token
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // 嘗試刷新 Token
      await refreshToken();
      // 重試原始請求
      return client(error.config);
    }
    throw mapApiError(error);
  }
);
```

**錯誤碼映射:** `src/shared/api/errorMapper.ts`

- `400` - Bad Request
- `401` - Unauthorized (自動 Refresh)
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error (超限、檔案過大)
- `429` - Rate Limit Exceeded
- `500` - Internal Server Error
- `NETWORK_ERROR` - 網路錯誤
- `TIMEOUT_ERROR` - 請求超時

### OpenAPI Codegen（hey-api / TanStack Query SDK）

**目的：** 由後端 OpenAPI 產生型別安全的 API client + TanStack Query options/mutations。

**唯一允許的 API 呼叫方式：**
- ✅ 使用 hey-api 生成的 **TanStack Query options/mutations**（`getXxxQueryOptions()` / `useXxxMutation()`）
- ❌ **禁止**直接呼叫 SDK 函式（如 `getMyProfile()`）
- ❌ **禁止**使用舊的 `@/src/shared/api/client`（legacy，已廢除）

**策略：** 使用 repo 內的 OpenAPI snapshot（策略 B），以便在雲端 agent / CI 不依賴 `localhost` 或內網即可產出 SDK。

**重要：baseURL 設定**

後端 OpenAPI 的 endpoint paths 已包含 `/api/v1`，因此生成 client 的 `baseUrl` 應使用 host-only（例如 `http://localhost:8080`），避免 `/api/v1/api/v1`。

OpenAPI snapshot 文件：`/openapi/README.md`  
SDK 使用指南：`apps/mobile/OPENAPI_SDK_GUIDE.md`

### US2：Signed URL 上傳的錯誤處理（Non-API Request）

Signed URL 上傳的目標通常不是後端網域，因此：

- 不會有後端的統一錯誤格式（無 `code`/`message`），需用 HTTP status + 網路錯誤分類
- 不會觸發 `401 refresh`，因此 403/400 多半代表簽名不匹配或 URL 過期 → 需重新取得 Signed URL
- 建議只對「可恢復」錯誤做有限重試（網路錯誤、timeout、5xx）；對 4xx 不盲重試

---

## 導航 (Navigation)

### 路由結構

```
/                        → 根布局 (認證檢查)
├── /auth/login         → 登入頁面
└── /(tabs)             → 主要應用
    ├── /               → 首頁
    ├── /cards          → 我的卡冊
    ├── /nearby         → 附近搜尋
    └── /profile        → 個人檔案
```

### 認證流程保護

**實作位置:** `app/_layout.tsx`

```typescript
// 自動導航邏輯
useEffect(() => {
  if (isLoading) return;

  const inAuthGroup = segments[0] === 'auth';

  if (!isAuthenticated && !inAuthGroup) {
    router.replace('/auth/login'); // 未登入 → 登入頁
  } else if (isAuthenticated && inAuthGroup) {
    router.replace('/(tabs)'); // 已登入 → 主應用
  }
}, [isAuthenticated, isLoading, segments]);
```

---

## 測試 (Testing)

### Jest (v30.2.0) + jest-expo (v54.0.16)

**用途:** JavaScript 測試框架  
**配置:** `jest.config.js`

### React Native Testing Library (v13.3.3)

**用途:** React Native 元件測試  
**特性:**

- ✅ 用戶導向測試
- ✅ 查詢 API
- ✅ 事件模擬

**測試範例:**

```typescript
import { render, fireEvent } from '@testing-library/react-native';
import LoginButton from './LoginButton';

test('should call onPress when pressed', () => {
  const onPress = jest.fn();
  const { getByText } = render(<LoginButton onPress={onPress} />);

  fireEvent.press(getByText('Sign in with Google'));

  expect(onPress).toHaveBeenCalled();
});
```

**執行測試:**

```bash
npm test              # 執行所有測試
npm run test:watch    # 監視模式
npm run test:coverage # 產生覆蓋率報告
```

---

## 程式碼品質工具 (Code Quality Tools)

### ESLint (v9.39.2)

**用途:** JavaScript/TypeScript Linter  
**配置:** `.eslintrc.js`  
**規則集:**

- `expo` - Expo 推薦規則
- `prettier` - Prettier 整合
- `@typescript-eslint` - TypeScript 規則

**執行:**

```bash
npm run lint        # 檢查程式碼
npm run lint:fix    # 自動修正
```

### Prettier (v3.7.4)

**用途:** 程式碼格式化  
**配置:** `.prettierrc`  
**設定:**

```json
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "es5",
  "printWidth": 100,
  "tabWidth": 2
}
```

**執行:**

```bash
npm run format      # 格式化所有檔案
```

**自動格式化:** 每次編輯完成後執行 `npm run format`

### TypeScript (v5.9.2)

**用途:** 靜態型別檢查  
**配置:** `tsconfig.json`  
**模式:** Strict Mode 啟用

**執行:**

```bash
npm run type-check  # 型別檢查
```

---

## 開發工具鏈 (Development Toolchain)

### 環境變數

**檔案:** `.env.example` (範本)

```env
EXPO_PUBLIC_API_BASE_URL=http://localhost:8080/api/v1
EXPO_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
EXPO_PUBLIC_GOOGLE_REDIRECT_URI=kcardswap://
```

**使用:**

```typescript
import { config } from './src/shared/config';

const apiUrl = config.apiBaseUrl; // 讀取環境變數
```

### 開發指令

```bash
# 開發
npm start           # 啟動 Expo Dev Server
npm run android     # Android 開發
npm run ios         # iOS 開發 (需 macOS)
npm run web         # Web 開發

# 程式碼品質
npm run type-check  # TypeScript 檢查
npm run lint        # ESLint 檢查
npm run lint:fix    # ESLint 自動修正
npm run format      # Prettier 格式化

# 測試
npm test            # 執行測試
npm run test:watch  # 測試監視模式
npm run test:coverage # 測試覆蓋率
```

### CI/CD

**檔案:** `.github/workflows/mobile-ci.yml`

**流程:**

1. TypeScript 型別檢查
2. ESLint 檢查
3. 測試執行
4. Build 驗證

---

## 套件使用指南 (Package Usage Guide)

### User Story 對應套件

| User Story           | 套件                   | 用途               |
| -------------------- | ---------------------- | ------------------ |
| **US1: Google 登入** | expo-auth-session      | OAuth PKCE Flow    |
|                      | expo-secure-store      | Token 儲存         |
|                      | expo-crypto            | Code Verifier 生成 |
| **US2: 小卡上傳**    | expo-image-picker      | 圖片選取           |
|                      | expo-image-manipulator | 圖片壓縮           |
| **US3: 附近搜尋**    | expo-location          | 地理定位           |
| **US4: 聊天通知**    | expo-notifications     | 推播通知           |
| **US5: 交易**        | (使用現有 API Client)  | -                  |
| **US6: 訂閱**        | expo-application       | App 版本資訊       |

### 套件安裝指南

**已安裝的套件:** 所有 Phase 1M 及 User Stories 所需套件已安裝完成

**新增套件:**

```bash
# 使用 npm (推薦)
npm install package-name --legacy-peer-deps

# 或使用 expo install (自動匹配版本)
npx expo install package-name
```

---

## 最佳實踐 (Best Practices)

### 1. 程式碼格式化

**每次編輯後執行:**

```bash
npm run format
```

### 2. 型別安全

- ✅ 使用 TypeScript 型別
- ✅ 避免 `any`
- ✅ 定義 Interface/Type

### 3. 狀態管理

- ✅ Zustand - 全域狀態 (Auth, User)
- ✅ TanStack Query - API 資料
- ✅ Local State - 元件內狀態

### 4. API 呼叫

- ✅ 使用 `src/shared/api/client.ts`
- ✅ TanStack Query 管理快取
- ✅ 錯誤處理統一映射

### 5. 安全性

- ✅ Token 使用 expo-secure-store
- ✅ 環境變數不提交
- ✅ API 請求 HTTPS
- ✅ 敏感資料加密

---

## 疑難排解 (Troubleshooting)

### 常見問題

**1. Metro Bundler Cache 問題**

```bash
npx expo start --clear
```

**2. 依賴安裝失敗**

```bash
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

**3. TypeScript 錯誤**

```bash
npm run type-check
```

**4. iOS Build 問題 (macOS)**

```bash
cd ios && pod install && cd ..
```

---

## 參考資源 (Resources)

### 官方文檔

- [Expo Documentation](https://docs.expo.dev/)
- [React Native Documentation](https://reactnative.dev/)
- [TanStack Query](https://tanstack.com/query/latest)
- [Zustand](https://github.com/pmndrs/zustand)
- [Gluestack UI](https://gluestack.io/ui/docs)

### 專案文檔

- [README.md](./README.md) - 專案說明
- [dev-setup.md](../../dev-setup.md) - 開發環境設定
- [PHASE-1M-COMPLETE.md](../../PHASE-1M-COMPLETE.md) - Phase 1M 完成報告

---

**文件維護:** 請在新增套件或技術變更時更新此文件
