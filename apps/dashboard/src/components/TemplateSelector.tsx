'use client';

import { useQuery } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import apiClient, { C2PATemplate } from '../lib/api';

interface TemplateSelectorProps {
  value?: string;
  onValueChange: (templateId: string | undefined) => void;
  disabled?: boolean;
  className?: string;
}

// Category display names and colors
const CATEGORY_CONFIG: Record<string, { label: string; color: string }> = {
  publisher: { label: 'Publisher', color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' },
  news: { label: 'News', color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' },
  academic: { label: 'Academic', color: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200' },
  legal: { label: 'Legal', color: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200' },
};

function getCategoryBadge(category: string | null) {
  if (!category) return null;
  const config = CATEGORY_CONFIG[category] || { label: category, color: 'bg-gray-100 text-gray-800' };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${config.color}`}>
      {config.label}
    </span>
  );
}

export function TemplateSelector({
  value,
  onValueChange,
  disabled = false,
  className,
}: TemplateSelectorProps) {
  const { data: session } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;

  const templatesQuery = useQuery({
    queryKey: ['c2pa-templates'],
    queryFn: async () => {
      if (!accessToken) throw new Error('Not authenticated');
      return apiClient.getC2PATemplates(accessToken);
    },
    enabled: Boolean(accessToken),
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });

  const templates = templatesQuery.data?.templates || [];
  const isLoading = templatesQuery.isLoading;
  const isError = templatesQuery.isError;

  // Group templates by category
  const groupedTemplates = templates.reduce<Record<string, C2PATemplate[]>>((acc, template) => {
    const category = template.category || 'other';
    if (!acc[category]) acc[category] = [];
    acc[category].push(template);
    return acc;
  }, {});

  // Find selected template for display
  const selectedTemplate = templates.find((t) => t.id === value);

  if (isError) {
    return (
      <div className={`text-sm text-muted-foreground ${className}`}>
        No rights templates configured
      </div>
    );
  }

  return (
    <Select
      value={value || 'none'}
      onValueChange={(val) => onValueChange(val === 'none' ? undefined : val)}
      disabled={disabled || isLoading}
    >
      <SelectTrigger className={className}>
        <SelectValue placeholder={isLoading ? 'Loading templates...' : 'Select a template (optional)'}>
          {selectedTemplate && (
            <div className="flex items-center gap-2">
              <span>{selectedTemplate.name}</span>
              {getCategoryBadge(selectedTemplate.category)}
            </div>
          )}
        </SelectValue>
      </SelectTrigger>
      <SelectContent>
        {/* No template option */}
        <SelectItem value="none">
          <span className="text-muted-foreground">No template (default)</span>
        </SelectItem>

        {/* Group by category */}
        {Object.entries(groupedTemplates).map(([category, categoryTemplates]) => (
          <SelectGroup key={category}>
            <SelectLabel className="flex items-center gap-2">
              {getCategoryBadge(category)}
              <span className="text-xs text-muted-foreground">
                ({categoryTemplates.length})
              </span>
            </SelectLabel>
            {categoryTemplates.map((template) => (
              <SelectItem key={template.id} value={template.id}>
                <div className="flex flex-col gap-0.5">
                  <span className="font-medium">{template.name}</span>
                  {template.description && (
                    <span className="text-xs text-muted-foreground line-clamp-1">
                      {template.description}
                    </span>
                  )}
                </div>
              </SelectItem>
            ))}
          </SelectGroup>
        ))}

        {templates.length === 0 && !isLoading && (
          <div className="px-2 py-4 text-center text-sm text-muted-foreground">
            No templates available
          </div>
        )}
      </SelectContent>
    </Select>
  );
}

export default TemplateSelector;
