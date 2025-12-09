# @encypher/sdk@1.0.0-alpha.1

A TypeScript SDK client for the localhost API.

## Usage

First, install the SDK from npm.

```bash
npm install @encypher/sdk --save
```

Next, try it out.


```ts
import {
  Configuration,
  AuditApi,
} from '@encypher/sdk';
import type { ExportAuditLogsApiV1AuditLogsExportGetRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new AuditApi(config);

  const body = {
    // string (optional)
    format: format_example,
    // string (optional)
    startDate: startDate_example,
    // string (optional)
    endDate: endDate_example,
  } satisfies ExportAuditLogsApiV1AuditLogsExportGetRequest;

  try {
    const data = await api.exportAuditLogsApiV1AuditLogsExportGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```


## Documentation

### API Endpoints

All URIs are relative to *http://localhost*

| Class | Method | HTTP request | Description
| ----- | ------ | ------------ | -------------
*AuditApi* | [**exportAuditLogsApiV1AuditLogsExportGet**](docs/AuditApi.md#exportauditlogsapiv1auditlogsexportget) | **GET** /api/v1/audit-logs/export | Export Audit Logs
*AuditApi* | [**getAuditLogsApiV1AuditLogsGet**](docs/AuditApi.md#getauditlogsapiv1auditlogsget) | **GET** /api/v1/audit-logs | Get Audit Logs
*BatchApi* | [**batchSignApiV1BatchSignPost**](docs/BatchApi.md#batchsignapiv1batchsignpost) | **POST** /api/v1/batch/sign | Batch Sign
*BatchApi* | [**batchVerifyApiV1BatchVerifyPost**](docs/BatchApi.md#batchverifyapiv1batchverifypost) | **POST** /api/v1/batch/verify | Batch Verify
*C2PACustomAssertionsApi* | [**createSchemaApiV1EnterpriseC2paSchemasPost**](docs/C2PACustomAssertionsApi.md#createschemaapiv1enterprisec2paschemaspost) | **POST** /api/v1/enterprise/c2pa/schemas | Create Schema
*C2PACustomAssertionsApi* | [**createTemplateApiV1EnterpriseC2paTemplatesPost**](docs/C2PACustomAssertionsApi.md#createtemplateapiv1enterprisec2patemplatespost) | **POST** /api/v1/enterprise/c2pa/templates | Create Template
*C2PACustomAssertionsApi* | [**deleteSchemaApiV1EnterpriseC2paSchemasSchemaIdDelete**](docs/C2PACustomAssertionsApi.md#deleteschemaapiv1enterprisec2paschemasschemaiddelete) | **DELETE** /api/v1/enterprise/c2pa/schemas/{schema_id} | Delete Schema
*C2PACustomAssertionsApi* | [**deleteTemplateApiV1EnterpriseC2paTemplatesTemplateIdDelete**](docs/C2PACustomAssertionsApi.md#deletetemplateapiv1enterprisec2patemplatestemplateiddelete) | **DELETE** /api/v1/enterprise/c2pa/templates/{template_id} | Delete Template
*C2PACustomAssertionsApi* | [**getSchemaApiV1EnterpriseC2paSchemasSchemaIdGet**](docs/C2PACustomAssertionsApi.md#getschemaapiv1enterprisec2paschemasschemaidget) | **GET** /api/v1/enterprise/c2pa/schemas/{schema_id} | Get Schema
*C2PACustomAssertionsApi* | [**getTemplateApiV1EnterpriseC2paTemplatesTemplateIdGet**](docs/C2PACustomAssertionsApi.md#gettemplateapiv1enterprisec2patemplatestemplateidget) | **GET** /api/v1/enterprise/c2pa/templates/{template_id} | Get Template
*C2PACustomAssertionsApi* | [**listSchemasApiV1EnterpriseC2paSchemasGet**](docs/C2PACustomAssertionsApi.md#listschemasapiv1enterprisec2paschemasget) | **GET** /api/v1/enterprise/c2pa/schemas | List Schemas
*C2PACustomAssertionsApi* | [**listTemplatesApiV1EnterpriseC2paTemplatesGet**](docs/C2PACustomAssertionsApi.md#listtemplatesapiv1enterprisec2patemplatesget) | **GET** /api/v1/enterprise/c2pa/templates | List Templates
*C2PACustomAssertionsApi* | [**updateSchemaApiV1EnterpriseC2paSchemasSchemaIdPut**](docs/C2PACustomAssertionsApi.md#updateschemaapiv1enterprisec2paschemasschemaidput) | **PUT** /api/v1/enterprise/c2pa/schemas/{schema_id} | Update Schema
*C2PACustomAssertionsApi* | [**updateTemplateApiV1EnterpriseC2paTemplatesTemplateIdPut**](docs/C2PACustomAssertionsApi.md#updatetemplateapiv1enterprisec2patemplatestemplateidput) | **PUT** /api/v1/enterprise/c2pa/templates/{template_id} | Update Template
*C2PACustomAssertionsApi* | [**validateAssertionApiV1EnterpriseC2paValidatePost**](docs/C2PACustomAssertionsApi.md#validateassertionapiv1enterprisec2pavalidatepost) | **POST** /api/v1/enterprise/c2pa/validate | Validate Assertion
*ChatApi* | [**chatHealthCheckApiV1StreamChatHealthGet**](docs/ChatApi.md#chathealthcheckapiv1streamchathealthget) | **GET** /api/v1/stream/chat/health | Chat Health Check
*ChatApi* | [**openaiCompatibleChatApiV1StreamChatOpenaiCompatiblePost**](docs/ChatApi.md#openaicompatiblechatapiv1streamchatopenaicompatiblepost) | **POST** /api/v1/stream/chat/openai-compatible | Openai Compatible Chat
*CoalitionApi* | [**getCoalitionDashboardApiV1CoalitionDashboardGet**](docs/CoalitionApi.md#getcoalitiondashboardapiv1coalitiondashboardget) | **GET** /api/v1/coalition/dashboard | Get Coalition Dashboard
*CoalitionApi* | [**getCoalitionDashboardApiV1CoalitionDashboardGet_0**](docs/CoalitionApi.md#getcoalitiondashboardapiv1coalitiondashboardget_0) | **GET** /api/v1/coalition/dashboard | Get Coalition Dashboard
*CoalitionApi* | [**getContentStatsApiV1CoalitionContentStatsGet**](docs/CoalitionApi.md#getcontentstatsapiv1coalitioncontentstatsget) | **GET** /api/v1/coalition/content-stats | Get Content Stats
*CoalitionApi* | [**getContentStatsApiV1CoalitionContentStatsGet_0**](docs/CoalitionApi.md#getcontentstatsapiv1coalitioncontentstatsget_0) | **GET** /api/v1/coalition/content-stats | Get Content Stats
*CoalitionApi* | [**getEarningsHistoryApiV1CoalitionEarningsGet**](docs/CoalitionApi.md#getearningshistoryapiv1coalitionearningsget) | **GET** /api/v1/coalition/earnings | Get Earnings History
*CoalitionApi* | [**getEarningsHistoryApiV1CoalitionEarningsGet_0**](docs/CoalitionApi.md#getearningshistoryapiv1coalitionearningsget_0) | **GET** /api/v1/coalition/earnings | Get Earnings History
*CoalitionApi* | [**optInToCoalitionApiV1CoalitionOptInPost**](docs/CoalitionApi.md#optintocoalitionapiv1coalitionoptinpost) | **POST** /api/v1/coalition/opt-in | Opt In To Coalition
*CoalitionApi* | [**optInToCoalitionApiV1CoalitionOptInPost_0**](docs/CoalitionApi.md#optintocoalitionapiv1coalitionoptinpost_0) | **POST** /api/v1/coalition/opt-in | Opt In To Coalition
*CoalitionApi* | [**optOutOfCoalitionApiV1CoalitionOptOutPost**](docs/CoalitionApi.md#optoutofcoalitionapiv1coalitionoptoutpost) | **POST** /api/v1/coalition/opt-out | Opt Out Of Coalition
*CoalitionApi* | [**optOutOfCoalitionApiV1CoalitionOptOutPost_0**](docs/CoalitionApi.md#optoutofcoalitionapiv1coalitionoptoutpost_0) | **POST** /api/v1/coalition/opt-out | Opt Out Of Coalition
*EnterpriseEmbeddingsApi* | [**encodeWithEmbeddingsApiV1EnterpriseEmbeddingsEncodeWithEmbeddingsPost**](docs/EnterpriseEmbeddingsApi.md#encodewithembeddingsapiv1enterpriseembeddingsencodewithembeddingspost) | **POST** /api/v1/enterprise/embeddings/encode-with-embeddings | Encode With Embeddings
*EnterpriseMerkleTreesApi* | [**detectPlagiarismApiV1EnterpriseMerkleDetectPlagiarismPost**](docs/EnterpriseMerkleTreesApi.md#detectplagiarismapiv1enterprisemerkledetectplagiarismpost) | **POST** /api/v1/enterprise/merkle/detect-plagiarism | Detect Plagiarism
*EnterpriseMerkleTreesApi* | [**encodeDocumentApiV1EnterpriseMerkleEncodePost**](docs/EnterpriseMerkleTreesApi.md#encodedocumentapiv1enterprisemerkleencodepost) | **POST** /api/v1/enterprise/merkle/encode | Encode Document into Merkle Trees
*EnterpriseMerkleTreesApi* | [**findSourcesApiV1EnterpriseMerkleAttributePost**](docs/EnterpriseMerkleTreesApi.md#findsourcesapiv1enterprisemerkleattributepost) | **POST** /api/v1/enterprise/merkle/attribute | Find Source Documents
*HealthApi* | [**healthCheckHealthGet**](docs/HealthApi.md#healthcheckhealthget) | **GET** /health | Health Check
*HealthApi* | [**readinessCheckReadyzGet**](docs/HealthApi.md#readinesscheckreadyzget) | **GET** /readyz | Readiness Check
*InfoApi* | [**rootGet**](docs/InfoApi.md#rootget) | **GET** / | Root
*LicensingApi* | [**createAgreementApiV1LicensingAgreementsPost**](docs/LicensingApi.md#createagreementapiv1licensingagreementspost) | **POST** /api/v1/licensing/agreements | Create Agreement
*LicensingApi* | [**createAgreementApiV1LicensingAgreementsPost_0**](docs/LicensingApi.md#createagreementapiv1licensingagreementspost_0) | **POST** /api/v1/licensing/agreements | Create Agreement
*LicensingApi* | [**createRevenueDistributionApiV1LicensingDistributionsPost**](docs/LicensingApi.md#createrevenuedistributionapiv1licensingdistributionspost) | **POST** /api/v1/licensing/distributions | Create Revenue Distribution
*LicensingApi* | [**createRevenueDistributionApiV1LicensingDistributionsPost_0**](docs/LicensingApi.md#createrevenuedistributionapiv1licensingdistributionspost_0) | **POST** /api/v1/licensing/distributions | Create Revenue Distribution
*LicensingApi* | [**getAgreementApiV1LicensingAgreementsAgreementIdGet**](docs/LicensingApi.md#getagreementapiv1licensingagreementsagreementidget) | **GET** /api/v1/licensing/agreements/{agreement_id} | Get Agreement
*LicensingApi* | [**getAgreementApiV1LicensingAgreementsAgreementIdGet_0**](docs/LicensingApi.md#getagreementapiv1licensingagreementsagreementidget_0) | **GET** /api/v1/licensing/agreements/{agreement_id} | Get Agreement
*LicensingApi* | [**getDistributionApiV1LicensingDistributionsDistributionIdGet**](docs/LicensingApi.md#getdistributionapiv1licensingdistributionsdistributionidget) | **GET** /api/v1/licensing/distributions/{distribution_id} | Get Distribution
*LicensingApi* | [**getDistributionApiV1LicensingDistributionsDistributionIdGet_0**](docs/LicensingApi.md#getdistributionapiv1licensingdistributionsdistributionidget_0) | **GET** /api/v1/licensing/distributions/{distribution_id} | Get Distribution
*LicensingApi* | [**listAgreementsApiV1LicensingAgreementsGet**](docs/LicensingApi.md#listagreementsapiv1licensingagreementsget) | **GET** /api/v1/licensing/agreements | List Agreements
*LicensingApi* | [**listAgreementsApiV1LicensingAgreementsGet_0**](docs/LicensingApi.md#listagreementsapiv1licensingagreementsget_0) | **GET** /api/v1/licensing/agreements | List Agreements
*LicensingApi* | [**listAvailableContentApiV1LicensingContentGet**](docs/LicensingApi.md#listavailablecontentapiv1licensingcontentget) | **GET** /api/v1/licensing/content | List Available Content
*LicensingApi* | [**listAvailableContentApiV1LicensingContentGet_0**](docs/LicensingApi.md#listavailablecontentapiv1licensingcontentget_0) | **GET** /api/v1/licensing/content | List Available Content
*LicensingApi* | [**listDistributionsApiV1LicensingDistributionsGet**](docs/LicensingApi.md#listdistributionsapiv1licensingdistributionsget) | **GET** /api/v1/licensing/distributions | List Distributions
*LicensingApi* | [**listDistributionsApiV1LicensingDistributionsGet_0**](docs/LicensingApi.md#listdistributionsapiv1licensingdistributionsget_0) | **GET** /api/v1/licensing/distributions | List Distributions
*LicensingApi* | [**processPayoutsApiV1LicensingPayoutsPost**](docs/LicensingApi.md#processpayoutsapiv1licensingpayoutspost) | **POST** /api/v1/licensing/payouts | Process Payouts
*LicensingApi* | [**processPayoutsApiV1LicensingPayoutsPost_0**](docs/LicensingApi.md#processpayoutsapiv1licensingpayoutspost_0) | **POST** /api/v1/licensing/payouts | Process Payouts
*LicensingApi* | [**terminateAgreementApiV1LicensingAgreementsAgreementIdDelete**](docs/LicensingApi.md#terminateagreementapiv1licensingagreementsagreementiddelete) | **DELETE** /api/v1/licensing/agreements/{agreement_id} | Terminate Agreement
*LicensingApi* | [**terminateAgreementApiV1LicensingAgreementsAgreementIdDelete_0**](docs/LicensingApi.md#terminateagreementapiv1licensingagreementsagreementiddelete_0) | **DELETE** /api/v1/licensing/agreements/{agreement_id} | Terminate Agreement
*LicensingApi* | [**trackContentAccessApiV1LicensingTrackAccessPost**](docs/LicensingApi.md#trackcontentaccessapiv1licensingtrackaccesspost) | **POST** /api/v1/licensing/track-access | Track Content Access
*LicensingApi* | [**trackContentAccessApiV1LicensingTrackAccessPost_0**](docs/LicensingApi.md#trackcontentaccessapiv1licensingtrackaccesspost_0) | **POST** /api/v1/licensing/track-access | Track Content Access
*LicensingApi* | [**updateAgreementApiV1LicensingAgreementsAgreementIdPatch**](docs/LicensingApi.md#updateagreementapiv1licensingagreementsagreementidpatch) | **PATCH** /api/v1/licensing/agreements/{agreement_id} | Update Agreement
*LicensingApi* | [**updateAgreementApiV1LicensingAgreementsAgreementIdPatch_0**](docs/LicensingApi.md#updateagreementapiv1licensingagreementsagreementidpatch_0) | **PATCH** /api/v1/licensing/agreements/{agreement_id} | Update Agreement
*LookupApi* | [**lookupSentenceApiV1LookupPost**](docs/LookupApi.md#lookupsentenceapiv1lookuppost) | **POST** /api/v1/lookup | Lookup Sentence
*OnboardingApi* | [**getCertificateStatusApiV1OnboardingCertificateStatusGet**](docs/OnboardingApi.md#getcertificatestatusapiv1onboardingcertificatestatusget) | **GET** /api/v1/onboarding/certificate-status | Get Certificate Status
*OnboardingApi* | [**requestCertificateApiV1OnboardingRequestCertificatePost**](docs/OnboardingApi.md#requestcertificateapiv1onboardingrequestcertificatepost) | **POST** /api/v1/onboarding/request-certificate | Request Certificate
*ProvisioningApi* | [**autoProvisionApiV1ProvisioningAutoProvisionPost**](docs/ProvisioningApi.md#autoprovisionapiv1provisioningautoprovisionpost) | **POST** /api/v1/provisioning/auto-provision | Auto-provision Organization and API Key
*ProvisioningApi* | [**createApiKeyApiV1ProvisioningApiKeysPost**](docs/ProvisioningApi.md#createapikeyapiv1provisioningapikeyspost) | **POST** /api/v1/provisioning/api-keys | Create API Key
*ProvisioningApi* | [**createUserAccountApiV1ProvisioningUsersPost**](docs/ProvisioningApi.md#createuseraccountapiv1provisioninguserspost) | **POST** /api/v1/provisioning/users | Create User Account
*ProvisioningApi* | [**listApiKeysApiV1ProvisioningApiKeysGet**](docs/ProvisioningApi.md#listapikeysapiv1provisioningapikeysget) | **GET** /api/v1/provisioning/api-keys | List API Keys
*ProvisioningApi* | [**provisioningHealthApiV1ProvisioningHealthGet**](docs/ProvisioningApi.md#provisioninghealthapiv1provisioninghealthget) | **GET** /api/v1/provisioning/health | Provisioning Service Health
*ProvisioningApi* | [**revokeApiKeyApiV1ProvisioningApiKeysKeyIdDelete**](docs/ProvisioningApi.md#revokeapikeyapiv1provisioningapikeyskeyiddelete) | **DELETE** /api/v1/provisioning/api-keys/{key_id} | Revoke API Key
*PublicToolsApi* | [**decodeTextApiV1ToolsDecodePost**](docs/PublicToolsApi.md#decodetextapiv1toolsdecodepost) | **POST** /api/v1/tools/decode | Decode Text
*PublicToolsApi* | [**decodeTextApiV1ToolsDecodePost_0**](docs/PublicToolsApi.md#decodetextapiv1toolsdecodepost_0) | **POST** /api/v1/tools/decode | Decode Text
*PublicToolsApi* | [**encodeTextApiV1ToolsEncodePost**](docs/PublicToolsApi.md#encodetextapiv1toolsencodepost) | **POST** /api/v1/tools/encode | Encode Text
*PublicToolsApi* | [**encodeTextApiV1ToolsEncodePost_0**](docs/PublicToolsApi.md#encodetextapiv1toolsencodepost_0) | **POST** /api/v1/tools/encode | Encode Text
*PublicVerificationApi* | [**batchVerifyEmbeddingsApiV1PublicVerifyBatchPost**](docs/PublicVerificationApi.md#batchverifyembeddingsapiv1publicverifybatchpost) | **POST** /api/v1/public/verify/batch | Batch Verify Embeddings (Public - No Auth Required)
*PublicVerificationApi* | [**extractAndVerifyEmbeddingApiV1PublicExtractAndVerifyPost**](docs/PublicVerificationApi.md#extractandverifyembeddingapiv1publicextractandverifypost) | **POST** /api/v1/public/extract-and-verify | Extract and Verify Invisible Embedding (Public - No Auth Required)
*PublicVerificationApi* | [**verifyEmbeddingApiV1PublicVerifyRefIdGet**](docs/PublicVerificationApi.md#verifyembeddingapiv1publicverifyrefidget) | **GET** /api/v1/public/verify/{ref_id} | Verify Embedding (Public - No Auth Required)
*SigningApi* | [**signContentApiV1SignPost**](docs/SigningApi.md#signcontentapiv1signpost) | **POST** /api/v1/sign | Sign Content
*StatusRevocationApi* | [**getDocumentStatusApiV1StatusDocumentsDocumentIdGet**](docs/StatusRevocationApi.md#getdocumentstatusapiv1statusdocumentsdocumentidget) | **GET** /api/v1/status/documents/{document_id} | Get Document Status
*StatusRevocationApi* | [**getDocumentStatusApiV1StatusDocumentsDocumentIdGet_0**](docs/StatusRevocationApi.md#getdocumentstatusapiv1statusdocumentsdocumentidget_0) | **GET** /api/v1/status/documents/{document_id} | Get Document Status
*StatusRevocationApi* | [**getStatusListApiV1StatusListOrganizationIdListIndexGet**](docs/StatusRevocationApi.md#getstatuslistapiv1statuslistorganizationidlistindexget) | **GET** /api/v1/status/list/{organization_id}/{list_index} | Get Status List
*StatusRevocationApi* | [**getStatusListApiV1StatusListOrganizationIdListIndexGet_0**](docs/StatusRevocationApi.md#getstatuslistapiv1statuslistorganizationidlistindexget_0) | **GET** /api/v1/status/list/{organization_id}/{list_index} | Get Status List
*StatusRevocationApi* | [**getStatusStatsApiV1StatusStatsGet**](docs/StatusRevocationApi.md#getstatusstatsapiv1statusstatsget) | **GET** /api/v1/status/stats | Get Status Stats
*StatusRevocationApi* | [**getStatusStatsApiV1StatusStatsGet_0**](docs/StatusRevocationApi.md#getstatusstatsapiv1statusstatsget_0) | **GET** /api/v1/status/stats | Get Status Stats
*StatusRevocationApi* | [**reinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost**](docs/StatusRevocationApi.md#reinstatedocumentapiv1statusdocumentsdocumentidreinstatepost) | **POST** /api/v1/status/documents/{document_id}/reinstate | Reinstate Document
*StatusRevocationApi* | [**reinstateDocumentApiV1StatusDocumentsDocumentIdReinstatePost_0**](docs/StatusRevocationApi.md#reinstatedocumentapiv1statusdocumentsdocumentidreinstatepost_0) | **POST** /api/v1/status/documents/{document_id}/reinstate | Reinstate Document
*StatusRevocationApi* | [**revokeDocumentApiV1StatusDocumentsDocumentIdRevokePost**](docs/StatusRevocationApi.md#revokedocumentapiv1statusdocumentsdocumentidrevokepost) | **POST** /api/v1/status/documents/{document_id}/revoke | Revoke Document
*StatusRevocationApi* | [**revokeDocumentApiV1StatusDocumentsDocumentIdRevokePost_0**](docs/StatusRevocationApi.md#revokedocumentapiv1statusdocumentsdocumentidrevokepost_0) | **POST** /api/v1/status/documents/{document_id}/revoke | Revoke Document
*StreamingApi* | [**closeStreamingSessionApiV1StreamSessionSessionIdClosePost**](docs/StreamingApi.md#closestreamingsessionapiv1streamsessionsessionidclosepost) | **POST** /api/v1/stream/session/{session_id}/close | Close Streaming Session
*StreamingApi* | [**createStreamingSessionApiV1StreamSessionCreatePost**](docs/StreamingApi.md#createstreamingsessionapiv1streamsessioncreatepost) | **POST** /api/v1/stream/session/create | Create Streaming Session
*StreamingApi* | [**getStreamRunApiV1StreamRunsRunIdGet**](docs/StreamingApi.md#getstreamrunapiv1streamrunsrunidget) | **GET** /api/v1/stream/runs/{run_id} | Get Stream Run
*StreamingApi* | [**getStreamingStatsApiV1StreamStatsGet**](docs/StreamingApi.md#getstreamingstatsapiv1streamstatsget) | **GET** /api/v1/stream/stats | Get Streaming Stats
*StreamingApi* | [**sseEventsEndpointApiV1StreamEventsGet**](docs/StreamingApi.md#sseeventsendpointapiv1streameventsget) | **GET** /api/v1/stream/events | Sse Events Endpoint
*StreamingApi* | [**streamSigningApiV1StreamSignPost**](docs/StreamingApi.md#streamsigningapiv1streamsignpost) | **POST** /api/v1/stream/sign | Stream Signing
*StreamingApi* | [**streamingHealthCheckApiV1StreamHealthGet**](docs/StreamingApi.md#streaminghealthcheckapiv1streamhealthget) | **GET** /api/v1/stream/health | Streaming Health Check
*TeamManagementApi* | [**acceptInviteApiV1OrgMembersAcceptInvitePost**](docs/TeamManagementApi.md#acceptinviteapiv1orgmembersacceptinvitepost) | **POST** /api/v1/org/members/accept-invite | Accept Invite
*TeamManagementApi* | [**acceptInviteApiV1OrgMembersAcceptInvitePost_0**](docs/TeamManagementApi.md#acceptinviteapiv1orgmembersacceptinvitepost_0) | **POST** /api/v1/org/members/accept-invite | Accept Invite
*TeamManagementApi* | [**inviteMemberApiV1OrgMembersInvitePost**](docs/TeamManagementApi.md#invitememberapiv1orgmembersinvitepost) | **POST** /api/v1/org/members/invite | Invite Member
*TeamManagementApi* | [**inviteMemberApiV1OrgMembersInvitePost_0**](docs/TeamManagementApi.md#invitememberapiv1orgmembersinvitepost_0) | **POST** /api/v1/org/members/invite | Invite Member
*TeamManagementApi* | [**listPendingInvitesApiV1OrgMembersInvitesGet**](docs/TeamManagementApi.md#listpendinginvitesapiv1orgmembersinvitesget) | **GET** /api/v1/org/members/invites | List Pending Invites
*TeamManagementApi* | [**listPendingInvitesApiV1OrgMembersInvitesGet_0**](docs/TeamManagementApi.md#listpendinginvitesapiv1orgmembersinvitesget_0) | **GET** /api/v1/org/members/invites | List Pending Invites
*TeamManagementApi* | [**listTeamMembersApiV1OrgMembersGet**](docs/TeamManagementApi.md#listteammembersapiv1orgmembersget) | **GET** /api/v1/org/members | List Team Members
*TeamManagementApi* | [**listTeamMembersApiV1OrgMembersGet_0**](docs/TeamManagementApi.md#listteammembersapiv1orgmembersget_0) | **GET** /api/v1/org/members | List Team Members
*TeamManagementApi* | [**removeMemberApiV1OrgMembersMemberIdDelete**](docs/TeamManagementApi.md#removememberapiv1orgmembersmemberiddelete) | **DELETE** /api/v1/org/members/{member_id} | Remove Member
*TeamManagementApi* | [**removeMemberApiV1OrgMembersMemberIdDelete_0**](docs/TeamManagementApi.md#removememberapiv1orgmembersmemberiddelete_0) | **DELETE** /api/v1/org/members/{member_id} | Remove Member
*TeamManagementApi* | [**revokeInviteApiV1OrgMembersInvitesInviteIdDelete**](docs/TeamManagementApi.md#revokeinviteapiv1orgmembersinvitesinviteiddelete) | **DELETE** /api/v1/org/members/invites/{invite_id} | Revoke Invite
*TeamManagementApi* | [**revokeInviteApiV1OrgMembersInvitesInviteIdDelete_0**](docs/TeamManagementApi.md#revokeinviteapiv1orgmembersinvitesinviteiddelete_0) | **DELETE** /api/v1/org/members/invites/{invite_id} | Revoke Invite
*TeamManagementApi* | [**updateMemberRoleApiV1OrgMembersMemberIdRolePatch**](docs/TeamManagementApi.md#updatememberroleapiv1orgmembersmemberidrolepatch) | **PATCH** /api/v1/org/members/{member_id}/role | Update Member Role
*TeamManagementApi* | [**updateMemberRoleApiV1OrgMembersMemberIdRolePatch_0**](docs/TeamManagementApi.md#updatememberroleapiv1orgmembersmemberidrolepatch_0) | **PATCH** /api/v1/org/members/{member_id}/role | Update Member Role
*UsageApi* | [**getUsageHistoryApiV1UsageHistoryGet**](docs/UsageApi.md#getusagehistoryapiv1usagehistoryget) | **GET** /api/v1/usage/history | Get Usage History
*UsageApi* | [**getUsageStatsApiV1UsageGet**](docs/UsageApi.md#getusagestatsapiv1usageget) | **GET** /api/v1/usage | Get Usage Stats
*UsageApi* | [**resetMonthlyUsageApiV1UsageResetPost**](docs/UsageApi.md#resetmonthlyusageapiv1usageresetpost) | **POST** /api/v1/usage/reset | Reset Monthly Usage
*VerificationApi* | [**verifyByDocumentIdApiV1VerifyDocumentIdGet**](docs/VerificationApi.md#verifybydocumentidapiv1verifydocumentidget) | **GET** /api/v1/verify/{document_id} | Verify By Document Id
*VerificationApi* | [**verifyContentApiV1VerifyPost**](docs/VerificationApi.md#verifycontentapiv1verifypost) | **POST** /api/v1/verify | Verify Content


### Models

- [APIKeyCreateRequest](docs/APIKeyCreateRequest.md)
- [APIKeyListResponse](docs/APIKeyListResponse.md)
- [APIKeyResponse](docs/APIKeyResponse.md)
- [APIKeyRevokeRequest](docs/APIKeyRevokeRequest.md)
- [AgreementStatus](docs/AgreementStatus.md)
- [AgreementType](docs/AgreementType.md)
- [AppModelsResponseModelsVerifyVerdict](docs/AppModelsResponseModelsVerifyVerdict.md)
- [AppRoutersToolsVerifyVerdict](docs/AppRoutersToolsVerifyVerdict.md)
- [AppSchemasBatchBatchVerifyRequest](docs/AppSchemasBatchBatchVerifyRequest.md)
- [AppSchemasEmbeddingsBatchVerifyRequest](docs/AppSchemasEmbeddingsBatchVerifyRequest.md)
- [AppSchemasEmbeddingsErrorResponse](docs/AppSchemasEmbeddingsErrorResponse.md)
- [AppSchemasMerkleErrorResponse](docs/AppSchemasMerkleErrorResponse.md)
- [AuditLogEntry](docs/AuditLogEntry.md)
- [AuditLogResponse](docs/AuditLogResponse.md)
- [AutoProvisionRequest](docs/AutoProvisionRequest.md)
- [AutoProvisionResponse](docs/AutoProvisionResponse.md)
- [BatchItemPayload](docs/BatchItemPayload.md)
- [BatchItemResult](docs/BatchItemResult.md)
- [BatchResponseData](docs/BatchResponseData.md)
- [BatchResponseEnvelope](docs/BatchResponseEnvelope.md)
- [BatchSignRequest](docs/BatchSignRequest.md)
- [BatchSummary](docs/BatchSummary.md)
- [BatchVerifyResponse](docs/BatchVerifyResponse.md)
- [BatchVerifyResult](docs/BatchVerifyResult.md)
- [BodyCreateStreamingSessionApiV1StreamSessionCreatePost](docs/BodyCreateStreamingSessionApiV1StreamSessionCreatePost.md)
- [C2PAAssertionValidateRequest](docs/C2PAAssertionValidateRequest.md)
- [C2PAAssertionValidateResponse](docs/C2PAAssertionValidateResponse.md)
- [C2PAAssertionValidationResult](docs/C2PAAssertionValidationResult.md)
- [C2PAInfo](docs/C2PAInfo.md)
- [C2PASchemaCreate](docs/C2PASchemaCreate.md)
- [C2PASchemaListResponse](docs/C2PASchemaListResponse.md)
- [C2PASchemaResponse](docs/C2PASchemaResponse.md)
- [C2PASchemaUpdate](docs/C2PASchemaUpdate.md)
- [C2PATemplateCreate](docs/C2PATemplateCreate.md)
- [C2PATemplateListResponse](docs/C2PATemplateListResponse.md)
- [C2PATemplateResponse](docs/C2PATemplateResponse.md)
- [C2PATemplateUpdate](docs/C2PATemplateUpdate.md)
- [ChatCompletionRequest](docs/ChatCompletionRequest.md)
- [ChatMessage](docs/ChatMessage.md)
- [CoalitionDashboardResponse](docs/CoalitionDashboardResponse.md)
- [ContentAccessLogResponse](docs/ContentAccessLogResponse.md)
- [ContentAccessTrack](docs/ContentAccessTrack.md)
- [ContentInfo](docs/ContentInfo.md)
- [ContentListResponse](docs/ContentListResponse.md)
- [ContentMetadata](docs/ContentMetadata.md)
- [ContentStats](docs/ContentStats.md)
- [DecodeToolRequest](docs/DecodeToolRequest.md)
- [DecodeToolResponse](docs/DecodeToolResponse.md)
- [DistributionStatus](docs/DistributionStatus.md)
- [DocumentEncodeRequest](docs/DocumentEncodeRequest.md)
- [DocumentEncodeResponse](docs/DocumentEncodeResponse.md)
- [DocumentInfo](docs/DocumentInfo.md)
- [DocumentStatusResponse](docs/DocumentStatusResponse.md)
- [EarningsSummary](docs/EarningsSummary.md)
- [EmbeddingInfo](docs/EmbeddingInfo.md)
- [EmbeddingOptions](docs/EmbeddingOptions.md)
- [EncodeToolRequest](docs/EncodeToolRequest.md)
- [EncodeToolResponse](docs/EncodeToolResponse.md)
- [EncodeWithEmbeddingsRequest](docs/EncodeWithEmbeddingsRequest.md)
- [EncodeWithEmbeddingsResponse](docs/EncodeWithEmbeddingsResponse.md)
- [ErrorDetail](docs/ErrorDetail.md)
- [ExtractAndVerifyRequest](docs/ExtractAndVerifyRequest.md)
- [ExtractAndVerifyResponse](docs/ExtractAndVerifyResponse.md)
- [HTTPValidationError](docs/HTTPValidationError.md)
- [HeatMapData](docs/HeatMapData.md)
- [InviteRequest](docs/InviteRequest.md)
- [InviteResponse](docs/InviteResponse.md)
- [LicenseInfo](docs/LicenseInfo.md)
- [LicensingAgreementCreate](docs/LicensingAgreementCreate.md)
- [LicensingAgreementCreateResponse](docs/LicensingAgreementCreateResponse.md)
- [LicensingAgreementResponse](docs/LicensingAgreementResponse.md)
- [LicensingAgreementUpdate](docs/LicensingAgreementUpdate.md)
- [LicensingInfo](docs/LicensingInfo.md)
- [LookupRequest](docs/LookupRequest.md)
- [LookupResponse](docs/LookupResponse.md)
- [MemberRevenueDetail](docs/MemberRevenueDetail.md)
- [MerkleProofInfo](docs/MerkleProofInfo.md)
- [MerkleRootResponse](docs/MerkleRootResponse.md)
- [MerkleTreeInfo](docs/MerkleTreeInfo.md)
- [PayoutCreate](docs/PayoutCreate.md)
- [PayoutResponse](docs/PayoutResponse.md)
- [PayoutStatus](docs/PayoutStatus.md)
- [PayoutSummary](docs/PayoutSummary.md)
- [PendingInvite](docs/PendingInvite.md)
- [PlagiarismDetectionRequest](docs/PlagiarismDetectionRequest.md)
- [PlagiarismDetectionResponse](docs/PlagiarismDetectionResponse.md)
- [RevenueDistributionCreate](docs/RevenueDistributionCreate.md)
- [RevenueDistributionResponse](docs/RevenueDistributionResponse.md)
- [RevocationReason](docs/RevocationReason.md)
- [RevocationResponse](docs/RevocationResponse.md)
- [RevokeRequest](docs/RevokeRequest.md)
- [SignRequest](docs/SignRequest.md)
- [SignResponse](docs/SignResponse.md)
- [SourceAttributionRequest](docs/SourceAttributionRequest.md)
- [SourceAttributionResponse](docs/SourceAttributionResponse.md)
- [SourceDocumentMatch](docs/SourceDocumentMatch.md)
- [SourceMatch](docs/SourceMatch.md)
- [StreamSignRequest](docs/StreamSignRequest.md)
- [SuccessResponse](docs/SuccessResponse.md)
- [TeamMember](docs/TeamMember.md)
- [TeamMemberListResponse](docs/TeamMemberListResponse.md)
- [TeamRole](docs/TeamRole.md)
- [TotalValue](docs/TotalValue.md)
- [TotalValue1](docs/TotalValue1.md)
- [UpdateRoleRequest](docs/UpdateRoleRequest.md)
- [UsageMetric](docs/UsageMetric.md)
- [UsageResetResponse](docs/UsageResetResponse.md)
- [UsageResponse](docs/UsageResponse.md)
- [UserAccountCreateRequest](docs/UserAccountCreateRequest.md)
- [UserAccountResponse](docs/UserAccountResponse.md)
- [ValidationError](docs/ValidationError.md)
- [ValidationErrorLocInner](docs/ValidationErrorLocInner.md)
- [VerifyEmbeddingRequest](docs/VerifyEmbeddingRequest.md)
- [VerifyEmbeddingResponse](docs/VerifyEmbeddingResponse.md)
- [VerifyRequest](docs/VerifyRequest.md)
- [VerifyResponse](docs/VerifyResponse.md)

### Authorization


Authentication schemes defined for the API:
<a id="HTTPBearer"></a>
#### HTTPBearer


- **Type**: HTTP Bearer Token authentication

## About

This TypeScript SDK client supports the [Fetch API](https://fetch.spec.whatwg.org/)
and is automatically generated by the
[OpenAPI Generator](https://openapi-generator.tech) project:

- API version: `1.0.0-preview`
- Package version: `1.0.0-alpha.1`
- Generator version: `7.17.0`
- Build package: `org.openapitools.codegen.languages.TypeScriptFetchClientCodegen`

The generated npm module supports the following:

- Environments
  * Node.js
  * Webpack
  * Browserify
- Language levels
  * ES5 - you must have a Promises/A+ library installed
  * ES6
- Module systems
  * CommonJS
  * ES6 module system


## Development

### Building

To build the TypeScript source code, you need to have Node.js and npm installed.
After cloning the repository, navigate to the project directory and run:

```bash
npm install
npm run build
```

### Publishing

Once you've built the package, you can publish it to npm:

```bash
npm publish
```

## License

[]()
