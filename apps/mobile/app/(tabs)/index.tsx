import { ScrollView } from 'react-native';
import { useAuthStore } from '@/src/shared/state/authStore';
import {
  Box,
  Text,
  Heading,
  Button,
  ButtonText,
  Card,
  Input,
  InputField,
} from '@/src/shared/ui/components';

export default function HomeScreen() {
  const { user } = useAuthStore();

  return (
    <ScrollView className="flex-1 bg-white">
      <Box className="p-4">
        <Heading size="2xl" className="mb-4 text-gray-800">
          Welcome to KCardSwap!
        </Heading>
        {user && (
          <Text size="md" className="text-gray-600 mb-4">
            Hello, {user.nickname || user.email}
          </Text>
        )}

        {/* Gluestack UI Components Demo */}
        <Card className="p-4 mb-4">
          <Heading size="lg" className="mb-2">
            Gluestack UI Integration ✅
          </Heading>
          <Text size="sm" className="text-gray-600 mb-4">
            Phase 1M Mobile Setup Complete with Gluestack UI components.
          </Text>

          {/* Button Examples */}
          <Box className="mb-4">
            <Text size="sm" className="font-medium mb-2">
              Buttons:
            </Text>
            <Box className="flex-row gap-2 mb-2">
              <Button variant="solid" size="md">
                <ButtonText>Solid Button</ButtonText>
              </Button>
              <Button variant="outline" size="md">
                <ButtonText>Outline</ButtonText>
              </Button>
            </Box>
          </Box>

          {/* Input Example */}
          <Box className="mb-4">
            <Text size="sm" className="font-medium mb-2">
              Input:
            </Text>
            <Input>
              <InputField placeholder="Enter your text here..." />
            </Input>
          </Box>
        </Card>

        {/* Feature Roadmap Card */}
        <Card className="p-4">
          <Heading size="lg" className="mb-2">
            Feature Roadmap
          </Heading>
          <Text size="sm" className="text-gray-600">
            Features to be implemented in User Story phases:{'\n\n'}
            • US1: Google Login & Profile{'\n'}
            • US2: Card Upload{'\n'}
            • US3: Nearby Search{'\n'}
            • US4: Friends & Chat{'\n'}
            • US5: Trading{'\n'}
            • US6: Subscription
          </Text>
        </Card>
      </Box>
    </ScrollView>
  );
}
