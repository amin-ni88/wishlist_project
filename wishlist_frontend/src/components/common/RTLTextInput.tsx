import React from 'react';
import { StyleSheet, TextInput as RNTextInput, TextInputProps } from 'react-native';
import { TextInput as PaperTextInput } from 'react-native-paper';
import { theme } from '../../utils/theme';
import { useRTL, createRTLStyles } from '../../context/RightToLeftContext';

interface RTLTextInputProps extends TextInputProps {
  label?: string;
  error?: string;
  mode?: 'flat' | 'outlined';
}

export const RTLTextInput: React.FC<RTLTextInputProps> = ({
  label,
  error,
  mode = 'outlined',
  style,
  ...props
}) => {
  const { isRTL } = useRTL();

  return (
    <PaperTextInput
      label={label}
      mode={mode}
      error={!!error}
      style={[
        styles.input,
        {
          textAlign: isRTL ? 'right' : 'left',
        },
        style,
      ]}
      right={error ? <PaperTextInput.Icon name="alert-circle" color={theme.colors.error} /> : undefined}
      {...props}
    />
  );
};

const styles = createRTLStyles({
  input: {
    backgroundColor: theme.colors.surface,
    marginBottom: theme.spacing.sm,
  },
  error: {
    color: theme.colors.error,
    fontSize: 12,
    marginTop: -theme.spacing.xs,
    marginBottom: theme.spacing.sm,
  },
});
