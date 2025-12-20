# KCardSwap Mobile App

React Native mobile application for KCardSwap, built with Expo SDK 54.

## Tech Stack

**完整技術文件請見 [TECH_STACK.md](./TECH_STACK.md)**

- **Framework**: Expo SDK 54 (React Native 0.81)
- **Language**: TypeScript
- **Navigation**: Expo Router (file-based routing)
- **UI Framework**: Gluestack UI (primary UI component system)
- **Styling Engine**: Tailwind CSS + NativeWind (used by Gluestack)
- **State Management**:
  - Zustand (global state, auth)
  - TanStack Query (server state, API calls)
- **API Client**: hey-api/openapi-ts 生成 SDK（Axios client + TanStack Query options/mutations）
  - **唯一 API 呼叫方式**：使用 TanStack Query options/mutations（禁止直接呼叫 SDK 函式或舊 client）
  - **例外**：Signed URL 上傳必須使用獨立 `fetch()`
- **Storage**: expo-secure-store (secure token storage)
- **Testing**: Jest + React Native Testing Library
- **Code Quality**: ESLint + Prettier

### Expo Packages Installed

**Authentication & Security:**

- expo-auth-session (Google OAuth PKCE)
- expo-secure-store (Encrypted token storage)
- expo-crypto (Cryptographic functions)

**Image & Media:**

- expo-image-picker (Image selection)
- expo-image-manipulator (Image compression)

**UI Components:**

- gluestack-ui (UI component system; initialized via `npx gluestack-ui init`)
  - Provider configured in `app/_layout.tsx`
  - Components: Button, Card, Input (with more available via CLI)
  - Theme tokens in `src/shared/ui/theme/tokens.ts`

**Location:**

- expo-location (Geolocation)

**Notifications:**

- expo-notifications (Push notifications)

**Device Info:**

- expo-device (Device information)
- expo-application (App metadata)

## Getting Started

### Prerequisites

- Node.js 20+ and npm
- Expo CLI (installed automatically with npx)
- For iOS: macOS with Xcode
- For Android: Android Studio with emulator or physical device

### Installation

```bash
cd apps/mobile
npm install --legacy-peer-deps

# Initialize Gluestack UI (already done, only needed once)
# npx gluestack-ui init
```

### Gluestack UI Setup

The project uses Gluestack UI v3 as the primary UI component system. The setup includes:

1. **Provider Configuration**: `GluestackUIProvider` is configured in `app/_layout.tsx`
2. **Components**: Available in `components/ui/` directory
   - `button` - Button components with variants (solid, outline, etc.)
   - `card` - Card component for content containers
   - `input` - Input components for forms
3. **Theme Tokens**: Centralized in `src/shared/ui/theme/tokens.ts`
4. **Shared Components**: Re-exported in `src/shared/ui/components/` for easy imports

**Adding More Components:**

```bash
# Add a specific component
npx gluestack-ui@latest add <component-name>

# Examples:
npx gluestack-ui@latest add avatar
npx gluestack-ui@latest add modal
npx gluestack-ui@latest add toast
```

### Environment Setup

1. Copy the environment template:

```bash
cp .env.example .env
```

2. Update the variables in `.env`:

```
EXPO_PUBLIC_API_BASE_URL=http://localhost:8080
# OpenAPI paths 已包含 /api/v1；baseUrl 請維持 host-only。
#（若不小心填成 http://localhost:8080/api/v1，SDK 會自動移除 /api/v1）
EXPO_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
```

## OpenAPI SDK 產生（hey-api / Axios client）

本專案規劃使用 hey-api 由 OpenAPI 產生：

- TypeScript API client（Axios runtime）
- TanStack Query 相關的 query/mutation options（可搭配 React Native / Expo 使用）

### 為什麼要用本地 snapshot

雲端 agent 或 CI 在沒有可達的 `localhost`/內網環境時，仍能穩定產出 SDK；因此 OpenAPI 以「repo 內快照檔」作為 codegen 輸入來源。

