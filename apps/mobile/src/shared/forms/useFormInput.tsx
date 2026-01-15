/**
 * React Hook Form Integration for Gluestack UI
 * 
 * 提供與 Gluestack UI 整合的表單輸入 hook
 */

import { Controller, type Control, type FieldPath, type FieldValues } from 'react-hook-form';
import { Input, InputField } from '@/src/shared/ui/components';

interface UseFormInputProps<TFieldValues extends FieldValues = FieldValues> {
  control: Control<TFieldValues>;
  name: FieldPath<TFieldValues>;
  placeholder?: string;
  disabled?: boolean;
  multiline?: boolean;
  numberOfLines?: number;
  maxLength?: number;
  secureTextEntry?: boolean;
}

/**
 * Hook for rendering form input with React Hook Form + Gluestack UI
 * 
 * Usage:
 * ```tsx
 * const { control } = useForm();
 * const FormInput = useFormInput({ control, name: 'email', placeholder: 'Email' });
 * return <FormInput />;
 * ```
 */
export function useFormInput<TFieldValues extends FieldValues = FieldValues>({
  control,
  name,
  placeholder,
  disabled,
  multiline,
  numberOfLines,
  maxLength,
  secureTextEntry,
}: UseFormInputProps<TFieldValues>) {
  return () => (
    <Controller
      control={control}
      name={name}
      render={({ field: { onChange, onBlur, value } }) => (
        <Input disabled={disabled}>
          <InputField
            value={value as string}
            onChangeText={onChange}
            onBlur={onBlur}
            placeholder={placeholder}
            multiline={multiline}
            numberOfLines={numberOfLines}
            maxLength={maxLength}
            secureTextEntry={secureTextEntry}
            textAlignVertical={multiline ? 'top' : 'center'}
          />
        </Input>
      )}
    />
  );
}
