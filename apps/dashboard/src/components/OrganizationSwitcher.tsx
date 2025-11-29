'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useOrganization } from '../contexts/OrganizationContext';

export function OrganizationSwitcher() {
  const { organizations, activeOrganization, setActiveOrganization, isLoading } = useOrganization();
  const [isOpen, setIsOpen] = useState(false);

  // Don't show if no organizations or only one
  if (isLoading || organizations.length <= 1) {
    return null;
  }

  const getTierBadgeColor = (tier: string) => {
    switch (tier) {
      case 'enterprise':
        return 'bg-purple-100 text-purple-700';
      case 'business':
        return 'bg-blue-100 text-blue-700';
      case 'professional':
        return 'bg-green-100 text-green-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-lg transition-colors border border-slate-200"
      >
        {/* Building icon */}
        <svg className="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
        <span className="max-w-[120px] truncate">
          {activeOrganization?.name || 'Select Organization'}
        </span>
        <svg className={`w-4 h-4 text-slate-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-40" 
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown */}
          <div className="absolute left-0 mt-2 w-72 bg-white rounded-xl shadow-lg border border-slate-200 z-50 overflow-hidden">
            <div className="p-2 border-b border-slate-100">
              <p className="px-2 py-1 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Your Organizations
              </p>
            </div>
            
            <div className="max-h-64 overflow-y-auto p-2">
              {organizations.map((org) => (
                <button
                  key={org.id}
                  onClick={() => {
                    setActiveOrganization(org);
                    setIsOpen(false);
                  }}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                    activeOrganization?.id === org.id
                      ? 'bg-blue-50 border border-blue-200'
                      : 'hover:bg-slate-50'
                  }`}
                >
                  {/* Org icon */}
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-semibold ${
                    activeOrganization?.id === org.id
                      ? 'bg-blue-ncs text-white'
                      : 'bg-slate-200 text-slate-600'
                  }`}>
                    {org.name.charAt(0).toUpperCase()}
                  </div>
                  
                  <div className="flex-1 text-left min-w-0">
                    <p className="font-medium text-sm text-slate-900 truncate">
                      {org.name}
                    </p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className={`px-1.5 py-0.5 text-xs font-medium rounded ${getTierBadgeColor(org.tier)}`}>
                        {org.tier.charAt(0).toUpperCase() + org.tier.slice(1)}
                      </span>
                      {org.subscription_status !== 'active' && (
                        <span className="text-xs text-amber-600">
                          {org.subscription_status}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  {/* Checkmark for active */}
                  {activeOrganization?.id === org.id && (
                    <svg className="w-5 h-5 text-blue-ncs" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </button>
              ))}
            </div>
            
            {/* Create new org link */}
            <div className="p-2 border-t border-slate-100">
              <Link
                href="/team?action=create-org"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-2 px-3 py-2 text-sm text-blue-ncs hover:bg-blue-50 rounded-lg transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Create New Organization
              </Link>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