### OpenAPI 來源

- Repo snapshot：`openapi/openapi.json`（由後端程式碼直接生成）

OpenAPI snapshot 生成/更新請見：`/openapi/README.md`

### 重要：baseURL 規則（避免 /api/v1/api/v1）

目前後端 OpenAPI 的 endpoint paths 已包含 `/api/v1`（例如 `/api/v1/cards/me`）。

- ✅ hey-api 生成 client 的 `baseUrl` 建議設定為「host-only」：`http://localhost:8080`
- ❌ 不要把 `/api/v1` 再放進 `baseUrl`，否則會造成 `/api/v1/api/v1/...`

這也意味著：當你從現有 `src/shared/api/client.ts`（legacy axios client）切換到 hey-api 生成 client 時，`.env` 的 `EXPO_PUBLIC_API_BASE_URL` 需要跟著調整。

### Signed URL Upload 仍是例外

Signed URL 上傳的目標通常不是後端網域，因此：

- **取得 Signed URL**（`POST /cards/upload-url`）走 hey-api SDK 的 TanStack Query mutation
- **上傳到 Signed URL**（PUT/POST 到 `upload_url`）必須使用獨立 `fetch()`
  - 不可使用 SDK（避免自動注入 Authorization header）
  - 必須完全依照後端回傳的 `method` 與 `required_headers`
  - 詳見 `apps/mobile/TECH_STACK.md` 的錯誤處理分流規則

### 雲端 agent / CI 的獨立 tasks（文件版）

1. 更新 OpenAPI snapshot（repo 內檔案）
2. 在 `apps/mobile` 安裝 hey-api 相關依賴（含 Axios client + TanStack Query plugin）
3. 以 snapshot 作為 input 產生 SDK（生成輸出可 commit，但視為 dependency：禁止手改；修改 OpenAPI 後必須 regenerate）
4. 驗證：`npm run type-check`、相關單元測試（如有）


### Running the App

```bash
# Start the development server
npm start

# Run on Android
npm run android

# Run on iOS (macOS only)
npm run ios

# Run on web
npm run web
```

## Project Structure

```
apps/mobile/
├── app/                      # Expo Router app directory (routes)
│   ├── _layout.tsx          # Root layout with providers (Gluestack + TanStack Query)
│   ├── auth/                # Auth screens (login, etc.)
│   └── (tabs)/              # Main app with tab navigation
├── components/               # Gluestack UI components
│   └── ui/                  # UI components added via CLI
│       ├── button/          # Button component
│       ├── card/            # Card component
│       ├── input/           # Input component
│       └── gluestack-ui-provider/ # Provider configuration
├── src/
│   ├── shared/              # Shared utilities
│   │   ├── api/            # API client and error handling
│   │   ├── auth/           # Token storage and session management
│   │   ├── state/          # Zustand stores
│   │   ├── ui/             # UI components and theme
│   │   │   ├── components/ # Shared UI component exports (Button, Card, Input)
│   │   │   └── theme/      # Theme tokens (colors, spacing, typography)
│   │   └── config.ts       # App configuration
│   └── features/            # Feature modules (to be implemented)
│       ├── auth/
│       ├── profile/
│       ├── cards/
│       ├── nearby/
│       ├── friends/
│       ├── chat/
│       ├── trade/
│       └── subscription/
├── __tests__/               # Test files
└── assets/                  # Images, fonts, etc.
```

## Development

### Available Scripts

```bash
npm start               # Start Expo development server
npm test                # Run tests once
npm run test:watch      # Run tests in watch mode
npm run test:coverage   # Run tests with coverage
npm run lint            # Run ESLint
npm run lint:fix        # Fix ESLint errors
npm run format          # Format code with Prettier
npm run format:check    # Check if code is formatted
npm run type-check      # Run TypeScript type checking
npm run validate        # Run all checks (type-check + lint + format)
npm run precommit       # Format, fix linting, and type-check (run before commit)
```

