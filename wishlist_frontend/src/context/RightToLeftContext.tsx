import React, { createContext, useContext, ReactNode } from 'react';

interface RightToLeftContextType {
  isRTL: boolean;
  textAlign: 'right' | 'left';
  direction: 'rtl' | 'ltr';
  flexDirection: 'row' | 'row-reverse';
}

const RightToLeftContext = createContext<RightToLeftContextType>({
  isRTL: true,
  textAlign: 'right',
  direction: 'rtl',
  flexDirection: 'row-reverse',
});

export const useRTL = () => useContext(RightToLeftContext);

interface Props {
  children: ReactNode;
}

export const RightToLeftProvider: React.FC<Props> = ({ children }) => {
  const rtlStyles = {
    isRTL: true,
    textAlign: 'right' as const,
    direction: 'rtl' as const,
    flexDirection: 'row-reverse' as const,
  };

  return (
    <RightToLeftContext.Provider value={rtlStyles}>
      {children}
    </RightToLeftContext.Provider>
  );
};

// Utility function to create RTL-aware styles
export const createRTLStyles = (styles: any) => {
  const rtlStyles = { ...styles };
  
  // Convert padding and margin
  Object.keys(rtlStyles).forEach(key => {
    const style = rtlStyles[key];
    
    if (style.paddingLeft) {
      style.paddingEnd = style.paddingLeft;
      delete style.paddingLeft;
    }
    if (style.paddingRight) {
      style.paddingStart = style.paddingRight;
      delete style.paddingRight;
    }
    if (style.marginLeft) {
      style.marginEnd = style.marginLeft;
      delete style.marginLeft;
    }
    if (style.marginRight) {
      style.marginStart = style.marginRight;
      delete style.marginRight;
    }
    
    // Convert text alignment
    if (style.textAlign === 'left') {
      style.textAlign = 'right';
    }
    
    // Convert flex direction
    if (style.flexDirection === 'row') {
      style.flexDirection = 'row-reverse';
    }
  });
  
  return StyleSheet.create(rtlStyles);
};
