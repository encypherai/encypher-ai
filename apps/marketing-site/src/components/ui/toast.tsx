import * as React from "react";

interface ToastProps {
  message: string;
  type?: "success" | "error" | "info";
  onClose?: () => void;
}

export const Toast: React.FC<ToastProps> = ({ message, type = "info", onClose }) => {
  React.useEffect(() => {
    const timer = setTimeout(() => {
      if (onClose) onClose();
    }, 4000);
    return () => clearTimeout(timer);
  }, [onClose]);

  let color = "bg-blue-600";
  if (type === "success") color = "bg-green-600";
  if (type === "error") color = "bg-red-600";

  return (
    <div
      className={`fixed bottom-4 right-4 z-50 px-4 py-2 rounded shadow-lg text-white ${color} relative`}
      role="alert"
      aria-live="assertive"
      style={{ minWidth: 320 }}
    >
      {/* Close button in upper right */}
      {onClose && (
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-white/80 hover:text-white font-bold text-lg"
          aria-label="Close notification"
        >
          ×
        </button>
      )}
      <div className="pr-8">{message}</div>
    </div>
  );
};
