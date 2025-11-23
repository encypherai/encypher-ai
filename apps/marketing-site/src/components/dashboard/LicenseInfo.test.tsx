import React from "react";
import { render, screen } from "@testing-library/react";
import { LicenseInfo, mapLicenseToProps } from "./LicenseInfo";

describe("LicenseInfo", () => {
  const license = {
    license_key: "FREE-1234-5678",
    tier: "free",
    status: "Active",
    issued_at: "2025-04-25T21:00:00Z",
    expires_at: "2026-04-25T21:00:00Z",
    is_trial: false
  };
  it("renders all license fields including expiresAt", () => {
    const props = mapLicenseToProps(license);
    render(<LicenseInfo {...props} />);
    expect(screen.getByText(/License Key/i)).toBeInTheDocument();
    expect(screen.getByText(license.license_key)).toBeInTheDocument();
    expect(screen.getByText(/Tier/i)).toBeInTheDocument();
    expect(screen.getByText(/Free/i)).toBeInTheDocument();
    expect(screen.getByText(/Status/i)).toBeInTheDocument();
    expect(screen.getByText(/Active/i)).toBeInTheDocument();
    expect(screen.getByText(/Issued At/i)).toBeInTheDocument();
    expect(screen.getByText(/Expires At/i)).toBeInTheDocument();
    // Dates are formatted, so check for presence of substring
    expect(screen.getByTitle(license.issued_at)).toBeInTheDocument();
    expect(screen.getByTitle(license.expires_at)).toBeInTheDocument();
  });

  it("shows warning or visual cue for expired license", () => {
    const expiredLicense = {
      license_key: "EXPIRED-9999-0000",
      tier: "Enterprise",
      status: "Expired",
      issued_at: "2024-04-25T21:00:00Z",
      expires_at: "2025-04-20T21:00:00Z",
      is_trial: false
    };
    const props = mapLicenseToProps(expiredLicense);
    render(<LicenseInfo {...props} />);
    expect(screen.getByText(/Expires At/i)).toBeInTheDocument();
    expect(screen.getByTitle(expiredLicense.expires_at)).toBeInTheDocument();
    // Optionally check for red badge or expired status
    expect(screen.getByText(/Expired/i)).toBeInTheDocument();
  });

  it("shows soon-to-expire license without error", () => {
    const soonExpiring = {
      license_key: "SOON-TO-EXPIRE-8888",
      tier: "Growth",
      status: "Active",
      issued_at: "2024-05-01T21:00:00Z",
      expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days from now
      is_trial: false
    };
    const props = mapLicenseToProps(soonExpiring);
    render(<LicenseInfo {...props} />);
    expect(screen.getByText(/Expires At/i)).toBeInTheDocument();
    expect(screen.getByTitle(soonExpiring.expires_at)).toBeInTheDocument();
    expect(screen.getByText(/Active/i)).toBeInTheDocument();
  });

  it("renders fallback for invalid expiresAt", () => {
    render(
      <LicenseInfo
        licenseKey="TEST-KEY"
        tier="free"
        status="Active"
        issuedAt="not-a-date"
        expiresAt="not-a-date"
        isTrial={false}
      />
    );
    expect(screen.getByText("Invalid date")).toBeInTheDocument();
  });

  it("renders fallback for missing expiresAt", () => {
    render(
      <LicenseInfo
        licenseKey="TEST-KEY"
        tier="free"
        status="Active"
        issuedAt={null as unknown as string}
        expiresAt={null as unknown as string}
        isTrial={false}
      />
    );
    expect(screen.getAllByText("N/A").length).toBeGreaterThan(0);
  });

  it("shows the correct tag for trial and full licenses", () => {
    const trialLicense = {
      license_key: "TRIAL-0000-1111",
      tier: "growth",
      status: "Active",
      issued_at: "2025-04-25T21:00:00Z",
      expires_at: "2025-05-25T21:00:00Z",
      is_trial: true
    };
    const fullLicense = {
      license_key: "FULL-2222-3333",
      tier: "enterprise",
      status: "Active",
      issued_at: "2025-04-25T21:00:00Z",
      expires_at: "2026-04-25T21:00:00Z",
      is_trial: false
    };
    const trialProps = mapLicenseToProps(trialLicense);
    render(<LicenseInfo {...trialProps} />);
    expect(screen.getByText("Trial")).toBeInTheDocument();
    // Rerender for full license
    const fullProps = mapLicenseToProps(fullLicense);
    render(<LicenseInfo {...fullProps} />);
    expect(screen.getByText("Full")).toBeInTheDocument();
  });
});
