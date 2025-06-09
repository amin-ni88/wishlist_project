import React from 'react';
import { StyleSheet, View, FlatList } from 'react-native';
import { Appbar, FAB } from 'react-native-paper';
import { WishlistItemCard } from '../components/common/WishlistItemCard';
import { theme } from '../utils/theme';
import { useNavigation } from '@react-navigation/native';

export const HomeScreen = () => {
  const navigation = useNavigation();

  const [wishlistItems, setWishlistItems] = React.useState([
    // Example data
    {
      id: '1',
      title: 'نوت بوک لنوو',
      description: 'لپ تاپ لنوو مدل ThinkPad X1 Carbon',
      imageUrl: 'https://example.com/laptop.jpg',
      price: 45000000,
      contributedAmount: 15000000,
    },
    // Add more items...
  ]);

  return (
    <View style={styles.container}>
      <Appbar.Header style={styles.header}>
        <Appbar.Content title="لیست آرزوها" color={theme.colors.white} />
        <Appbar.Action
          icon="bell"
          color={theme.colors.white}
          onPress={() => navigation.navigate('Notifications')}
        />
      </Appbar.Header>

      <FlatList
        data={wishlistItems}
        renderItem={({ item }) => (
          <WishlistItemCard
            title={item.title}
            description={item.description}
            imageUrl={item.imageUrl}
            price={item.price}
            contributedAmount={item.contributedAmount}
            onPress={() => navigation.navigate('WishlistItemDetail', { id: item.id })}
          />
        )}
        keyExtractor={item => item.id}
        contentContainerStyle={styles.listContainer}
      />

      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => navigation.navigate('AddWishlistItem')}
        color={theme.colors.white}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    backgroundColor: theme.colors.primary,
  },
  listContainer: {
    paddingBottom: theme.spacing.xl,
  },
  fab: {
    position: 'absolute',
    margin: theme.spacing.md,
    right: theme.spacing.md,
    bottom: theme.spacing.md,
    backgroundColor: theme.colors.accent,
  },
});
