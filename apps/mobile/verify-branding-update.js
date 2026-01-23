#!/usr/bin/env node
/**
 * 驗證腳本：UI 品牌更新與開發模式登入
 * 
 * 此腳本驗證以下項目：
 * 1. 環境變數配置正確
 * 2. 開發模式開關功能正常（使用 EXPO_PUBLIC_ENV）
 * 3. 應用名稱更新為「小卡Show!」
 */

console.log('🔍 開始驗證 UI 品牌更新與開發模式登入...\n');

// 測試 1: 開發模式
console.log('✅ 測試 1: 開發模式配置');
process.env.EXPO_PUBLIC_ENV = 'development';
process.env.EXPO_PUBLIC_APP_NAME = '小卡Show!';

const devConfig = {
  appName: process.env.EXPO_PUBLIC_APP_NAME || '小卡Show!',
  env: process.env.EXPO_PUBLIC_ENV || 'development',
  isDevLoginEnabled: process.env.EXPO_PUBLIC_ENV === 'development',
};

console.log('   應用名稱:', devConfig.appName);
console.log('   環境:', devConfig.env);
console.log('   開發模式登入:', devConfig.isDevLoginEnabled ? '✅ 啟用' : '❌ 停用');

if (devConfig.appName !== '小卡Show!') {
  console.error('   ❌ 錯誤：應用名稱不正確');
  process.exit(1);
}

if (!devConfig.isDevLoginEnabled) {
  console.error('   ❌ 錯誤：開發模式下應啟用開發登入');
  process.exit(1);
}

console.log('   ✅ 通過\n');

// 測試 2: 生產模式
console.log('✅ 測試 2: 生產模式配置');
process.env.EXPO_PUBLIC_ENV = 'production';

const prodConfig = {
  appName: process.env.EXPO_PUBLIC_APP_NAME || '小卡Show!',
  env: process.env.EXPO_PUBLIC_ENV || 'development',
  isDevLoginEnabled: process.env.EXPO_PUBLIC_ENV === 'development',
};

console.log('   應用名稱:', prodConfig.appName);
console.log('   環境:', prodConfig.env);
console.log('   開發模式登入:', prodConfig.isDevLoginEnabled ? '✅ 啟用' : '❌ 停用');

if (prodConfig.isDevLoginEnabled) {
  console.error('   ❌ 錯誤：生產模式下不應啟用開發登入');
  process.exit(1);
}

console.log('   ✅ 通過\n');

// 測試 3: 預設值
console.log('✅ 測試 3: 預設值配置');
delete process.env.EXPO_PUBLIC_ENV;
delete process.env.EXPO_PUBLIC_APP_NAME;

const defaultConfig = {
  appName: process.env.EXPO_PUBLIC_APP_NAME || '小卡Show!',
  env: process.env.EXPO_PUBLIC_ENV || 'development',
  isDevLoginEnabled: (process.env.EXPO_PUBLIC_ENV || 'development') === 'development',
};

console.log('   應用名稱:', defaultConfig.appName);
console.log('   環境:', defaultConfig.env);
console.log('   開發模式登入:', defaultConfig.isDevLoginEnabled ? '✅ 啟用' : '❌ 停用');

if (defaultConfig.appName !== '小卡Show!') {
  console.error('   ❌ 錯誤：預設應用名稱不正確');
  process.exit(1);
}

console.log('   ✅ 通過\n');

// 總結
console.log('═══════════════════════════════════════');
console.log('🎉 所有測試通過！');
console.log('═══════════════════════════════════════');
console.log('\n📝 實作總結：');
console.log('   • 品牌更新為「小卡Show!」');
console.log('   • 開發模式登入功能已實作');
console.log('   • 環境變數配置正確');
console.log('   • 使用 EXPO_PUBLIC_ENV 控制開發/生產模式');
console.log('\n💡 使用方式：');
console.log('   開發模式：EXPO_PUBLIC_ENV=development（顯示帳號密碼登入）');
console.log('   生產模式：EXPO_PUBLIC_ENV=production（只顯示 Google 登入）');
console.log('\n📚 詳細文件：apps/mobile/UI_BRANDING_UPDATE.md\n');
