# @encypher/sdk@1.0.0-alpha.1

A TypeScript SDK client for the api.encypherai.com API.

## Usage

First, install the SDK from npm.

```bash
npm install @encypher/sdk --save
```

Next, try it out.


```ts
import {
  Configuration,
  APIKeysApi,
} from '@encypher/sdk';
import type { CreateKeyApiV1KeysPostRequest } from '@encypher/sdk';

async function example() {
  console.log("🚀 Testing @encypher/sdk SDK...");
  const config = new Configuration({ 
    // Configure HTTP bearer authorization: HTTPBearer
    accessToken: "YOUR BEARER TOKEN",
  });
  const api = new APIKeysApi(config);

  const body = {
    // KeyCreateRequest
    keyCreateRequest: ...,
  } satisfies CreateKeyApiV1KeysPostRequest;

  try {
    const data = await api.createKeyApiV1KeysPost(body);
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

All URIs are relative to *https://api.encypherai.com*

| Class | Method | HTTP request | Description
| ----- | ------ | ------------ | -------------
*APIKeysApi* | [**createKeyApiV1KeysPost**](docs/APIKeysApi.md#createkeyapiv1keyspost) | **POST** /api/v1/keys | Create Key
*APIKeysApi* | [**createKeyApiV1KeysPost_0**](docs/APIKeysApi.md#createkeyapiv1keyspost_0) | **POST** /api/v1/keys | Create Key
*APIKeysApi* | [**listKeysApiV1KeysGet**](docs/APIKeysApi.md#listkeysapiv1keysget) | **GET** /api/v1/keys | List Keys
*APIKeysApi* | [**listKeysApiV1KeysGet_0**](docs/APIKeysApi.md#listkeysapiv1keysget_0) | **GET** /api/v1/keys | List Keys
*APIKeysApi* | [**revokeKeyApiV1KeysKeyIdDelete**](docs/APIKeysApi.md#revokekeyapiv1keyskeyiddelete) | **DELETE** /api/v1/keys/{key_id} | Revoke Key
*APIKeysApi* | [**revokeKeyApiV1KeysKeyIdDelete_0**](docs/APIKeysApi.md#revokekeyapiv1keyskeyiddelete_0) | **DELETE** /api/v1/keys/{key_id} | Revoke Key
*APIKeysApi* | [**rotateKeyApiV1KeysKeyIdRotatePost**](docs/APIKeysApi.md#rotatekeyapiv1keyskeyidrotatepost) | **POST** /api/v1/keys/{key_id}/rotate | Rotate Key
*APIKeysApi* | [**rotateKeyApiV1KeysKeyIdRotatePost_0**](docs/APIKeysApi.md#rotatekeyapiv1keyskeyidrotatepost_0) | **POST** /api/v1/keys/{key_id}/rotate | Rotate Key
*APIKeysApi* | [**updateKeyApiV1KeysKeyIdPatch**](docs/APIKeysApi.md#updatekeyapiv1keyskeyidpatch) | **PATCH** /api/v1/keys/{key_id} | Update Key
*APIKeysApi* | [**updateKeyApiV1KeysKeyIdPatch_0**](docs/APIKeysApi.md#updatekeyapiv1keyskeyidpatch_0) | **PATCH** /api/v1/keys/{key_id} | Update Key
*AccountApi* | [**getAccountInfoApiV1AccountGet**](docs/AccountApi.md#getaccountinfoapiv1accountget) | **GET** /api/v1/account | Get Account Info
*AccountApi* | [**getAccountInfoApiV1AccountGet_0**](docs/AccountApi.md#getaccountinfoapiv1accountget_0) | **GET** /api/v1/account | Get Account Info
*AccountApi* | [**getAccountQuotaApiV1AccountQuotaGet**](docs/AccountApi.md#getaccountquotaapiv1accountquotaget) | **GET** /api/v1/account/quota | Get Account Quota
*AccountApi* | [**getAccountQuotaApiV1AccountQuotaGet_0**](docs/AccountApi.md#getaccountquotaapiv1accountquotaget_0) | **GET** /api/v1/account/quota | Get Account Quota
*BYOKApi* | [**listPublicKeysApiV1ByokPublicKeysGet**](docs/BYOKApi.md#listpublickeysapiv1byokpublickeysget) | **GET** /api/v1/byok/public-keys | List public keys
*BYOKApi* | [**listPublicKeysApiV1ByokPublicKeysGet_0**](docs/BYOKApi.md#listpublickeysapiv1byokpublickeysget_0) | **GET** /api/v1/byok/public-keys | List public keys
*BYOKApi* | [**registerPublicKeyApiV1ByokPublicKeysPost**](docs/BYOKApi.md#registerpublickeyapiv1byokpublickeyspost) | **POST** /api/v1/byok/public-keys | Register a public key
*BYOKApi* | [**registerPublicKeyApiV1ByokPublicKeysPost_0**](docs/BYOKApi.md#registerpublickeyapiv1byokpublickeyspost_0) | **POST** /api/v1/byok/public-keys | Register a public key
*BYOKApi* | [**revokePublicKeyApiV1ByokPublicKeysKeyIdDelete**](docs/BYOKApi.md#revokepublickeyapiv1byokpublickeyskeyiddelete) | **DELETE** /api/v1/byok/public-keys/{key_id} | Revoke a public key
*BYOKApi* | [**revokePublicKeyApiV1ByokPublicKeysKeyIdDelete_0**](docs/BYOKApi.md#revokepublickeyapiv1byokpublickeyskeyiddelete_0) | **DELETE** /api/v1/byok/public-keys/{key_id} | Revoke a public key
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
*DocumentsApi* | [**deleteDocumentApiV1DocumentsDocumentIdDelete**](docs/DocumentsApi.md#deletedocumentapiv1documentsdocumentiddelete) | **DELETE** /api/v1/documents/{document_id} | Delete Document
*DocumentsApi* | [**deleteDocumentApiV1DocumentsDocumentIdDelete_0**](docs/DocumentsApi.md#deletedocumentapiv1documentsdocumentiddelete_0) | **DELETE** /api/v1/documents/{document_id} | Delete Document
*DocumentsApi* | [**getDocumentApiV1DocumentsDocumentIdGet**](docs/DocumentsApi.md#getdocumentapiv1documentsdocumentidget) | **GET** /api/v1/documents/{document_id} | Get Document
*DocumentsApi* | [**getDocumentApiV1DocumentsDocumentIdGet_0**](docs/DocumentsApi.md#getdocumentapiv1documentsdocumentidget_0) | **GET** /api/v1/documents/{document_id} | Get Document
*DocumentsApi* | [**getDocumentHistoryApiV1DocumentsDocumentIdHistoryGet**](docs/DocumentsApi.md#getdocumenthistoryapiv1documentsdocumentidhistoryget) | **GET** /api/v1/documents/{document_id}/history | Get Document History
*DocumentsApi* | [**getDocumentHistoryApiV1DocumentsDocumentIdHistoryGet_0**](docs/DocumentsApi.md#getdocumenthistoryapiv1documentsdocumentidhistoryget_0) | **GET** /api/v1/documents/{document_id}/history | Get Document History
*DocumentsApi* | [**listDocumentsApiV1DocumentsGet**](docs/DocumentsApi.md#listdocumentsapiv1documentsget) | **GET** /api/v1/documents | List Documents
*DocumentsApi* | [**listDocumentsApiV1DocumentsGet_0**](docs/DocumentsApi.md#listdocumentsapiv1documentsget_0) | **GET** /api/v1/documents | List Documents
*EnterpriseEmbeddingsApi* | [**encodeWithEmbeddingsApiV1EnterpriseEmbeddingsEncodeWithEmbeddingsPost**](docs/EnterpriseEmbeddingsApi.md#encodewithembeddingsapiv1enterpriseembeddingsencodewithembeddingspost) | **POST** /api/v1/enterprise/embeddings/encode-with-embeddings | Encode With Embeddings
*EnterpriseEmbeddingsApi* | [**signAdvancedApiV1EnterpriseEmbeddingsSignAdvancedPost**](docs/EnterpriseEmbeddingsApi.md#signadvancedapiv1enterpriseembeddingssignadvancedpost) | **POST** /api/v1/enterprise/embeddings/sign/advanced | Sign Advanced
*EnterpriseMerkleTreesApi* | [**detectPlagiarismApiV1EnterpriseMerkleDetectPlagiarismPost**](docs/EnterpriseMerkleTreesApi.md#detectplagiarismapiv1enterprisemerkledetectplagiarismpost) | **POST** /api/v1/enterprise/merkle/detect-plagiarism | Detect Plagiarism
*EnterpriseMerkleTreesApi* | [**encodeDocumentApiV1EnterpriseMerkleEncodePost**](docs/EnterpriseMerkleTreesApi.md#encodedocumentapiv1enterprisemerkleencodepost) | **POST** /api/v1/enterprise/merkle/encode | Encode Document into Merkle Trees
*EnterpriseMerkleTreesApi* | [**findSourcesApiV1EnterpriseMerkleAttributePost**](docs/EnterpriseMerkleTreesApi.md#findsourcesapiv1enterprisemerkleattributepost) | **POST** /api/v1/enterprise/merkle/attribute | Find Source Documents
*HealthApi* | [**healthCheckHealthGet**](docs/HealthApi.md#healthcheckhealthget) | **GET** /health | Health Check
*HealthApi* | [**readinessCheckReadyzGet**](docs/HealthApi.md#readinesscheckreadyzget) | **GET** /readyz | Readiness Check
*InfoApi* | [**rootGet**](docs/InfoApi.md#rootget) | **GET** / | Root
*LookupApi* | [**lookupSentenceApiV1LookupPost**](docs/LookupApi.md#lookupsentenceapiv1lookuppost) | **POST** /api/v1/lookup | Lookup Sentence
*LookupApi* | [**provenanceLookupApiV1ProvenanceLookupPost**](docs/LookupApi.md#provenancelookupapiv1provenancelookuppost) | **POST** /api/v1/provenance/lookup | Provenance Lookup
*OnboardingApi* | [**getCertificateStatusApiV1OnboardingCertificateStatusGet**](docs/OnboardingApi.md#getcertificatestatusapiv1onboardingcertificatestatusget) | **GET** /api/v1/onboarding/certificate-status | Get Certificate Status
*OnboardingApi* | [**requestCertificateApiV1OnboardingRequestCertificatePost**](docs/OnboardingApi.md#requestcertificateapiv1onboardingrequestcertificatepost) | **POST** /api/v1/onboarding/request-certificate | Request Certificate
*PublicC2PAApi* | [**createManifestApiV1PublicC2paCreateManifestPost**](docs/PublicC2PAApi.md#createmanifestapiv1publicc2pacreatemanifestpost) | **POST** /api/v1/public/c2pa/create-manifest | Create C2PA-like manifest JSON from plaintext (Public - Non-Cryptographic)
*PublicC2PAApi* | [**getTrustAnchorApiV1PublicC2paTrustAnchorsSignerIdGet**](docs/PublicC2PAApi.md#gettrustanchorapiv1publicc2patrustanchorssigneridget) | **GET** /api/v1/public/c2pa/trust-anchors/{signer_id} | Lookup trust anchor for C2PA verification (Public)
*PublicC2PAApi* | [**validateManifestApiV1PublicC2paValidateManifestPost**](docs/PublicC2PAApi.md#validatemanifestapiv1publicc2pavalidatemanifestpost) | **POST** /api/v1/public/c2pa/validate-manifest | Validate C2PA-like manifest JSON (Public - Non-Cryptographic)
*PublicToolsApi* | [**decodeTextApiV1ToolsDecodePost**](docs/PublicToolsApi.md#decodetextapiv1toolsdecodepost) | **POST** /api/v1/tools/decode | Decode Text
*PublicToolsApi* | [**decodeTextApiV1ToolsDecodePost_0**](docs/PublicToolsApi.md#decodetextapiv1toolsdecodepost_0) | **POST** /api/v1/tools/decode | Decode Text
*PublicToolsApi* | [**encodeTextApiV1ToolsEncodePost**](docs/PublicToolsApi.md#encodetextapiv1toolsencodepost) | **POST** /api/v1/tools/encode | Encode Text
*PublicToolsApi* | [**encodeTextApiV1ToolsEncodePost_0**](docs/PublicToolsApi.md#encodetextapiv1toolsencodepost_0) | **POST** /api/v1/tools/encode | Encode Text
*PublicVerificationApi* | [**batchVerifyEmbeddingsApiV1PublicVerifyBatchPost**](docs/PublicVerificationApi.md#batchverifyembeddingsapiv1publicverifybatchpost) | **POST** /api/v1/public/verify/batch | Batch Verify Embeddings (Public - No Auth Required)
*PublicVerificationApi* | [**extractAndVerifyEmbeddingApiV1PublicExtractAndVerifyPost**](docs/PublicVerificationApi.md#extractandverifyembeddingapiv1publicextractandverifypost) | **POST** /api/v1/public/extract-and-verify | Extract and Verify Invisible Embedding (Public - No Auth Required)
*PublicVerificationApi* | [**verifyEmbeddingApiV1PublicVerifyRefIdGet**](docs/PublicVerificationApi.md#verifyembeddingapiv1publicverifyrefidget) | **GET** /api/v1/public/verify/{ref_id} | Verify Embedding (Public - No Auth Required)
*SigningApi* | [**signAdvancedApiV1SignAdvancedPost**](docs/SigningApi.md#signadvancedapiv1signadvancedpost) | **POST** /api/v1/sign/advanced | Sign Advanced
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
*UsageApi* | [**getUsageHistoryApiV1UsageHistoryGet**](docs/UsageApi.md#getusagehistoryapiv1usagehistoryget) | **GET** /api/v1/usage/history | Get Usage History
*UsageApi* | [**getUsageStatsApiV1UsageGet**](docs/UsageApi.md#getusagestatsapiv1usageget) | **GET** /api/v1/usage | Get Usage Stats
*UsageApi* | [**resetMonthlyUsageApiV1UsageResetPost**](docs/UsageApi.md#resetmonthlyusageapiv1usageresetpost) | **POST** /api/v1/usage/reset | Reset Monthly Usage
*VerificationApi* | [**verifyByDocumentIdApiV1VerifyDocumentIdGet**](docs/VerificationApi.md#verifybydocumentidapiv1verifydocumentidget) | **GET** /api/v1/verify/{document_id} | Verify By Document Id
*VerificationApi* | [**verifyContentApiV1VerifyPost**](docs/VerificationApi.md#verifycontentapiv1verifypost) | **POST** /api/v1/verify | Verify Content
*WebhooksApi* | [**createWebhookApiV1WebhooksPost**](docs/WebhooksApi.md#createwebhookapiv1webhookspost) | **POST** /api/v1/webhooks | Create Webhook
*WebhooksApi* | [**createWebhookApiV1WebhooksPost_0**](docs/WebhooksApi.md#createwebhookapiv1webhookspost_0) | **POST** /api/v1/webhooks | Create Webhook
*WebhooksApi* | [**deleteWebhookApiV1WebhooksWebhookIdDelete**](docs/WebhooksApi.md#deletewebhookapiv1webhookswebhookiddelete) | **DELETE** /api/v1/webhooks/{webhook_id} | Delete Webhook
*WebhooksApi* | [**deleteWebhookApiV1WebhooksWebhookIdDelete_0**](docs/WebhooksApi.md#deletewebhookapiv1webhookswebhookiddelete_0) | **DELETE** /api/v1/webhooks/{webhook_id} | Delete Webhook
*WebhooksApi* | [**getWebhookApiV1WebhooksWebhookIdGet**](docs/WebhooksApi.md#getwebhookapiv1webhookswebhookidget) | **GET** /api/v1/webhooks/{webhook_id} | Get Webhook
*WebhooksApi* | [**getWebhookApiV1WebhooksWebhookIdGet_0**](docs/WebhooksApi.md#getwebhookapiv1webhookswebhookidget_0) | **GET** /api/v1/webhooks/{webhook_id} | Get Webhook
*WebhooksApi* | [**getWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet**](docs/WebhooksApi.md#getwebhookdeliveriesapiv1webhookswebhookiddeliveriesget) | **GET** /api/v1/webhooks/{webhook_id}/deliveries | Get Webhook Deliveries
*WebhooksApi* | [**getWebhookDeliveriesApiV1WebhooksWebhookIdDeliveriesGet_0**](docs/WebhooksApi.md#getwebhookdeliveriesapiv1webhookswebhookiddeliveriesget_0) | **GET** /api/v1/webhooks/{webhook_id}/deliveries | Get Webhook Deliveries
*WebhooksApi* | [**listWebhooksApiV1WebhooksGet**](docs/WebhooksApi.md#listwebhooksapiv1webhooksget) | **GET** /api/v1/webhooks | List Webhooks
*WebhooksApi* | [**listWebhooksApiV1WebhooksGet_0**](docs/WebhooksApi.md#listwebhooksapiv1webhooksget_0) | **GET** /api/v1/webhooks | List Webhooks
*WebhooksApi* | [**testWebhookApiV1WebhooksWebhookIdTestPost**](docs/WebhooksApi.md#testwebhookapiv1webhookswebhookidtestpost) | **POST** /api/v1/webhooks/{webhook_id}/test | Test Webhook
*WebhooksApi* | [**testWebhookApiV1WebhooksWebhookIdTestPost_0**](docs/WebhooksApi.md#testwebhookapiv1webhookswebhookidtestpost_0) | **POST** /api/v1/webhooks/{webhook_id}/test | Test Webhook
*WebhooksApi* | [**updateWebhookApiV1WebhooksWebhookIdPatch**](docs/WebhooksApi.md#updatewebhookapiv1webhookswebhookidpatch) | **PATCH** /api/v1/webhooks/{webhook_id} | Update Webhook
*WebhooksApi* | [**updateWebhookApiV1WebhooksWebhookIdPatch_0**](docs/WebhooksApi.md#updatewebhookapiv1webhookswebhookidpatch_0) | **PATCH** /api/v1/webhooks/{webhook_id} | Update Webhook


### Models

- [AccountInfo](docs/AccountInfo.md)
- [AccountResponse](docs/AccountResponse.md)
- [AppModelsRequestModelsRightsMetadata](docs/AppModelsRequestModelsRightsMetadata.md)
- [AppModelsResponseModelsVerifyVerdict](docs/AppModelsResponseModelsVerifyVerdict.md)
- [AppRoutersToolsVerifyVerdict](docs/AppRoutersToolsVerifyVerdict.md)
- [AppSchemasBatchBatchVerifyRequest](docs/AppSchemasBatchBatchVerifyRequest.md)
- [AppSchemasEmbeddingsBatchVerifyRequest](docs/AppSchemasEmbeddingsBatchVerifyRequest.md)
- [AppSchemasEmbeddingsErrorResponse](docs/AppSchemasEmbeddingsErrorResponse.md)
- [AppSchemasEmbeddingsRightsMetadata](docs/AppSchemasEmbeddingsRightsMetadata.md)
- [AppSchemasMerkleErrorResponse](docs/AppSchemasMerkleErrorResponse.md)
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
- [ContentInfo](docs/ContentInfo.md)
- [ContentStats](docs/ContentStats.md)
- [CreateManifestRequest](docs/CreateManifestRequest.md)
- [CreateManifestResponse](docs/CreateManifestResponse.md)
- [CreateManifestSigningPayload](docs/CreateManifestSigningPayload.md)
- [DecodeToolRequest](docs/DecodeToolRequest.md)
- [DecodeToolResponse](docs/DecodeToolResponse.md)
- [DocumentDeleteResponse](docs/DocumentDeleteResponse.md)
- [DocumentDetail](docs/DocumentDetail.md)
- [DocumentDetailResponse](docs/DocumentDetailResponse.md)
- [DocumentEncodeRequest](docs/DocumentEncodeRequest.md)
- [DocumentEncodeResponse](docs/DocumentEncodeResponse.md)
- [DocumentHistoryResponse](docs/DocumentHistoryResponse.md)
- [DocumentInfo](docs/DocumentInfo.md)
- [DocumentListResponse](docs/DocumentListResponse.md)
- [DocumentStatusResponse](docs/DocumentStatusResponse.md)
- [EarningsSummary](docs/EarningsSummary.md)
- [EmbeddingInfo](docs/EmbeddingInfo.md)
- [EmbeddingOptions](docs/EmbeddingOptions.md)
- [EmbeddingResult](docs/EmbeddingResult.md)
- [EmbeddingVerdict](docs/EmbeddingVerdict.md)
- [EncodeToolRequest](docs/EncodeToolRequest.md)
- [EncodeToolResponse](docs/EncodeToolResponse.md)
- [EncodeWithEmbeddingsRequest](docs/EncodeWithEmbeddingsRequest.md)
- [EncodeWithEmbeddingsResponse](docs/EncodeWithEmbeddingsResponse.md)
- [ErrorDetail](docs/ErrorDetail.md)
- [ExtractAndVerifyRequest](docs/ExtractAndVerifyRequest.md)
- [ExtractAndVerifyResponse](docs/ExtractAndVerifyResponse.md)
- [FeatureFlags](docs/FeatureFlags.md)
- [HTTPValidationError](docs/HTTPValidationError.md)
- [HeatMapData](docs/HeatMapData.md)
- [KeyCreateRequest](docs/KeyCreateRequest.md)
- [KeyCreateResponse](docs/KeyCreateResponse.md)
- [KeyListResponse](docs/KeyListResponse.md)
- [KeyRevokeResponse](docs/KeyRevokeResponse.md)
- [KeyRotateResponse](docs/KeyRotateResponse.md)
- [KeyUpdateRequest](docs/KeyUpdateRequest.md)
- [KeyUpdateResponse](docs/KeyUpdateResponse.md)
- [LicenseInfo](docs/LicenseInfo.md)
- [LicensingInfo](docs/LicensingInfo.md)
- [LookupRequest](docs/LookupRequest.md)
- [LookupResponse](docs/LookupResponse.md)
- [MerkleProofInfo](docs/MerkleProofInfo.md)
- [MerkleRootResponse](docs/MerkleRootResponse.md)
- [MerkleTreeInfo](docs/MerkleTreeInfo.md)
- [PayoutSummary](docs/PayoutSummary.md)
- [PlagiarismDetectionRequest](docs/PlagiarismDetectionRequest.md)
- [PlagiarismDetectionResponse](docs/PlagiarismDetectionResponse.md)
- [PublicKeyInfo](docs/PublicKeyInfo.md)
- [PublicKeyListResponse](docs/PublicKeyListResponse.md)
- [PublicKeyRegisterRequest](docs/PublicKeyRegisterRequest.md)
- [PublicKeyRegisterResponse](docs/PublicKeyRegisterResponse.md)
- [QuotaInfo](docs/QuotaInfo.md)
- [QuotaMetric](docs/QuotaMetric.md)
- [QuotaResponse](docs/QuotaResponse.md)
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
- [TrustAnchorResponse](docs/TrustAnchorResponse.md)
- [UsageMetric](docs/UsageMetric.md)
- [UsageResetResponse](docs/UsageResetResponse.md)
- [UsageResponse](docs/UsageResponse.md)
- [ValidateManifestRequest](docs/ValidateManifestRequest.md)
- [ValidateManifestResponse](docs/ValidateManifestResponse.md)
- [ValidationError](docs/ValidationError.md)
- [ValidationErrorLocInner](docs/ValidationErrorLocInner.md)
- [VerifyEmbeddingRequest](docs/VerifyEmbeddingRequest.md)
- [VerifyEmbeddingResponse](docs/VerifyEmbeddingResponse.md)
- [VerifyRequest](docs/VerifyRequest.md)
- [VerifyResponse](docs/VerifyResponse.md)
- [WebhookCreateRequest](docs/WebhookCreateRequest.md)
- [WebhookCreateResponse](docs/WebhookCreateResponse.md)
- [WebhookDeleteResponse](docs/WebhookDeleteResponse.md)
- [WebhookDeliveriesResponse](docs/WebhookDeliveriesResponse.md)
- [WebhookListResponse](docs/WebhookListResponse.md)
- [WebhookTestResponse](docs/WebhookTestResponse.md)
- [WebhookUpdateRequest](docs/WebhookUpdateRequest.md)
- [WebhookUpdateResponse](docs/WebhookUpdateResponse.md)

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
