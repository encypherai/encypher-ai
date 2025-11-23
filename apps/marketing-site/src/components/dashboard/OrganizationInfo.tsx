"use client";
import React from "react";
import { Building2, Pencil, Mail, DollarSign, MapPin, CalendarCheck } from "lucide-react";

export type OrganizationInfoProps = {
  name: string;
  revenueTier: string;
  contactEmail: string;
  address?: string;
  createdAt: string;
  updatedAt: string;
  editable?: boolean;
  onEdit?: () => void;
};

// Utility: Map backend revenue tier to user-friendly label
const getRevenueTierLabel = (tier: string) => {
  switch (tier?.toLowerCase()) {
    case 'free_agpl':
    case 'free':
      return 'Free / Open Source';
    case 'growth':
      return 'Growth License';
    case 'enterprise':
      return 'Enterprise License';
    default:
      return tier || 'Unknown';
  }
};

export const OrganizationInfo: React.FC<OrganizationInfoProps> = ({
  name,
  revenueTier,
  contactEmail,
  address,
  createdAt,
  updatedAt,
  editable,
  onEdit,
}) => (
  <section className="relative bg-white/80 dark:bg-gray-900/70 rounded-2xl shadow-lg ring-1 ring-gray-200 dark:ring-gray-800 p-8 w-full max-w-xl mb-8 backdrop-blur-md font-roboto" aria-label="Organization Information" tabIndex={0}>
    <div className="flex items-center justify-between mb-6">
      <h2 className="text-xl font-bold flex items-center gap-2 font-roboto">
        <span className="sr-only">Organization Information</span>
        <Building2 className="w-6 h-6 text-indigo-500" /> Organization Info
      </h2>
      {editable && onEdit && (
        <button
          className="flex items-center gap-2 px-3 py-1 rounded bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400 transition font-roboto"
          onClick={onEdit}
          aria-label="Edit organization info"
        >
          <Pencil className="w-4 h-4" /> Edit
        </button>
      )}
    </div>
    <dl className="grid grid-cols-2 gap-x-4 gap-y-2 font-roboto">
      <dt className="text-gray-500 dark:text-gray-400 font-semibold flex items-center gap-2 font-roboto"><Mail className="w-4 h-4 text-blue-400" />Contact Email</dt>
      <dd className="font-mono text-base text-gray-900 dark:text-white font-roboto" tabIndex={0}>{contactEmail}</dd>
      <dt className="text-gray-500 dark:text-gray-400 font-semibold flex items-center gap-2 font-roboto"><DollarSign className="w-4 h-4 text-green-400" />Revenue Tier</dt>
      <dd className="text-base text-gray-900 dark:text-white font-roboto" tabIndex={0}>{getRevenueTierLabel(revenueTier)}</dd>
      <dt className="text-gray-500 dark:text-gray-400 font-semibold flex items-center gap-2 font-roboto"><Building2 className="w-4 h-4 text-indigo-400" />Name</dt>
      <dd className="text-base text-gray-900 dark:text-white font-roboto" tabIndex={0}>{name}</dd>
      {address && (
        <>
          <dt className="text-gray-500 dark:text-gray-400 font-semibold flex items-center gap-2 font-roboto"><MapPin className="w-4 h-4 text-pink-400" />Address</dt>
          <dd className="text-base text-gray-900 dark:text-white font-roboto" tabIndex={0}>{address}</dd>
        </>
      )}
      <dt className="text-gray-500 dark:text-gray-400 font-semibold flex items-center gap-2 font-roboto"><CalendarCheck className="w-4 h-4 text-yellow-400" />Created At</dt>
      <dd className="font-mono text-xs text-gray-700 dark:text-gray-300 font-roboto" title={createdAt} tabIndex={0}>{new Date(createdAt).toLocaleString()}</dd>
      <dt className="text-gray-500 dark:text-gray-400 font-semibold flex items-center gap-2 font-roboto"><CalendarCheck className="w-4 h-4 text-orange-400" />Updated At</dt>
      <dd className="font-mono text-xs text-gray-700 dark:text-gray-300 font-roboto" title={updatedAt} tabIndex={0}>{new Date(updatedAt).toLocaleString()}</dd>
    </dl>
  </section>
);
