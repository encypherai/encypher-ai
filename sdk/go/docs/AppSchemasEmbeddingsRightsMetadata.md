# AppSchemasEmbeddingsRightsMetadata

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**CopyrightHolder** | Pointer to **NullableString** |  | [optional] 
**LicenseUrl** | Pointer to **NullableString** |  | [optional] 
**UsageTerms** | Pointer to **NullableString** |  | [optional] 
**SyndicationAllowed** | Pointer to **NullableBool** |  | [optional] 
**EmbargoUntil** | Pointer to **NullableTime** |  | [optional] 
**ContactEmail** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewAppSchemasEmbeddingsRightsMetadata

`func NewAppSchemasEmbeddingsRightsMetadata() *AppSchemasEmbeddingsRightsMetadata`

NewAppSchemasEmbeddingsRightsMetadata instantiates a new AppSchemasEmbeddingsRightsMetadata object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewAppSchemasEmbeddingsRightsMetadataWithDefaults

`func NewAppSchemasEmbeddingsRightsMetadataWithDefaults() *AppSchemasEmbeddingsRightsMetadata`

NewAppSchemasEmbeddingsRightsMetadataWithDefaults instantiates a new AppSchemasEmbeddingsRightsMetadata object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetCopyrightHolder

`func (o *AppSchemasEmbeddingsRightsMetadata) GetCopyrightHolder() string`

GetCopyrightHolder returns the CopyrightHolder field if non-nil, zero value otherwise.

### GetCopyrightHolderOk

`func (o *AppSchemasEmbeddingsRightsMetadata) GetCopyrightHolderOk() (*string, bool)`

GetCopyrightHolderOk returns a tuple with the CopyrightHolder field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCopyrightHolder

`func (o *AppSchemasEmbeddingsRightsMetadata) SetCopyrightHolder(v string)`

SetCopyrightHolder sets CopyrightHolder field to given value.

### HasCopyrightHolder

`func (o *AppSchemasEmbeddingsRightsMetadata) HasCopyrightHolder() bool`

HasCopyrightHolder returns a boolean if a field has been set.

### SetCopyrightHolderNil

`func (o *AppSchemasEmbeddingsRightsMetadata) SetCopyrightHolderNil(b bool)`

 SetCopyrightHolderNil sets the value for CopyrightHolder to be an explicit nil

### UnsetCopyrightHolder
`func (o *AppSchemasEmbeddingsRightsMetadata) UnsetCopyrightHolder()`

UnsetCopyrightHolder ensures that no value is present for CopyrightHolder, not even an explicit nil
### GetLicenseUrl

`func (o *AppSchemasEmbeddingsRightsMetadata) GetLicenseUrl() string`

GetLicenseUrl returns the LicenseUrl field if non-nil, zero value otherwise.

### GetLicenseUrlOk

`func (o *AppSchemasEmbeddingsRightsMetadata) GetLicenseUrlOk() (*string, bool)`

GetLicenseUrlOk returns a tuple with the LicenseUrl field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLicenseUrl

`func (o *AppSchemasEmbeddingsRightsMetadata) SetLicenseUrl(v string)`

SetLicenseUrl sets LicenseUrl field to given value.

### HasLicenseUrl

`func (o *AppSchemasEmbeddingsRightsMetadata) HasLicenseUrl() bool`

HasLicenseUrl returns a boolean if a field has been set.

### SetLicenseUrlNil

`func (o *AppSchemasEmbeddingsRightsMetadata) SetLicenseUrlNil(b bool)`

 SetLicenseUrlNil sets the value for LicenseUrl to be an explicit nil

### UnsetLicenseUrl
`func (o *AppSchemasEmbeddingsRightsMetadata) UnsetLicenseUrl()`

UnsetLicenseUrl ensures that no value is present for LicenseUrl, not even an explicit nil
### GetUsageTerms

`func (o *AppSchemasEmbeddingsRightsMetadata) GetUsageTerms() string`

GetUsageTerms returns the UsageTerms field if non-nil, zero value otherwise.

### GetUsageTermsOk

`func (o *AppSchemasEmbeddingsRightsMetadata) GetUsageTermsOk() (*string, bool)`

GetUsageTermsOk returns a tuple with the UsageTerms field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUsageTerms

`func (o *AppSchemasEmbeddingsRightsMetadata) SetUsageTerms(v string)`

SetUsageTerms sets UsageTerms field to given value.

### HasUsageTerms

