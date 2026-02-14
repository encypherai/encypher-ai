'use client';

import { createContext, useContext, useState, useEffect, useRef, useCallback, ReactNode } from 'react';
import { useSession } from 'next-auth/react';

interface Organization {
  id: string;
  name: string;
  slug: string | null;
  email: string;
  account_type?: 'individual' | 'organization' | null;
  display_name?: string | null;
  anonymous_publisher?: boolean;
  tier: string;
  max_seats: number;
  subscription_status: string;
  created_at: string;
}

interface OrganizationContextType {
  organizations: Organization[];
  activeOrganization: Organization | null;
  setActiveOrganization: (org: Organization) => void;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

const OrganizationContext = createContext<OrganizationContextType | undefined>(undefined);

export function OrganizationProvider({ children }: { children: ReactNode }) {
  const { data: session } = useSession();
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [activeOrganization, setActiveOrgState] = useState<Organization | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const hasFetchedRef = useRef(false);

  const accessToken = (session?.user as any)?.accessToken as string | undefined;

  const fetchOrganizations = useCallback(async () => {
    if (!accessToken) {
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      // NEXT_PUBLIC_API_URL already includes /api/v1
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/organizations`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch organizations');
      }

      const data = await response.json();
      const orgs = data.data || [];
      setOrganizations(orgs);

      // Set active org from localStorage or use first org
      const savedOrgId = localStorage.getItem('activeOrganizationId');
      const savedOrg = orgs.find((org: Organization) => org.id === savedOrgId);
      
      if (savedOrg) {
        setActiveOrgState(savedOrg);
      } else if (orgs.length > 0) {
        setActiveOrgState(orgs[0]);
        localStorage.setItem('activeOrganizationId', orgs[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  }, [accessToken]);

  useEffect(() => {
    if (accessToken && !hasFetchedRef.current) {
      hasFetchedRef.current = true;
      fetchOrganizations();
    } else if (!accessToken) {
      hasFetchedRef.current = false;
      setIsLoading(false);
    }
  }, [accessToken, fetchOrganizations]);

  const setActiveOrganization = (org: Organization) => {
    setActiveOrgState(org);
    localStorage.setItem('activeOrganizationId', org.id);
  };

  return (
    <OrganizationContext.Provider
      value={{
        organizations,
        activeOrganization,
        setActiveOrganization,
        isLoading,
        error,
        refetch: fetchOrganizations,
      }}
    >
      {children}
    </OrganizationContext.Provider>
  );
}

export function useOrganization() {
  const context = useContext(OrganizationContext);
  if (context === undefined) {
    throw new Error('useOrganization must be used within an OrganizationProvider');
  }
  return context;
}
