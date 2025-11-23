"use client";
import React from 'react';
import { useOrganization } from '@/lib/hooks/useOrganization';
import { useUserKey } from '@/lib/hooks/useUserKey';
import { UserKeyCard } from './UserKeyCard';
import { OrgPublicKeyCard } from './OrgPublicKeyCard';
import { useSession } from 'next-auth/react';

export const KeysPanel: React.FC = () => {
  const { data: session } = useSession();
  const token = session?.accessToken;
  const { org, error: orgError, isLoading: orgLoading } = useOrganization();
  const { error: userKeyError } = useUserKey(token);

  console.log("[KeysPanel] render. org:", org, "orgError:", orgError, "orgLoading:", orgLoading);

  // Render the main section - always render both cards regardless of loading state
  return (
    <section className="w-full max-w-4xl mx-auto py-8">
      <div className="flex flex-col md:flex-row md:gap-8 gap-4">
        {/* UserKeyCard always shown */} 
        <div className="md:w-1/2 w-full order-2 md:order-1">
          <UserKeyCard />
        </div>

        {/* OrgPublicKeyCard always shown - it will handle empty state internally */}
        <div className="md:w-1/2 w-full order-1 md:order-2">
          <OrgPublicKeyCard publicKey={org?.latest_org_public_key ?? ''} />
        </div>
      </div>
      
      {/* Display errors below the cards */}
      {(orgError || userKeyError) && (
        <div className="mt-4 p-4 border border-destructive rounded-md bg-destructive/10 text-destructive">
          {orgError && <div>Org Error: {String(orgError)}</div>}
          {userKeyError && <div>Key Error: {String(userKeyError)}</div>}
        </div>
      )}
    </section>
  );
};
