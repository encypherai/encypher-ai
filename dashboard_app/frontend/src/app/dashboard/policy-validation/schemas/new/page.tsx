'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { 
  ArrowLeftIcon,
  DocumentTextIcon,
} from '@heroicons/react/24/outline';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { policyValidationService, PolicySchemaCreate } from '@/lib/services/policy-validation';

export default function NewPolicySchemaPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PolicySchemaCreate>();
  
  const onSubmit = async (data: PolicySchemaCreate) => {
    try {
      setIsSubmitting(true);
      setError(null);
      await policyValidationService.createPolicySchema(data);
      router.push('/dashboard/policy-validation');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create policy schema. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <div className="space-y-6">
      <div className="flex items-center">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push('/dashboard/policy-validation')}
          className="mr-4"
        >
          <ArrowLeftIcon className="h-4 w-4 mr-1" />
          Back
        </Button>
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Create New Policy Schema</h1>
      </div>
      
      {error && (
        <div className="bg-red-50 dark:bg-red-900/30 border border-red-400 text-red-700 dark:text-red-300 px-4 py-3 rounded relative" role="alert">
          <span className="block sm:inline">{error}</span>
        </div>
      )}
      
      <Card>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <Input
            id="name"
            label="Schema Name"
            error={errors.name?.message}
            {...register('name', {
              required: 'Schema name is required',
            })}
          />
          
          <Input
            id="version"
            label="Version"
            type="number"
            step="0.1"
            error={errors.version?.message}
            {...register('version', {
              required: 'Version is required',
              valueAsNumber: true,
            })}
          />
          
          <div>
            <label htmlFor="schema" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              JSON Schema
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <DocumentTextIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
              </div>
              <textarea
                id="schema"
                rows={10}
                className="input-field pl-10"
                placeholder='{"type": "object", "properties": {...}}'
                {...register('schema', {
                  required: 'JSON schema is required',
                  validate: {
                    validJson: (value) => {
                      try {
                        JSON.parse(value);
                        return true;
                      } catch (e) {
                        return 'Invalid JSON format';
                      }
                    },
                  },
                })}
              />
            </div>
            {errors.schema && (
              <p className="mt-1 text-sm text-red-600">{errors.schema.message}</p>
            )}
          </div>
          
          <Input
            id="description"
            label="Description"
            error={errors.description?.message}
            {...register('description', {
              required: 'Description is required',
            })}
          />
          
          <div className="flex justify-end space-x-3">
            <Button
              variant="secondary"
              onClick={() => router.push('/dashboard/policy-validation')}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              isLoading={isSubmitting}
            >
              Create Schema
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
