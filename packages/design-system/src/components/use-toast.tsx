'use client';
// ToastProvider now supports:
// - variant: 'success' | 'error' | 'info' (for color)
// - position: { top?: number, left?: number, right?: number, bottom?: number } (for custom placement)
// The default is bottom-right. Pass position to override.
// Example: toast({ title: 'Copied!', variant: 'success', position: { top: 100, left: 300 } })
import * as React from "react";

export type Toast = {
  id: string;
  title?: string;
  description?: string;
  duration?: number;
  variant?: 'success' | 'error' | 'info';
  position?: {
    top?: number;
    left?: number;
    right?: number;
    bottom?: number;
  };
};

const ToastContext = React.createContext<{
  toast: (toast: Omit<Toast, "id">) => void;
} | null>(null);

export function useToast() {
  const ctx = React.useContext(ToastContext);
  if (!ctx) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return ctx;
}

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = React.useState<Toast[]>([]);

  const toast = (t: Omit<Toast, "id">) => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts((prev) => [...prev, { ...t, id }]);
    // If duration === Infinity, don't auto-dismiss
    if (t.duration !== Infinity) {
      setTimeout(() => {
        setToasts((prev) => prev.filter((toast) => toast.id !== id));
      }, t.duration || 2000);
    }
  };

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      {toasts.map((t: Toast) => {
        let className =
          "border px-4 py-2 rounded shadow text-sm animate-fade-in bg-muted";
        if (t.variant === 'success') {
          className = "bg-green-600 text-white border-green-700 px-4 py-2 rounded shadow text-sm animate-fade-in";
        } else if (t.variant === 'error') {
          className = "bg-red-600 text-white border-red-700 px-4 py-2 rounded shadow text-sm animate-fade-in";
        } else if (t.variant === 'info') {
          className = "bg-blue-600 text-white border-blue-700 px-4 py-2 rounded shadow text-sm animate-fade-in";
        }
        const style = t.position
          ? {
              position: 'absolute' as const,
              ...t.position,
              zIndex: 9999,
            }
          : {
              position: 'fixed' as const,
              bottom: 16,
              right: 16,
              zIndex: 9999,
            };
        return (
          <div
            key={t.id}
            className={className + " relative min-w-[320px]"}
            style={style}
            data-testid="toast-notification"
            role="alert"
            aria-live="assertive"
            tabIndex={0}
          >
            {/* Close button in upper right for persistent toasts */}
            {t.duration === Infinity && (
              <button
                className="absolute top-2 right-2 text-white/80 hover:text-white font-bold text-lg focus:outline-none"
                aria-label="Close notification"
                onClick={() => setToasts((prev) => prev.filter((toast) => toast.id !== t.id))}
              >
                ×
              </button>
            )}
            {t.title && <div className="font-semibold">{t.title}</div>}
            {t.description && <div className="pr-8">{t.description}</div>}
          </div>
        );
      })}
    </ToastContext.Provider>
  );
};
