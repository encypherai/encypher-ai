import React from 'react';

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    value: any;
    name: string;
    dataKey: string;
    payload: any;
    color?: string;
  }>;
  label?: string;
  labelFormatter?: (label: string) => string;
  formatter?: (value: any, name: string, props: any) => [string, string];
}

/**
 * A custom tooltip component for Recharts that safely formats data
 * to prevent React rendering errors with objects
 */
const CustomTooltip: React.FC<CustomTooltipProps> = ({
  active,
  payload,
  label,
  labelFormatter,
  formatter
}) => {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  // Format the label if a formatter is provided
  const formattedLabel = labelFormatter ? labelFormatter(label || '') : `Date: ${label}`;

  return (
    <div className="bg-white dark:bg-gray-800 p-2 border border-gray-200 dark:border-gray-700 rounded shadow-md">
      <p className="text-gray-600 dark:text-gray-300 font-medium mb-1">{formattedLabel}</p>
      <div>
        {payload.map((entry, index) => {
          // Format the value and name if a formatter is provided
          const [formattedValue, formattedName] = formatter 
            ? formatter(entry.value, entry.name, entry) 
            : [entry.value?.toString() || '0', entry.name || entry.dataKey || 'Value'];
          
          return (
            <p 
              key={`item-${index}`} 
              style={{ color: entry.color }}
              className="text-sm"
            >
              {formattedName}: {formattedValue}
            </p>
          );
        })}
      </div>
    </div>
  );
};

export default CustomTooltip;
