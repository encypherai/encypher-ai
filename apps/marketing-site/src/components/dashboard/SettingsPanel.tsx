"use client";
import React from "react";
import { useSession } from "next-auth/react";
import { UserProfileCard } from "./UserProfileCard";

export const SettingsPanel: React.FC = () => {
  const { data: session } = useSession();
  const user = session?.user;
  const email = user?.email || "";
  const role = user?.role || "User";
  const isActive = Boolean(user?.isActive ?? true);

  return (
    <section className="flex flex-col gap-8 w-full max-w-2xl mx-auto py-8">
      <UserProfileCard email={email} role={role} isActive={isActive} />
    </section>
  );
};
