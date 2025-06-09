export const fonts = {
  regular: 'IRANSans-Regular',
  medium: 'IRANSans-Medium',
  bold: 'IRANSans-Bold',
  light: 'IRANSans-Light',
};

export const fontConfig = {
  ios: {
    regular: {
      fontFamily: fonts.regular,
      fontWeight: '400',
    },
    medium: {
      fontFamily: fonts.medium,
      fontWeight: '500',
    },
    bold: {
      fontFamily: fonts.bold,
      fontWeight: '700',
    },
    light: {
      fontFamily: fonts.light,
      fontWeight: '300',
    },
  },
  android: {
    regular: {
      fontFamily: fonts.regular,
    },
    medium: {
      fontFamily: fonts.medium,
    },
    bold: {
      fontFamily: fonts.bold,
    },
    light: {
      fontFamily: fonts.light,
    },
  },
};
