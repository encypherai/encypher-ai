"use client";

import { Tabs, TabsList, TabsTrigger, TabsContent } from "@encypher/design-system";
import React, { useState } from "react";

export interface DashboardLayoutProps {
  orgPanel: React.ReactNode;
  invitationsPanel: React.ReactNode;
  keysPanel?: React.ReactNode;
  settingsPanel?: React.ReactNode;
  enterprisePanel?: React.ReactNode;
  initialTab?: string;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  orgPanel,
  invitationsPanel,
  keysPanel,
  settingsPanel,
  enterprisePanel,
  initialTab = "settings", // Prioritize user settings by default
}) => {
  const [activeTab, setActiveTab] = useState(initialTab);
  return (
    <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
      <TabsList>
        {settingsPanel && (
          <TabsTrigger
            value="settings"
            className={activeTab === "settings" ? "bg-blue-600 text-white" : ""}
          >
            Settings
          </TabsTrigger>
        )}
        {keysPanel && (
          <TabsTrigger
            value="keys"
            className={activeTab === "keys" ? "bg-blue-600 text-white" : ""}
          >
            Keys
          </TabsTrigger>
        )}
        {enterprisePanel && (
          <TabsTrigger
            value="enterprise"
            className={activeTab === "enterprise" ? "bg-blue-600 text-white" : ""}
          >
            Enterprise Tools
          </TabsTrigger>
        )}
        {/* Invitations tab temporarily hidden for future release */}
        {/*
        {invitationsPanel && (
          <TabsTrigger
            value="invitations"
            className={activeTab === "invitations" ? "bg-blue-600 text-white" : ""}
          >
            Invitations
          </TabsTrigger>
        )}
        */}
        <TabsTrigger
          value="organization"
          className={activeTab === "organization" ? "bg-blue-600 text-white" : ""}
        >
          Organization
        </TabsTrigger>
      </TabsList>
      {settingsPanel && <TabsContent value="settings"> {settingsPanel} </TabsContent>}
      {keysPanel && <TabsContent value="keys"> {keysPanel} </TabsContent>}
      {enterprisePanel && <TabsContent value="enterprise"> {enterprisePanel} </TabsContent>}
      <TabsContent value="organization">{orgPanel}</TabsContent>
      {/* InvitationsPanel content hidden for now */}
      {/* {invitationsPanel && <TabsContent value="invitations">{invitationsPanel}</TabsContent>} */}
    </Tabs>
  );
};
