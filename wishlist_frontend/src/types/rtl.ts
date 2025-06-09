export interface RTLConfig {
  isRTL: boolean;
  textAlign: 'right' | 'left';
  direction: 'rtl' | 'ltr';
  flexDirection: 'row' | 'row-reverse';
}

export interface RTLStyleProps {
  textAlign?: 'right' | 'left';
  writingDirection?: 'rtl' | 'ltr';
  textAlignVertical?: 'center' | 'auto' | 'top' | 'bottom';
  flexDirection?: 'row' | 'row-reverse' | 'column' | 'column-reverse';
}