### Code Style & Formatting

This project uses:

- **ESLint** for code linting
- **Prettier** for code formatting
- **TypeScript** strict mode

**推薦工作流程 (Recommended Workflow):**

1. 編輯程式碼後執行格式化:

   ```bash
   npm run format
   ```

2. 提交前執行完整檢查:

   ```bash
   npm run precommit
   ```

3. 或手動執行所有檢查:
   ```bash
   npm run validate
   ```

**自動格式化設定:**
大多數編輯器支援儲存時自動格式化，請參考 [TECH_STACK.md](./TECH_STACK.md) 的設定說明。

### Testing

Tests are written with Jest and React Native Testing Library.

```bash
# Run all tests
npm test

# Watch mode
npm run test:watch

# With coverage
npm run test:coverage
```

## Features Implementation Status

### Phase 1M: Mobile Setup ✅ (Complete)

- [x] Expo SDK 54 setup with TypeScript
- [x] Expo Router navigation structure
- [x] **Gluestack UI v3 setup** (with Tailwind/NativeWind styling engine)
  - [x] Provider configured in app/_layout.tsx
  - [x] Button, Card, Input components added
  - [x] Theme tokens in src/shared/ui/theme/
  - [x] Snapshot tests for components
- [x] API client with Axios (baseURL, timeout, error handling)
- [x] Token storage with expo-secure-store
- [x] Zustand auth store (login/logout/refresh)
- [x] TanStack Query setup
- [x] Error mapping for backend codes
- [x] Environment variables configuration
- [x] Testing infrastructure (Jest + RNTL)
- [x] ESLint and Prettier
- [x] Mobile CI workflow

### Phase 3: US1 - Google Login & Profile (To be implemented)

- [ ] Google OAuth with PKCE flow
- [ ] Profile view and edit screens
- [ ] Token refresh mechanism
- [ ] Avatar upload

### Phase 4: US2 - Card Upload (To be implemented)

- [ ] Image picker integration
- [ ] Upload to signed URL
- [ ] My cards list
- [ ] Delete card

### Phase 5: US3 - Nearby Search (To be implemented)

- [ ] Location permissions
- [ ] Nearby search screen
- [ ] Map integration

### Phase 6: US4 - Friends & Chat (To be implemented)

- [ ] Friend requests
- [ ] Chat UI
- [ ] Push notifications

### Phase 7: US5 - Trade (To be implemented)

- [ ] Trade proposal
- [ ] Trade status tracking
- [ ] Trade history

### Phase 8: US6 - Subscription (To be implemented)

- [ ] Google Play Billing integration
- [ ] Subscription status
- [ ] Paywall UI

## API Integration

The app connects to the backend API at `EXPO_PUBLIC_API_BASE_URL`.

### Authentication Flow

1. User logs in via Google OAuth (PKCE flow)
2. Backend returns access token + refresh token
3. Tokens stored securely in expo-secure-store
4. API client automatically adds tokens to requests
5. Automatic token refresh on 401 errors
6. Redirect to login if refresh fails

### Error Handling

Backend error codes are mapped to user-friendly messages in `src/shared/api/errorMapper.ts`.

## Deployment

### EAS Build (Future)

```bash
# Install EAS CLI
npm install -g eas-cli

# Configure EAS
eas build:configure

# Build for Android
eas build --platform android

# Build for iOS
eas build --platform ios
```

## Troubleshooting

### Common Issues

1. **Module not found errors**: Run `npm install --legacy-peer-deps`
2. **Metro bundler cache**: Run `npx expo start -c`
3. **TypeScript errors**: Run `npm run type-check`
4. **iOS build issues**: Clear derived data in Xcode

### Logs

```bash
# View logs
npx expo logs

# Clear cache
npx expo start --clear
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

[Add license information]
