"use client";

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { useToast } from '@/components/ui/use-toast';
import type { RevenueTier } from "@/types/organization";

// Define valid revenue tiers (reflecting current product tiers)
const REVENUE_TIERS = [
  { label: 'Free/AGPL', value: 'free_agpl' },
  { label: 'Growth', value: 'growth' },
  { label: 'Enterprise', value: 'enterprise' },
];

interface CreateOrgFormProps {
  onSave: (name: string, revenueTier: RevenueTier, address?: string) => Promise<void>;
  onCancel: () => void;
}

export function CreateOrgForm({ onSave, onCancel }: CreateOrgFormProps) {
  const [name, setName] = useState('');
  const [revenueTier, setRevenueTier] = useState<RevenueTier | undefined>(undefined);
  const [address, setAddress] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!name.trim()) {
      toast({ title: 'Validation Error', description: 'Organization name is required.', variant: 'error' });
      return;
    }
    if (!revenueTier) {
      toast({ title: 'Validation Error', description: 'Please select a revenue tier.', variant: 'error' });
      return;
    }
    if (address && ["free_agpl", "growth", "enterprise"].includes(address)) {
      toast({ title: 'Validation Error', description: 'Address cannot be a revenue tier value.', variant: 'error' });
      return;
    }
    setIsLoading(true);
    try {
      await onSave(name, revenueTier, address);
      // onSave should handle success toast/navigation
    } catch (error: unknown) {
      // onSave should handle error display
      console.error('Error creating organization:', error);
      let errorMessage = 'Unknown error';
      if (error instanceof Error) {
          errorMessage = error.message;
      }
      // Potentially show a generic error toast here if onSave doesn't
      toast({ title: 'Error', description: `Failed to create organization: ${errorMessage}`, variant: 'error' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto border border-border bg-neutral-900 text-neutral-100 shadow-xl">
      <CardHeader>
        <CardTitle>Create New Organization</CardTitle>
        <CardDescription>Enter the details for your new organization.</CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="orgName">Organization Name</Label>
            <Input
              id="orgName"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your Company, Inc."
              required
              disabled={isLoading}
              className="bg-neutral-900 text-neutral-100 border border-border focus:ring-primary"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="revenueTier">Revenue Tier</Label>
            <Select
              value={revenueTier as RevenueTier | undefined}
              onValueChange={(v) => setRevenueTier(v as RevenueTier)}
              required
              disabled={isLoading}
            >
              <SelectTrigger id="revenueTier" className="bg-neutral-900 text-neutral-100 border border-border focus:ring-primary">
                <SelectValue placeholder="Select a tier..." />
              </SelectTrigger>
              <SelectContent className="bg-neutral-900 text-neutral-100 border border-border">
                {REVENUE_TIERS.map((tier) => (
                  <SelectItem key={tier.value} value={tier.value} className="bg-neutral-900 text-neutral-100">
                    {tier.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="address">Address (optional)</Label>
            <Input
              id="address"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              placeholder="123 Main St, City, Country"
              disabled={isLoading}
              className="bg-neutral-900 text-neutral-100 border border-border focus:ring-primary"
            />
          </div>
        </CardContent>
        <CardFooter className="flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onCancel} disabled={isLoading}>
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Creating...' : 'Create Organization'}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
