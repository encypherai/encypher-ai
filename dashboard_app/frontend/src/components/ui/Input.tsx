import React, { forwardRef } from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  fullWidth?: boolean;
  className?: string;
  labelClassName?: string;
  inputClassName?: string;
  icon?: React.ReactNode;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, fullWidth = true, className = '', labelClassName = '', inputClassName = '', icon, ...props }, ref) => {
    const widthClass = fullWidth ? 'w-full' : '';
    
    return (
      <div className={`${widthClass} ${className}`}>
        {label && (
          <label htmlFor={props.id} className={`block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 ${labelClassName}`}>
            {label}
          </label>
        )}
        <div className="relative">
          {icon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              {icon}
            </div>
          )}
          <input
            ref={ref}
            className={`input-field ${icon ? 'pl-10' : ''} ${error ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''} ${inputClassName}`}
            {...props}
          />
        </div>
        {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
        {helperText && !error && <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{helperText}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
