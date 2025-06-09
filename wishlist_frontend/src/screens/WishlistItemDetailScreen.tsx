import React from 'react';
import { StyleSheet, View, ScrollView, Image } from 'react-native';
import { Appbar, Text, Card, Button, Portal, Modal, TextInput } from 'react-native-paper';
import { theme } from '../utils/theme';
import { useRTL, createRTLStyles } from '../context/RightToLeftContext';

export const WishlistItemDetailScreen = ({ route, navigation }) => {
  const [showContributeModal, setShowContributeModal] = React.useState(false);
  const [contributionAmount, setContributionAmount] = React.useState('');

  // In a real app, fetch this data from API
  const item = {
    id: '1',
    title: 'نوت بوک لنوو',
    description: 'لپ تاپ لنوو مدل ThinkPad X1 Carbon با پردازنده نسل 12 اینتل',
    imageUrl: 'https://example.com/laptop.jpg',
    price: 45000000,
    contributedAmount: 15000000,
    contributors: [
      { name: 'علی', amount: 5000000 },
      { name: 'مریم', amount: 10000000 },
    ],
  };

  const handleContribute = () => {
    // Handle contribution logic
    setShowContributeModal(false);
  };

  return (
    <View style={styles.container}>
      <Appbar.Header style={styles.header}>
        <Appbar.BackAction onPress={() => navigation.goBack()} color={theme.colors.white} />
        <Appbar.Content title={item.title} color={theme.colors.white} />
        <Appbar.Action icon="share" onPress={() => {}} color={theme.colors.white} />
      </Appbar.Header>

      <ScrollView>
        <Card style={styles.card}>
          <Card.Cover source={{ uri: item.imageUrl }} style={styles.image} />
          <Card.Content>
            <Text style={styles.title}>{item.title}</Text>
            <Text style={styles.description}>{item.description}</Text>
            <View style={styles.priceContainer}>
              <Text style={styles.priceLabel}>قیمت:</Text>
              <Text style={styles.price}>{item.price.toLocaleString()} تومان</Text>
            </View>
            <View style={styles.progressContainer}>
              <Text style={styles.contributedLabel}>جمع‌آوری شده:</Text>
              <Text style={styles.contributedAmount}>
                {item.contributedAmount.toLocaleString()} تومان
              </Text>
              <View style={styles.progressBar}>
                <View 
                  style={[
                    styles.progress, 
                    { width: `${(item.contributedAmount / item.price) * 100}%` }
                  ]} 
                />
              </View>
            </View>

            <View style={styles.contributorsContainer}>
              <Text style={styles.contributorsTitle}>مشارکت‌کنندگان:</Text>
              {item.contributors.map((contributor, index) => (
                <View key={index} style={styles.contributorItem}>
                  <Text style={styles.contributorName}>{contributor.name}</Text>
                  <Text style={styles.contributorAmount}>
                    {contributor.amount.toLocaleString()} تومان
                  </Text>
                </View>
              ))}
            </View>
          </Card.Content>
        </Card>
      </ScrollView>

      <View style={styles.bottomBar}>
        <Button
          mode="contained"
          onPress={() => setShowContributeModal(true)}
          style={styles.contributeButton}
        >
          مشارکت در خرید
        </Button>
      </View>

      <Portal>
        <Modal
          visible={showContributeModal}
          onDismiss={() => setShowContributeModal(false)}
          contentContainerStyle={styles.modal}
        >
          <Text style={styles.modalTitle}>مبلغ مشارکت</Text>
          <TextInput
            keyboardType="numeric"
            value={contributionAmount}
            onChangeText={setContributionAmount}
            style={styles.input}
            placeholder="مبلغ به تومان"
          />
          <Button
            mode="contained"
            onPress={handleContribute}
            style={styles.modalButton}
          >
            پرداخت
          </Button>
        </Modal>
      </Portal>
    </View>
  );
};

const styles = createRTLStyles({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    backgroundColor: theme.colors.primary,
  },
  card: {
    margin: theme.spacing.md,
    elevation: 2,
  },
  image: {
    height: 300,
  },
  title: {
    ...theme.typography.h2,
    color: theme.colors.text,
    marginVertical: theme.spacing.md,
  },
  description: {
    ...theme.typography.body,
    color: theme.colors.onSurface,
    marginBottom: theme.spacing.lg,
  },
  priceContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: theme.spacing.md,
  },
  priceLabel: {
    ...theme.typography.body,
    color: theme.colors.text,
  },
  price: {
    ...theme.typography.h3,
    color: theme.colors.primary,
  },
  progressContainer: {
    marginBottom: theme.spacing.lg,
  },
  contributedLabel: {
    ...theme.typography.body,
    color: theme.colors.text,
    marginBottom: theme.spacing.xs,
  },
  contributedAmount: {
    ...theme.typography.h3,
    color: theme.colors.accent,
    marginBottom: theme.spacing.sm,
  },
  progressBar: {
    height: 8,
    backgroundColor: theme.colors.secondary,
    borderRadius: 4,
  },
  progress: {
    height: '100%',
    backgroundColor: theme.colors.primary,
    borderRadius: 4,
  },
  contributorsContainer: {
    marginTop: theme.spacing.lg,
  },
  contributorsTitle: {
    ...theme.typography.h3,
    color: theme.colors.text,
    marginBottom: theme.spacing.md,
  },
  contributorItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: theme.spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.secondary,
  },
  contributorName: {
    ...theme.typography.body,
    color: theme.colors.text,
  },
  contributorAmount: {
    ...theme.typography.body,
    color: theme.colors.primary,
  },
  bottomBar: {
    padding: theme.spacing.md,
    backgroundColor: theme.colors.surface,
    elevation: 4,
  },
  contributeButton: {
    backgroundColor: theme.colors.accent,
  },
  modal: {
    backgroundColor: theme.colors.surface,
    padding: theme.spacing.lg,
    margin: theme.spacing.lg,
    borderRadius: theme.roundness,
  },
  modalTitle: {
    ...theme.typography.h2,
    color: theme.colors.text,
    marginBottom: theme.spacing.lg,
    textAlign: 'center',
  },
  input: {
    marginBottom: theme.spacing.lg,
  },
  modalButton: {
    marginTop: theme.spacing.md,
  },
});
