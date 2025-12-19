import { View, Text, ScrollView } from 'react-native';
import { useAuthStore } from '../../src/shared/state/authStore';
import { Button, ButtonText } from '../../src/shared/ui/components/Button';
import { Card } from '../../src/shared/ui/components/Card';
import { Input, InputField } from '../../src/shared/ui/components/Input';

export default function HomeScreen() {
  const { user } = useAuthStore();

  return (
    <ScrollView className="flex-1 bg-white">
      <View className="p-4">
        <Text className="text-2xl font-bold mb-4 text-gray-800">Welcome to KCardSwap!</Text>
        {user && (
          <Text className="text-base text-gray-600 mb-4">
            Hello, {user.nickname || user.email}
          </Text>
        )}

        {/* Gluestack UI Components Demo */}
        <Card className="p-4 mb-4">
          <Text className="text-lg font-semibold mb-2">Gluestack UI Integration ✅</Text>
          <Text className="text-sm text-gray-600 mb-4">
            Phase 1M Mobile Setup Complete with Gluestack UI components.
          </Text>

          {/* Button Examples */}
          <View className="mb-4">
            <Text className="text-sm font-medium mb-2">Buttons:</Text>
            <View className="flex-row gap-2 mb-2">
              <Button variant="solid" size="md">
                <ButtonText>Solid Button</ButtonText>
              </Button>
              <Button variant="outline" size="md">
                <ButtonText>Outline</ButtonText>
              </Button>
            </View>
          </View>

          {/* Input Example */}
          <View className="mb-4">
            <Text className="text-sm font-medium mb-2">Input:</Text>
            <Input>
              <InputField placeholder="Enter your text here..." />
            </Input>
          </View>
        </Card>

        {/* Feature Roadmap Card */}
        <Card className="p-4">
          <Text className="text-lg font-semibold mb-2">Feature Roadmap</Text>
          <Text className="text-sm text-gray-600">
            Features to be implemented in User Story phases:{'\n\n'}
            • US1: Google Login & Profile{'\n'}
            • US2: Card Upload{'\n'}
            • US3: Nearby Search{'\n'}
            • US4: Friends & Chat{'\n'}
            • US5: Trading{'\n'}
            • US6: Subscription
          </Text>
        </Card>
      </View>
    </ScrollView>
  );
}
