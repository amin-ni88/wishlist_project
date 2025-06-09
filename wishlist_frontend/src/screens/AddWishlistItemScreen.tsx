import React, { useState } from 'react';
import { StyleSheet, View, ScrollView, Image } from 'react-native';
import { Appbar, TextInput, Button, IconButton } from 'react-native-paper';
import * as ImagePicker from 'expo-image-picker';
import { theme } from '../utils/theme';
import { useRTL, createRTLStyles } from '../context/RightToLeftContext';

export const AddWishlistItemScreen = ({ navigation }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState('');
  const [productUrl, setProductUrl] = useState('');
  const [image, setImage] = useState(null);

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [16, 9],
      quality: 0.8,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
    }
  };

  const handleSubmit = async () => {
    // Handle form submission
    // Upload image and create wishlist item
    navigation.goBack();
  };

  return (
    <View style={styles.container}>
      <Appbar.Header style={styles.header}>
        <Appbar.BackAction onPress={() => navigation.goBack()} color={theme.colors.white} />
        <Appbar.Content title="افزودن آرزوی جدید" color={theme.colors.white} />
      </Appbar.Header>

      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.imageContainer}>
          {image ? (
            <Image source={{ uri: image }} style={styles.image} />
          ) : (
            <IconButton
              icon="camera"
              size={40}
              onPress={pickImage}
              style={styles.imageButton}
            />
          )}
        </View>

        <TextInput
          label="عنوان"
          value={title}
          onChangeText={setTitle}
          style={styles.input}
        />

        <TextInput
          label="توضیحات"
          value={description}
          onChangeText={setDescription}
          multiline
          numberOfLines={4}
          style={styles.input}
        />

        <TextInput
          label="قیمت (تومان)"
          value={price}
          onChangeText={setPrice}
          keyboardType="numeric"
          style={styles.input}
        />

        <TextInput
          label="لینک محصول"
          value={productUrl}
          onChangeText={setProductUrl}
          keyboardType="url"
          style={styles.input}
        />

        <Button
          mode="contained"
          onPress={handleSubmit}
          style={styles.submitButton}
          labelStyle={styles.submitButtonLabel}
        >
          ثبت آرزو
        </Button>
      </ScrollView>
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
  content: {
    padding: theme.spacing.md,
  },
  imageContainer: {
    height: 200,
    backgroundColor: theme.colors.secondary,
    borderRadius: theme.roundness,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: theme.spacing.lg,
    overflow: 'hidden',
  },
  image: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  imageButton: {
    backgroundColor: theme.colors.surface,
  },
  input: {
    marginBottom: theme.spacing.md,
    backgroundColor: theme.colors.surface,
  },
  submitButton: {
    marginTop: theme.spacing.lg,
    backgroundColor: theme.colors.accent,
    paddingVertical: theme.spacing.sm,
  },
  submitButtonLabel: {
    fontSize: 16,
    fontWeight: 'bold',
  },
});
