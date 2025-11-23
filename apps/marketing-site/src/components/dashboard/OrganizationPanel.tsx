"use client";
import React, { useState } from "react";
import { OrganizationInfo } from "@/components/dashboard/OrganizationInfo";
import { LicenseInfo, mapLicenseToProps } from "@/components/dashboard/LicenseInfo";
import { EditOrgForm } from "@/components/dashboard/EditOrgForm";
import { OrgPublicKeyCard } from "@/components/dashboard/OrgPublicKeyCard";
import { useOrganization } from "@/lib/hooks/useOrganization";
import { useLicense } from "@/lib/hooks/useLicense";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle, PlusCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export const OrganizationPanel: React.FC = () => {
  const { org, isLoading: orgLoading, error: orgError } = useOrganization();
  const { license, isLoading: licenseLoading, error: licenseError } = useLicense();
  const [editing, setEditing] = useState(false);

  console.log("[OrganizationPanel] render:", { 
    org, 
    orgLoading, 
    orgError, 
    license, 
    licenseLoading, 
    licenseError 
  });

  // Combined loading state
  const isLoading = orgLoading || licenseLoading;
  
  // Combined error state (excluding expected 404s which are handled as null org)
  const displayError = orgError || licenseError;

  // Render loading state
  if (isLoading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Organization Information</CardTitle>
          <CardDescription>Loading organization details...</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="h-24 w-full animate-pulse bg-muted rounded-md"></div>
          <div className="h-24 w-full animate-pulse bg-muted rounded-md"></div>
        </CardContent>
      </Card>
    );
  }

  // Render error state
  if (displayError) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Organization Information</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error Loading Organization</AlertTitle>
            <AlertDescription>
              {displayError instanceof Error 
                ? displayError.message 
                : String(displayError)}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  // Render "no organization" state
  if (!org) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Organization Information</CardTitle>
          <CardDescription>You are not part of any organization.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="text-center p-8 border border-dashed rounded-md">
            <p className="text-muted-foreground mb-4">
              You need to be part of an organization to access all features.
            </p>
            <Button variant="outline">
              <PlusCircle className="mr-2 h-4 w-4" />
              Create Organization
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Map org fields for OrganizationInfo
  const orgInfoProps = {
    name: org.name,
    revenueTier: org.revenue_tier,
    contactEmail: org.primary_contact_email,
    address: org.address,
    createdAt: org.created_at,
    updatedAt: org.updated_at,
    editable: true,
    onEdit: () => setEditing(true),
  };

  // Map license fields for LicenseInfo
  const licenseProps = license ? mapLicenseToProps(license) : undefined;

  // Props for EditOrgForm
  const editOrgFormProps = {
    name: org.name,
    contactEmail: org.primary_contact_email,
    address: org.address || "",
    onSave: () => setEditing(false), // TODO: Wire up save logic
    onCancel: () => setEditing(false),
  };

  // Props for OrgPublicKeyCard
  const orgPublicKeyProps = {
    publicKey: org.latest_org_public_key || "",
  };

  // Render normal state with organization information
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Organization Information</CardTitle>
        <CardDescription>View and manage your organization details</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {!editing ? (
          <OrganizationInfo {...orgInfoProps} />
        ) : (
          <EditOrgForm {...editOrgFormProps} />
        )}
        {licenseProps && <LicenseInfo {...licenseProps} />}
        <OrgPublicKeyCard publicKey={orgPublicKeyProps.publicKey} />
      </CardContent>
    </Card>
  );
};
