import React from 'react';
import { Text as RNText, TextProps, StyleSheet } from 'react-native';
import { useRTL, createRTLStyles } from '../../context/RightToLeftContext';
import { theme } from '../../utils/theme';

interface RTLTextProps extends TextProps {
  variant?: 'h1' | 'h2' | 'h3' | 'body' | 'small';
  color?: string;
}

export const Text: React.FC<RTLTextProps> = ({
  children,
  variant = 'body',
  color = theme.colors.text,
  style,
  ...props
}) => {
  const { isRTL } = useRTL();

  const variantStyles = {
    h1: styles.h1,
    h2: styles.h2,
    h3: styles.h3,
    body: styles.body,
    small: styles.small,
  };

  return (
    <RNText
      style={[
        styles.text,
        variantStyles[variant],
        { color, textAlign: isRTL ? 'right' : 'left' },
        style,
      ]}
      {...props}
    >
      {children}
    </RNText>
  );
};

const styles = createRTLStyles({
  text: {
    fontFamily: theme.fonts.regular.fontFamily,
  },
  h1: {
    fontSize: 32,
    fontFamily: theme.fonts.bold.fontFamily,
    marginBottom: theme.spacing.sm,
  },
  h2: {
    fontSize: 24,
    fontFamily: theme.fonts.bold.fontFamily,
    marginBottom: theme.spacing.sm,
  },
  h3: {
    fontSize: 20,
    fontFamily: theme.fonts.medium.fontFamily,
    marginBottom: theme.spacing.xs,
  },
  body: {
    fontSize: 16,
    lineHeight: 24,
  },
  small: {
    fontSize: 14,
    lineHeight: 20,
  },
});
