import React from 'react';
import { StyleSheet, View, Image } from 'react-native';
import { Card, Title, Paragraph, ProgressBar } from 'react-native-paper';
import { theme } from '../../utils/theme';
import { useRTL, createRTLStyles } from '../../context/RightToLeftContext';
import { useRTL, createRTLStyles } from '../../context/RightToLeftContext';

interface WishlistItemCardProps {
  title: string;
  description: string;
  imageUrl?: string;
  price: number;
  contributedAmount: number;
  onPress: () => void;
}

export const WishlistItemCard = ({
  title,
  description,
  imageUrl,
  price,
  contributedAmount,
  onPress,
}: WishlistItemCardProps) => {
  const progress = contributedAmount / price;

  return (
    <Card style={styles.card} onPress={onPress}>
      {imageUrl && (
        <Card.Cover
          source={{ uri: imageUrl }}
          style={styles.image}
        />
      )}
      <Card.Content>
        <Title style={styles.title}>{title}</Title>
        <Paragraph numberOfLines={2} style={styles.description}>
          {description}
        </Paragraph>
        <View style={styles.progressContainer}>
          <ProgressBar
            progress={progress}
            color={theme.colors.primary}
            style={styles.progressBar}
          />
          <Paragraph style={styles.amount}>
            {`${contributedAmount} / ${price} تومان`}
          </Paragraph>
        </View>
      </Card.Content>
    </Card>
  );
};

import { useRTL, createRTLStyles } from '../../context/RightToLeftContext';

const styles = createRTLStyles({
  card: {
    marginVertical: theme.spacing.sm,
    marginHorizontal: theme.spacing.md,
    borderRadius: theme.roundness,
    backgroundColor: theme.colors.surface,
    elevation: 2,
  },
  image: {
    height: 200,
    borderTopLeftRadius: theme.roundness,
    borderTopRightRadius: theme.roundness,
  },
  title: {
    color: theme.colors.text,
    marginTop: theme.spacing.sm,
    fontWeight: 'bold',
  },
  description: {
    color: theme.colors.onSurface,
    marginTop: theme.spacing.xs,
  },
  progressContainer: {
    marginTop: theme.spacing.md,
  },
  progressBar: {
    height: 8,
    borderRadius: 4,
  },
  amount: {
    marginTop: theme.spacing.xs,
    color: theme.colors.primary,
    textAlign: 'right',
  },
});
