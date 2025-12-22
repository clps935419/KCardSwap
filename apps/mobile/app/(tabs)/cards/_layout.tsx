/**
 * Cards Stack Navigator
 * Phase 4 (US2) - Stack navigation for cards tab
 * 
 * Stack screens:
 * - index: MyCardsScreen (M204) - List of user's cards
 * - upload: UploadCardScreen (M201-M203) - Upload new card
 */
import { Stack } from 'expo-router';

export default function CardsLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: true,
        headerStyle: {
          backgroundColor: '#3B82F6',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}
    >
      <Stack.Screen
        name="index"
        options={{
          title: '我的卡冊',
          headerShown: false, // Tab has its own header
        }}
      />
      <Stack.Screen
        name="upload"
        options={{
          title: '上傳小卡',
          presentation: 'modal',
        }}
      />
    </Stack>
  );
}
