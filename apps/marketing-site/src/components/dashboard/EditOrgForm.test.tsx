import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { EditOrgForm } from "./EditOrgForm";

describe("EditOrgForm", () => {
  const defaultProps = {
    name: "Acme Inc.",
    contactEmail: "contact@acme.com",
    address: "123 Main St",
    onSave: jest.fn(),
    onCancel: jest.fn(),
  };

  it("renders with initial values", () => {
    render(<EditOrgForm {...defaultProps} />);
    expect(screen.getByLabelText(/name/i)).toHaveValue("Acme Inc.");
    expect(screen.getByLabelText(/contact email/i)).toHaveValue("contact@acme.com");
    expect(screen.getByLabelText(/address/i)).toHaveValue("123 Main St");
  });

  it("shows validation errors for empty required fields", () => {
    render(<EditOrgForm {...defaultProps} />);
    fireEvent.change(screen.getByLabelText(/name/i), { target: { value: "" } });
    fireEvent.change(screen.getByLabelText(/contact email/i), { target: { value: "" } });
    fireEvent.submit(screen.getByRole("button", { name: /save/i }));
    expect(screen.getByText(/organization name is required/i)).toBeInTheDocument();
    expect(screen.getByText(/invalid email address/i)).toBeInTheDocument();
  });

  it("shows validation error for invalid email", () => {
    render(<EditOrgForm {...defaultProps} />);
    fireEvent.change(screen.getByLabelText(/contact email/i), { target: { value: "not-an-email" } });
    fireEvent.submit(screen.getByRole("button", { name: /save/i }));
    expect(screen.getByText(/invalid email address/i)).toBeInTheDocument();
  });

  it("calls onSave with valid values", () => {
    const onSave = jest.fn();
    render(<EditOrgForm {...defaultProps} onSave={onSave} />);
    fireEvent.change(screen.getByLabelText(/name/i), { target: { value: "New Org" } });
    fireEvent.change(screen.getByLabelText(/contact email/i), { target: { value: "new@org.com" } });
    fireEvent.change(screen.getByLabelText(/address/i), { target: { value: "456 Elm St" } });
    fireEvent.submit(screen.getByRole("button", { name: /save/i }));
    expect(onSave).toHaveBeenCalledWith({ name: "New Org", contactEmail: "new@org.com", address: "456 Elm St" });
  });

  it("calls onCancel when Cancel button is clicked", () => {
    const onCancel = jest.fn();
    render(<EditOrgForm {...defaultProps} onCancel={onCancel} />);
    fireEvent.click(screen.getByRole("button", { name: /cancel/i }));
    expect(onCancel).toHaveBeenCalled();
  });
});
