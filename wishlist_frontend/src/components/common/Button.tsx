import React from 'react';
import { StyleSheet } from 'react-native';
import { Button as PaperButton } from 'react-native-paper';
import { theme } from '../../utils/theme';
import { useRTL, createRTLStyles } from '../../context/RightToLeftContext';

interface ButtonProps {
  mode?: 'contained' | 'outlined' | 'text';
  onPress: () => void;
  children: React.ReactNode;
  loading?: boolean;
  disabled?: boolean;
  color?: string;
  style?: any;
}

export const Button = ({
  mode = 'contained',
  onPress,
  children,
  loading = false,
  disabled = false,
  color,
  style,
}: ButtonProps) => {
  return (
    <PaperButton
      mode={mode}
      onPress={onPress}
      loading={loading}
      disabled={disabled}
      color={color || theme.colors.primary}
      style={[styles.button, style]}
      labelStyle={styles.label}
    >
      {children}
    </PaperButton>
  );
};

const styles = StyleSheet.create({
  button: {
    borderRadius: theme.roundness,
    paddingHorizontal: theme.spacing.md,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
  },
});