`func (o *AppSchemasEmbeddingsRightsMetadata) HasUsageTerms() bool`

HasUsageTerms returns a boolean if a field has been set.

### SetUsageTermsNil

`func (o *AppSchemasEmbeddingsRightsMetadata) SetUsageTermsNil(b bool)`

 SetUsageTermsNil sets the value for UsageTerms to be an explicit nil

### UnsetUsageTerms
`func (o *AppSchemasEmbeddingsRightsMetadata) UnsetUsageTerms()`

UnsetUsageTerms ensures that no value is present for UsageTerms, not even an explicit nil
### GetSyndicationAllowed

`func (o *AppSchemasEmbeddingsRightsMetadata) GetSyndicationAllowed() bool`

GetSyndicationAllowed returns the SyndicationAllowed field if non-nil, zero value otherwise.

### GetSyndicationAllowedOk

`func (o *AppSchemasEmbeddingsRightsMetadata) GetSyndicationAllowedOk() (*bool, bool)`

GetSyndicationAllowedOk returns a tuple with the SyndicationAllowed field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSyndicationAllowed

`func (o *AppSchemasEmbeddingsRightsMetadata) SetSyndicationAllowed(v bool)`

SetSyndicationAllowed sets SyndicationAllowed field to given value.

### HasSyndicationAllowed

`func (o *AppSchemasEmbeddingsRightsMetadata) HasSyndicationAllowed() bool`

HasSyndicationAllowed returns a boolean if a field has been set.

### SetSyndicationAllowedNil

`func (o *AppSchemasEmbeddingsRightsMetadata) SetSyndicationAllowedNil(b bool)`

 SetSyndicationAllowedNil sets the value for SyndicationAllowed to be an explicit nil

### UnsetSyndicationAllowed
`func (o *AppSchemasEmbeddingsRightsMetadata) UnsetSyndicationAllowed()`

UnsetSyndicationAllowed ensures that no value is present for SyndicationAllowed, not even an explicit nil
### GetEmbargoUntil

`func (o *AppSchemasEmbeddingsRightsMetadata) GetEmbargoUntil() time.Time`

GetEmbargoUntil returns the EmbargoUntil field if non-nil, zero value otherwise.

### GetEmbargoUntilOk

`func (o *AppSchemasEmbeddingsRightsMetadata) GetEmbargoUntilOk() (*time.Time, bool)`

GetEmbargoUntilOk returns a tuple with the EmbargoUntil field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEmbargoUntil

`func (o *AppSchemasEmbeddingsRightsMetadata) SetEmbargoUntil(v time.Time)`

SetEmbargoUntil sets EmbargoUntil field to given value.

### HasEmbargoUntil

`func (o *AppSchemasEmbeddingsRightsMetadata) HasEmbargoUntil() bool`

HasEmbargoUntil returns a boolean if a field has been set.

### SetEmbargoUntilNil

`func (o *AppSchemasEmbeddingsRightsMetadata) SetEmbargoUntilNil(b bool)`

 SetEmbargoUntilNil sets the value for EmbargoUntil to be an explicit nil

### UnsetEmbargoUntil
`func (o *AppSchemasEmbeddingsRightsMetadata) UnsetEmbargoUntil()`

UnsetEmbargoUntil ensures that no value is present for EmbargoUntil, not even an explicit nil
### GetContactEmail

`func (o *AppSchemasEmbeddingsRightsMetadata) GetContactEmail() string`

GetContactEmail returns the ContactEmail field if non-nil, zero value otherwise.

### GetContactEmailOk

`func (o *AppSchemasEmbeddingsRightsMetadata) GetContactEmailOk() (*string, bool)`

GetContactEmailOk returns a tuple with the ContactEmail field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetContactEmail

`func (o *AppSchemasEmbeddingsRightsMetadata) SetContactEmail(v string)`

SetContactEmail sets ContactEmail field to given value.

### HasContactEmail

`func (o *AppSchemasEmbeddingsRightsMetadata) HasContactEmail() bool`

HasContactEmail returns a boolean if a field has been set.

### SetContactEmailNil

`func (o *AppSchemasEmbeddingsRightsMetadata) SetContactEmailNil(b bool)`

 SetContactEmailNil sets the value for ContactEmail to be an explicit nil

### UnsetContactEmail
`func (o *AppSchemasEmbeddingsRightsMetadata) UnsetContactEmail()`

UnsetContactEmail ensures that no value is present for ContactEmail, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


