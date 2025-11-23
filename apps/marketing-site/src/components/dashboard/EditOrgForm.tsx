"use client";
import React, { useState, useEffect } from "react";
import { orgUpdateSchema, OrgUpdateInput } from "@/lib/validation/orgSchema";

export type EditOrgFormProps = {
  name: string;
  contactEmail: string;
  address: string;
  onSave: (data: OrgUpdateInput) => void;
  onCancel: () => void;
};

export const EditOrgForm: React.FC<EditOrgFormProps> = ({
  name: initialName,
  contactEmail: initialContactEmail,
  address: initialAddress,
  onSave,
  onCancel,
}) => {
  const [name, setName] = useState(initialName ?? "");
  const [contactEmail, setContactEmail] = useState(initialContactEmail ?? "");
  const [address, setAddress] = useState(initialAddress ?? "");
  const [errors, setErrors] = useState<Partial<Record<keyof OrgUpdateInput, string>>>({});

  useEffect(() => {
    setName(initialName ?? "");
    setContactEmail(initialContactEmail ?? "");
    setAddress(initialAddress ?? "");
  }, [initialName, initialContactEmail, initialAddress]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    const input = { name, contactEmail, address };
    const result = orgUpdateSchema.safeParse(input);
    if (!result.success) {
      const fieldErrors: Partial<Record<keyof OrgUpdateInput, string>> = {};
      result.error.errors.forEach(err => {
        if (err.path && err.path[0]) {
          fieldErrors[err.path[0] as keyof OrgUpdateInput] = err.message;
        }
      });
      setErrors(fieldErrors);
      return;
    }
    onSave(result.data);
  };

  return (
    <form
      className="bg-white dark:bg-gray-900 rounded-lg shadow p-6 w-full max-w-xl mb-6 font-roboto"
      onSubmit={handleSubmit}
      noValidate
    >
      <h2 className="text-xl font-bold mb-4 font-roboto">Edit Organization Info</h2>
      <div className="mb-4">
        <label className="block font-semibold mb-1 font-roboto" htmlFor="org-name">Name</label>
        <input
          id="org-name"
          className={`w-full px-3 py-2 border rounded font-roboto ${errors.name ? 'border-red-500' : ''}`}
          value={name}
          onChange={e => setName(e.target.value)}
          required
          aria-invalid={!!errors.name}
          aria-describedby={errors.name ? 'org-name-error' : undefined}
        />
        {errors.name && <div className="text-red-500 text-xs mt-1" id="org-name-error">{errors.name}</div>}
      </div>
      <div className="mb-4">
        <label className="block font-semibold mb-1 font-roboto" htmlFor="org-email">Contact Email</label>
        <input
          id="org-email"
          type="email"
          className={`w-full px-3 py-2 border rounded font-roboto ${errors.contactEmail ? 'border-red-500' : ''}`}
          value={contactEmail}
          onChange={e => setContactEmail(e.target.value)}
          required
          aria-invalid={!!errors.contactEmail}
          aria-describedby={errors.contactEmail ? 'org-email-error' : undefined}
        />
        {errors.contactEmail && <div className="text-red-500 text-xs mt-1" id="org-email-error">{errors.contactEmail}</div>}
      </div>
      <div className="mb-4">
        <label className="block font-semibold mb-1 font-roboto" htmlFor="org-address">Address</label>
        <textarea
          id="org-address"
          className={`w-full px-3 py-2 border rounded font-roboto ${errors.address ? 'border-red-500' : ''}`}
          value={address}
          onChange={e => setAddress(e.target.value)}
          aria-invalid={!!errors.address}
          aria-describedby={errors.address ? 'org-address-error' : undefined}
        />
        {errors.address && <div className="text-red-500 text-xs mt-1" id="org-address-error">{errors.address}</div>}
      </div>
      <div className="flex gap-4 font-roboto">
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 font-roboto"
        >
          Save
        </button>
        <button
          type="button"
          className="px-4 py-2 bg-gray-400 text-white rounded hover:bg-gray-500 font-roboto"
          onClick={onCancel}
        >
          Cancel
        </button>
      </div>
    </form>
  );
};
