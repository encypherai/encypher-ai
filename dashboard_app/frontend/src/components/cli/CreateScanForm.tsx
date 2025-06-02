'use client';

import React, { useState } from 'react';
import { useMutation, useQueryClient } from 'react-query';
import { FolderIcon } from '@heroicons/react/24/outline';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import { useNotifications } from '@/lib/notifications';
import cliService from '@/services/cliService';

// Define the scan types for better type safety
type ScanType = 'audit_log' | 'policy_validation';

// Define the parameters structure based on scan type
interface ScanParameters {
  output_format?: string;
  custom_fields?: string[];
  policy_schema?: string;
  output_file?: string;
  [key: string]: any; // Allow for additional parameters
}

// Define the form data structure
interface ScanFormData {
  scan_type: ScanType;
  target_path: string;
  parameters: ScanParameters;
}

interface CreateScanFormProps {
  onSuccess?: () => void;
  className?: string;
}

export default function CreateScanForm({ onSuccess, className = '' }: CreateScanFormProps) {
  const queryClient = useQueryClient();
  const { addNotification } = useNotifications();
  
  const [formData, setFormData] = useState<ScanFormData>({
    scan_type: 'audit_log',
    target_path: '',
    parameters: {},
  });

  const [advancedMode, setAdvancedMode] = useState(false);
  const [parametersJson, setParametersJson] = useState('{}');
  const [jsonError, setJsonError] = useState('');

  // Form validation state
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  
  // Mutation for creating a new scan
  const createScanMutation = useMutation<any, Error, ScanFormData>(
    (data: ScanFormData) => cliService.startScan(data),
    {
      onSuccess: (response) => {
        const scanId = response?.id || 'new';
        addNotification({
          type: 'success',
          title: 'Scan started',
          message: `The CLI scan has been started successfully. Scan ID: ${scanId}`,
        });
        // Invalidate queries to refresh scan lists
        queryClient.invalidateQueries('cliScans');
        queryClient.invalidateQueries('activeScans');
        
        // Call onSuccess callback if provided
        if (onSuccess) onSuccess();
        
        // Reset form to initial state
        setFormData({
          scan_type: 'audit_log',
          target_path: '',
          parameters: {},
        });
        setParametersJson('{}');
        setJsonError('');
        setFormErrors({});
      },
      onError: (error: Error) => {
        addNotification({
          type: 'error',
          title: 'Failed to start scan',
          message: error.message || 'An unexpected error occurred',
        });
      },
    }
  );

  // Handle form input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // Handle parameters JSON input with improved validation
  const handleParametersChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const jsonValue = e.target.value;
    setParametersJson(jsonValue);
    setJsonError('');
    
    if (!jsonValue.trim()) {
      // Empty JSON is valid - set to empty object
      setFormData((prev) => ({
        ...prev,
        parameters: {},
      }));
      return;
    }
    
    try {
      const parsedJson = JSON.parse(jsonValue) as ScanParameters;
      
      // Validate that the parsed JSON is an object
      if (typeof parsedJson !== 'object' || parsedJson === null || Array.isArray(parsedJson)) {
        setJsonError('Parameters must be a JSON object');
        return;
      }
      
      setFormData((prev) => ({
        ...prev,
        parameters: parsedJson,
      }));
    } catch (err) {
      setJsonError('Invalid JSON format');
    }
  };

  // Validate form data and return validation errors
  const validateForm = (): Record<string, string> => {
    const errors: Record<string, string> = {};
    
    // Check for JSON format errors
    if (jsonError) {
      errors.parameters = jsonError;
    }
    
    // Validate required fields
    if (!formData.target_path.trim()) {
      errors.target_path = 'Target path is required';
    }
    
    // Validate scan type specific parameters
    if (formData.scan_type === 'policy_validation') {
      if (!formData.parameters.policy_schema || !formData.parameters.policy_schema.trim()) {
        errors.policy_schema = 'Policy schema path is required for policy validation scans';
      }
    }
    
    return errors;
  };
  
  // Handle form submission with improved validation
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate the form
    const errors = validateForm();
    setFormErrors(errors);
    
    // If there are errors, don't submit
    if (Object.keys(errors).length > 0) {
      // Show the first error as a notification
      const firstError = Object.values(errors)[0];
      addNotification({
        type: 'error',
        title: 'Validation Error',
        message: firstError,
      });
      return;
    }
    
    // Submit the form if validation passes
    createScanMutation.mutate(formData);
  };

  return (
    <Card title="Start New CLI Scan" className={className}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Select
          label="Scan Type"
          name="scan_type"
          value={formData.scan_type}
          onChange={(value) => handleInputChange({ target: { name: 'scan_type', value } } as any)}
          options={[
            { value: 'audit_log', label: 'Audit Log' },
            { value: 'policy_validation', label: 'Policy Validation' },
          ]}
        />
        
        <div className="flex items-end gap-2">
          <Input
            label="Target Path"
            name="target_path"
            value={formData.target_path}
            onChange={(e) => {
              handleInputChange(e);
              // Clear error when user types
              if (formErrors.target_path) {
                setFormErrors(prev => ({ ...prev, target_path: '' }));
              }
            }}
            placeholder="/path/to/directory"
            className="flex-1"
            error={formErrors.target_path}
          />
          <Button
            type="button"
            variant="secondary"
            className="mb-[1px]"
            onClick={() => {
              // In a real app, this would open a file picker
              addNotification({
                type: 'info',
                title: 'Feature Not Available',
                message: 'File browser integration is not available in this version.',
              });
            }}
          >
            <FolderIcon className="h-5 w-5" />
          </Button>
        </div>
        
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Parameters</h4>
          <Button
            type="button"
            variant="ghost"
            size="xs"
            onClick={() => setAdvancedMode(!advancedMode)}
          >
            {advancedMode ? 'Simple Mode' : 'Advanced Mode'}
          </Button>
        </div>
        
        {advancedMode ? (
          <div>
            <textarea
              className={`w-full h-32 p-2 border rounded-md font-mono text-sm ${
                jsonError || formErrors.parameters ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : 'border-gray-300 dark:border-gray-700'
              } bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100`}
              value={parametersJson}
              onChange={handleParametersChange}
              placeholder='{"key": "value"}'
            />
            {(jsonError || formErrors.parameters) && (
              <p className="mt-1 text-sm text-red-600">{jsonError || formErrors.parameters}</p>
            )}
            <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
              <p>Example for Audit Log: <code>{'{"output_format": "csv", "custom_fields": ["department_id"]}'}</code></p>
              <p>Example for Policy Validation: <code>{'{"policy_schema": "/path/to/policy.json", "output_file": "results.csv"}'}</code></p>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {formData.scan_type === 'audit_log' && (
              <>
                <Input
                  label="Output Format"
                  name="output_format"
                  placeholder="csv"
                  onChange={(e) => {
                    const value = e.target.value;
                    setFormData((prev) => ({
                      ...prev,
                      parameters: {
                        ...prev.parameters,
                        output_format: value,
                      },
                    }));
                    try {
                      const updatedParams = {
                        ...formData.parameters,
                        output_format: value,
                      };
                      setParametersJson(JSON.stringify(updatedParams, null, 2));
                    } catch (err) {
                      // Ignore errors here
                    }
                  }}
                  value={formData.parameters.output_format || ''}
                />
                <Input
                  label="Custom Fields"
                  name="custom_fields"
                  placeholder="department_id,project_code"
                  onChange={(e) => {
                    const value = e.target.value;
                    setFormData((prev) => ({
                      ...prev,
                      parameters: {
                        ...prev.parameters,
                        custom_fields: value.split(',').map(f => f.trim()).filter(Boolean),
                      },
                    }));
                    try {
                      const updatedParams = {
                        ...formData.parameters,
                        custom_fields: value.split(',').map(f => f.trim()).filter(Boolean),
                      };
                      setParametersJson(JSON.stringify(updatedParams, null, 2));
                    } catch (err) {
                      // Ignore errors here
                    }
                  }}
                  value={Array.isArray(formData.parameters.custom_fields) ? formData.parameters.custom_fields.join(', ') : ''}
                />
              </>
            )}
            
            {formData.scan_type === 'policy_validation' && (
              <>
                <Input
                  label="Policy Schema Path"
                  name="policy_schema"
                  placeholder="/path/to/policy.json"
                  onChange={(e) => {
                    const value = e.target.value;
                    setFormData((prev) => ({
                      ...prev,
                      parameters: {
                        ...prev.parameters,
                        policy_schema: value,
                      },
                    }));
                    try {
                      const updatedParams = {
                        ...formData.parameters,
                        policy_schema: value,
                      };
                      setParametersJson(JSON.stringify(updatedParams, null, 2));
                    } catch (err) {
                      // Ignore errors here
                    }
                    
                    // Clear error when user types
                    if (formErrors.policy_schema) {
                      setFormErrors(prev => ({ ...prev, policy_schema: '' }));
                    }
                  }}
                  value={formData.parameters.policy_schema || ''}
                  error={formErrors.policy_schema}
                />
                <Input
                  label="Output File"
                  name="output_file"
                  placeholder="validation_results.csv"
                  onChange={(e) => {
                    const value = e.target.value;
                    setFormData((prev) => ({
                      ...prev,
                      parameters: {
                        ...prev.parameters,
                        output_file: value,
                      },
                    }));
                    try {
                      const updatedParams = {
                        ...formData.parameters,
                        output_file: value,
                      };
                      setParametersJson(JSON.stringify(updatedParams, null, 2));
                    } catch (err) {
                      // Ignore errors here
                    }
                  }}
                  value={formData.parameters.output_file || ''}
                />
              </>
            )}
          </div>
        )}
        
        <div className="flex justify-between pt-2">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            {createScanMutation.isLoading && (
              <span className="flex items-center">
                <span className="inline-block h-2 w-2 rounded-full bg-blue-500 mr-2 animate-pulse"></span>
                Starting scan...
              </span>
            )}
          </div>
          <div className="flex space-x-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setFormData({
                  scan_type: 'audit_log',
                  target_path: '',
                  parameters: {},
                });
                setParametersJson('{}');
                setJsonError('');
                setFormErrors({});
              }}
              disabled={createScanMutation.isLoading}
            >
              Reset
            </Button>
            <Button
              type="submit"
              isLoading={createScanMutation.isLoading}
              disabled={!formData.target_path || jsonError !== ''}
            >
              Start Scan
            </Button>
          </div>
        </div>
      </form>
    </Card>
  );
}
