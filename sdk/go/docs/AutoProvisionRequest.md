# AutoProvisionRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Email** | **string** | User email address | 
**OrganizationName** | Pointer to **NullableString** |  | [optional] 
**Source** | **string** | Source of the provisioning request | 
**SourceMetadata** | Pointer to **map[string]interface{}** |  | [optional] 
**Tier** | Pointer to **NullableString** |  | [optional] 
**AutoActivate** | Pointer to **bool** | Whether to automatically activate the organization | [optional] [default to true]

## Methods

### NewAutoProvisionRequest

`func NewAutoProvisionRequest(email string, source string, ) *AutoProvisionRequest`

NewAutoProvisionRequest instantiates a new AutoProvisionRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewAutoProvisionRequestWithDefaults

`func NewAutoProvisionRequestWithDefaults() *AutoProvisionRequest`

NewAutoProvisionRequestWithDefaults instantiates a new AutoProvisionRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetEmail

`func (o *AutoProvisionRequest) GetEmail() string`

GetEmail returns the Email field if non-nil, zero value otherwise.

### GetEmailOk

`func (o *AutoProvisionRequest) GetEmailOk() (*string, bool)`

GetEmailOk returns a tuple with the Email field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEmail

`func (o *AutoProvisionRequest) SetEmail(v string)`

SetEmail sets Email field to given value.


### GetOrganizationName

`func (o *AutoProvisionRequest) GetOrganizationName() string`

GetOrganizationName returns the OrganizationName field if non-nil, zero value otherwise.

### GetOrganizationNameOk

`func (o *AutoProvisionRequest) GetOrganizationNameOk() (*string, bool)`

GetOrganizationNameOk returns a tuple with the OrganizationName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationName

`func (o *AutoProvisionRequest) SetOrganizationName(v string)`

SetOrganizationName sets OrganizationName field to given value.

### HasOrganizationName

`func (o *AutoProvisionRequest) HasOrganizationName() bool`

HasOrganizationName returns a boolean if a field has been set.

### SetOrganizationNameNil

`func (o *AutoProvisionRequest) SetOrganizationNameNil(b bool)`

 SetOrganizationNameNil sets the value for OrganizationName to be an explicit nil

### UnsetOrganizationName
`func (o *AutoProvisionRequest) UnsetOrganizationName()`

UnsetOrganizationName ensures that no value is present for OrganizationName, not even an explicit nil
### GetSource

`func (o *AutoProvisionRequest) GetSource() string`

GetSource returns the Source field if non-nil, zero value otherwise.

### GetSourceOk

`func (o *AutoProvisionRequest) GetSourceOk() (*string, bool)`

GetSourceOk returns a tuple with the Source field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSource

`func (o *AutoProvisionRequest) SetSource(v string)`

SetSource sets Source field to given value.


### GetSourceMetadata

`func (o *AutoProvisionRequest) GetSourceMetadata() map[string]interface{}`

GetSourceMetadata returns the SourceMetadata field if non-nil, zero value otherwise.

### GetSourceMetadataOk

`func (o *AutoProvisionRequest) GetSourceMetadataOk() (*map[string]interface{}, bool)`

GetSourceMetadataOk returns a tuple with the SourceMetadata field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSourceMetadata

`func (o *AutoProvisionRequest) SetSourceMetadata(v map[string]interface{})`

SetSourceMetadata sets SourceMetadata field to given value.

### HasSourceMetadata

`func (o *AutoProvisionRequest) HasSourceMetadata() bool`

HasSourceMetadata returns a boolean if a field has been set.

### SetSourceMetadataNil

`func (o *AutoProvisionRequest) SetSourceMetadataNil(b bool)`

 SetSourceMetadataNil sets the value for SourceMetadata to be an explicit nil

### UnsetSourceMetadata
`func (o *AutoProvisionRequest) UnsetSourceMetadata()`

UnsetSourceMetadata ensures that no value is present for SourceMetadata, not even an explicit nil
### GetTier

`func (o *AutoProvisionRequest) GetTier() string`

GetTier returns the Tier field if non-nil, zero value otherwise.

### GetTierOk

`func (o *AutoProvisionRequest) GetTierOk() (*string, bool)`

GetTierOk returns a tuple with the Tier field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTier

`func (o *AutoProvisionRequest) SetTier(v string)`

SetTier sets Tier field to given value.

### HasTier

`func (o *AutoProvisionRequest) HasTier() bool`

HasTier returns a boolean if a field has been set.

### SetTierNil

`func (o *AutoProvisionRequest) SetTierNil(b bool)`

 SetTierNil sets the value for Tier to be an explicit nil

### UnsetTier
`func (o *AutoProvisionRequest) UnsetTier()`

UnsetTier ensures that no value is present for Tier, not even an explicit nil
### GetAutoActivate

`func (o *AutoProvisionRequest) GetAutoActivate() bool`

GetAutoActivate returns the AutoActivate field if non-nil, zero value otherwise.

### GetAutoActivateOk

`func (o *AutoProvisionRequest) GetAutoActivateOk() (*bool, bool)`

GetAutoActivateOk returns a tuple with the AutoActivate field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAutoActivate

`func (o *AutoProvisionRequest) SetAutoActivate(v bool)`

SetAutoActivate sets AutoActivate field to given value.

### HasAutoActivate

`func (o *AutoProvisionRequest) HasAutoActivate() bool`

HasAutoActivate returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


