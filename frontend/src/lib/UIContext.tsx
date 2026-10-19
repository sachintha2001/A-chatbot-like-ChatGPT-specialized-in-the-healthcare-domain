"use client";

import React, { createContext, useContext, useState } from "react";

interface UIContextType {
  isCoverPage: boolean;
  setIsCoverPage: (val: boolean) => void;
}

const UIContext = createContext<UIContextType>({
  isCoverPage: true,
  setIsCoverPage: () => {},
});

export function UIProvider({ children }: { children: React.ReactNode }) {
  const [isCoverPage, setIsCoverPage] = useState<boolean>(true);

  return (
    <UIContext.Provider value={{ isCoverPage, setIsCoverPage }}>
      {children}
    </UIContext.Provider>
  );
}

export function useUI() {
  return useContext(UIContext);
}
