# FeatureFlags

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**MerkleEnabled** | Pointer to **bool** | Merkle tree features enabled | [optional] [default to false]
**ByokEnabled** | Pointer to **bool** | Bring Your Own Key enabled | [optional] [default to false]
**SentenceTracking** | Pointer to **bool** | Sentence-level tracking enabled | [optional] [default to false]
**BulkOperations** | Pointer to **bool** | Bulk/batch operations enabled | [optional] [default to false]
**CustomAssertions** | Pointer to **bool** | Custom C2PA assertions enabled | [optional] [default to false]
**Streaming** | Pointer to **bool** | Streaming API enabled | [optional] [default to true]
**TeamManagement** | Pointer to **bool** | Team management enabled | [optional] [default to false]
**AuditLogs** | Pointer to **bool** | Audit logs enabled | [optional] [default to false]
**Sso** | Pointer to **bool** | SSO/SAML enabled | [optional] [default to false]
**MaxTeamMembers** | Pointer to **int32** | Maximum team members allowed | [optional] [default to 1]

## Methods

### NewFeatureFlags

`func NewFeatureFlags() *FeatureFlags`

NewFeatureFlags instantiates a new FeatureFlags object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewFeatureFlagsWithDefaults

`func NewFeatureFlagsWithDefaults() *FeatureFlags`

NewFeatureFlagsWithDefaults instantiates a new FeatureFlags object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetMerkleEnabled

`func (o *FeatureFlags) GetMerkleEnabled() bool`

GetMerkleEnabled returns the MerkleEnabled field if non-nil, zero value otherwise.

### GetMerkleEnabledOk

`func (o *FeatureFlags) GetMerkleEnabledOk() (*bool, bool)`

GetMerkleEnabledOk returns a tuple with the MerkleEnabled field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMerkleEnabled

`func (o *FeatureFlags) SetMerkleEnabled(v bool)`

SetMerkleEnabled sets MerkleEnabled field to given value.

### HasMerkleEnabled

`func (o *FeatureFlags) HasMerkleEnabled() bool`

HasMerkleEnabled returns a boolean if a field has been set.

### GetByokEnabled

`func (o *FeatureFlags) GetByokEnabled() bool`

GetByokEnabled returns the ByokEnabled field if non-nil, zero value otherwise.

### GetByokEnabledOk

`func (o *FeatureFlags) GetByokEnabledOk() (*bool, bool)`

GetByokEnabledOk returns a tuple with the ByokEnabled field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetByokEnabled

`func (o *FeatureFlags) SetByokEnabled(v bool)`

SetByokEnabled sets ByokEnabled field to given value.

### HasByokEnabled

`func (o *FeatureFlags) HasByokEnabled() bool`

HasByokEnabled returns a boolean if a field has been set.

### GetSentenceTracking

`func (o *FeatureFlags) GetSentenceTracking() bool`

GetSentenceTracking returns the SentenceTracking field if non-nil, zero value otherwise.

### GetSentenceTrackingOk

`func (o *FeatureFlags) GetSentenceTrackingOk() (*bool, bool)`

GetSentenceTrackingOk returns a tuple with the SentenceTracking field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSentenceTracking

`func (o *FeatureFlags) SetSentenceTracking(v bool)`

SetSentenceTracking sets SentenceTracking field to given value.

### HasSentenceTracking

`func (o *FeatureFlags) HasSentenceTracking() bool`

HasSentenceTracking returns a boolean if a field has been set.

### GetBulkOperations

`func (o *FeatureFlags) GetBulkOperations() bool`

GetBulkOperations returns the BulkOperations field if non-nil, zero value otherwise.

### GetBulkOperationsOk

`func (o *FeatureFlags) GetBulkOperationsOk() (*bool, bool)`

GetBulkOperationsOk returns a tuple with the BulkOperations field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetBulkOperations

`func (o *FeatureFlags) SetBulkOperations(v bool)`

SetBulkOperations sets BulkOperations field to given value.

