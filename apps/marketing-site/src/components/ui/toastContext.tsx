// This file is now deprecated. ToastProvider is unified in use-toast.tsx. Please use that instead.
// (Optionally, you may delete this file if you have migrated all imports.)

"use client";
import React, { createContext, useCallback, useContext, useState } from "react";
import { Toast } from "./toast";

interface ToastContextProps {
  showToast: (message: string, type?: "success" | "error" | "info") => void;
}

const ToastContext = createContext<ToastContextProps | undefined>(undefined);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toast, setToast] = useState<{
    message: string;
    type: "success" | "error" | "info";
    visible: boolean;
  }>({ message: "", type: "info", visible: false });

  const showToast = useCallback((message: string, type: "success" | "error" | "info" = "info") => {
    setToast({ message, type, visible: true });
  }, []);

  const handleClose = useCallback(() => {
    setToast((prev) => ({ ...prev, visible: false }));
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {toast.visible && (
        <Toast message={toast.message} type={toast.type} onClose={handleClose} />
      )}
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) throw new Error("useToast must be used within a ToastProvider");
  return context;
};
