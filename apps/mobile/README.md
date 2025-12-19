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
- **API Client**: Axios with interceptors
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
```

### Environment Setup

1. Copy the environment template:

```bash
cp .env.example .env
```

2. Update the variables in `.env`:

```
EXPO_PUBLIC_API_BASE_URL=http://localhost:8080/api/v1
EXPO_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
```

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
│   ├── _layout.tsx          # Root layout with providers
│   ├── auth/                # Auth screens (login, etc.)
│   └── (tabs)/              # Main app with tab navigation
├── src/
│   ├── shared/              # Shared utilities
│   │   ├── api/            # API client and error handling
│   │   ├── auth/           # Token storage and session management
│   │   ├── state/          # Zustand stores
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
- [x] Gluestack UI setup (with Tailwind/NativeWind styling engine)
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