### HasBulkOperations

`func (o *FeatureFlags) HasBulkOperations() bool`

HasBulkOperations returns a boolean if a field has been set.

### GetCustomAssertions

`func (o *FeatureFlags) GetCustomAssertions() bool`

GetCustomAssertions returns the CustomAssertions field if non-nil, zero value otherwise.

### GetCustomAssertionsOk

`func (o *FeatureFlags) GetCustomAssertionsOk() (*bool, bool)`

GetCustomAssertionsOk returns a tuple with the CustomAssertions field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCustomAssertions

`func (o *FeatureFlags) SetCustomAssertions(v bool)`

SetCustomAssertions sets CustomAssertions field to given value.

### HasCustomAssertions

`func (o *FeatureFlags) HasCustomAssertions() bool`

HasCustomAssertions returns a boolean if a field has been set.

### GetStreaming

`func (o *FeatureFlags) GetStreaming() bool`

GetStreaming returns the Streaming field if non-nil, zero value otherwise.

### GetStreamingOk

`func (o *FeatureFlags) GetStreamingOk() (*bool, bool)`

GetStreamingOk returns a tuple with the Streaming field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStreaming

`func (o *FeatureFlags) SetStreaming(v bool)`

SetStreaming sets Streaming field to given value.

### HasStreaming

`func (o *FeatureFlags) HasStreaming() bool`

HasStreaming returns a boolean if a field has been set.

### GetTeamManagement

`func (o *FeatureFlags) GetTeamManagement() bool`

GetTeamManagement returns the TeamManagement field if non-nil, zero value otherwise.

### GetTeamManagementOk

`func (o *FeatureFlags) GetTeamManagementOk() (*bool, bool)`

GetTeamManagementOk returns a tuple with the TeamManagement field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTeamManagement

`func (o *FeatureFlags) SetTeamManagement(v bool)`

SetTeamManagement sets TeamManagement field to given value.

### HasTeamManagement

`func (o *FeatureFlags) HasTeamManagement() bool`

HasTeamManagement returns a boolean if a field has been set.

### GetAuditLogs

`func (o *FeatureFlags) GetAuditLogs() bool`

GetAuditLogs returns the AuditLogs field if non-nil, zero value otherwise.

### GetAuditLogsOk

`func (o *FeatureFlags) GetAuditLogsOk() (*bool, bool)`

GetAuditLogsOk returns a tuple with the AuditLogs field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAuditLogs

`func (o *FeatureFlags) SetAuditLogs(v bool)`

SetAuditLogs sets AuditLogs field to given value.

### HasAuditLogs

`func (o *FeatureFlags) HasAuditLogs() bool`

HasAuditLogs returns a boolean if a field has been set.

### GetSso

`func (o *FeatureFlags) GetSso() bool`

GetSso returns the Sso field if non-nil, zero value otherwise.

### GetSsoOk

`func (o *FeatureFlags) GetSsoOk() (*bool, bool)`

GetSsoOk returns a tuple with the Sso field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSso

`func (o *FeatureFlags) SetSso(v bool)`

SetSso sets Sso field to given value.

### HasSso

`func (o *FeatureFlags) HasSso() bool`

HasSso returns a boolean if a field has been set.

### GetMaxTeamMembers

`func (o *FeatureFlags) GetMaxTeamMembers() int32`

GetMaxTeamMembers returns the MaxTeamMembers field if non-nil, zero value otherwise.

### GetMaxTeamMembersOk

`func (o *FeatureFlags) GetMaxTeamMembersOk() (*int32, bool)`

GetMaxTeamMembersOk returns a tuple with the MaxTeamMembers field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMaxTeamMembers

`func (o *FeatureFlags) SetMaxTeamMembers(v int32)`

SetMaxTeamMembers sets MaxTeamMembers field to given value.

### HasMaxTeamMembers

`func (o *FeatureFlags) HasMaxTeamMembers() bool`

HasMaxTeamMembers returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


