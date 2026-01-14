# RightsMetadata

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

### NewRightsMetadata

`func NewRightsMetadata() *RightsMetadata`

NewRightsMetadata instantiates a new RightsMetadata object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewRightsMetadataWithDefaults

`func NewRightsMetadataWithDefaults() *RightsMetadata`

NewRightsMetadataWithDefaults instantiates a new RightsMetadata object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetCopyrightHolder

`func (o *RightsMetadata) GetCopyrightHolder() string`

GetCopyrightHolder returns the CopyrightHolder field if non-nil, zero value otherwise.

### GetCopyrightHolderOk

`func (o *RightsMetadata) GetCopyrightHolderOk() (*string, bool)`

GetCopyrightHolderOk returns a tuple with the CopyrightHolder field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCopyrightHolder

`func (o *RightsMetadata) SetCopyrightHolder(v string)`

SetCopyrightHolder sets CopyrightHolder field to given value.

### HasCopyrightHolder

`func (o *RightsMetadata) HasCopyrightHolder() bool`

HasCopyrightHolder returns a boolean if a field has been set.

### SetCopyrightHolderNil

`func (o *RightsMetadata) SetCopyrightHolderNil(b bool)`

 SetCopyrightHolderNil sets the value for CopyrightHolder to be an explicit nil

### UnsetCopyrightHolder
`func (o *RightsMetadata) UnsetCopyrightHolder()`

UnsetCopyrightHolder ensures that no value is present for CopyrightHolder, not even an explicit nil
### GetLicenseUrl

`func (o *RightsMetadata) GetLicenseUrl() string`

GetLicenseUrl returns the LicenseUrl field if non-nil, zero value otherwise.

### GetLicenseUrlOk

`func (o *RightsMetadata) GetLicenseUrlOk() (*string, bool)`

GetLicenseUrlOk returns a tuple with the LicenseUrl field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLicenseUrl

`func (o *RightsMetadata) SetLicenseUrl(v string)`

SetLicenseUrl sets LicenseUrl field to given value.

### HasLicenseUrl

`func (o *RightsMetadata) HasLicenseUrl() bool`

HasLicenseUrl returns a boolean if a field has been set.

### SetLicenseUrlNil

`func (o *RightsMetadata) SetLicenseUrlNil(b bool)`

 SetLicenseUrlNil sets the value for LicenseUrl to be an explicit nil

### UnsetLicenseUrl
`func (o *RightsMetadata) UnsetLicenseUrl()`

UnsetLicenseUrl ensures that no value is present for LicenseUrl, not even an explicit nil
### GetUsageTerms

`func (o *RightsMetadata) GetUsageTerms() string`

GetUsageTerms returns the UsageTerms field if non-nil, zero value otherwise.

### GetUsageTermsOk

`func (o *RightsMetadata) GetUsageTermsOk() (*string, bool)`

GetUsageTermsOk returns a tuple with the UsageTerms field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUsageTerms

`func (o *RightsMetadata) SetUsageTerms(v string)`

SetUsageTerms sets UsageTerms field to given value.

### HasUsageTerms

`func (o *RightsMetadata) HasUsageTerms() bool`

HasUsageTerms returns a boolean if a field has been set.

### SetUsageTermsNil

`func (o *RightsMetadata) SetUsageTermsNil(b bool)`

 SetUsageTermsNil sets the value for UsageTerms to be an explicit nil

### UnsetUsageTerms
`func (o *RightsMetadata) UnsetUsageTerms()`

UnsetUsageTerms ensures that no value is present for UsageTerms, not even an explicit nil
### GetSyndicationAllowed

`func (o *RightsMetadata) GetSyndicationAllowed() bool`

GetSyndicationAllowed returns the SyndicationAllowed field if non-nil, zero value otherwise.

### GetSyndicationAllowedOk

`func (o *RightsMetadata) GetSyndicationAllowedOk() (*bool, bool)`

GetSyndicationAllowedOk returns a tuple with the SyndicationAllowed field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSyndicationAllowed

`func (o *RightsMetadata) SetSyndicationAllowed(v bool)`

SetSyndicationAllowed sets SyndicationAllowed field to given value.

### HasSyndicationAllowed

`func (o *RightsMetadata) HasSyndicationAllowed() bool`

HasSyndicationAllowed returns a boolean if a field has been set.

### SetSyndicationAllowedNil

`func (o *RightsMetadata) SetSyndicationAllowedNil(b bool)`

 SetSyndicationAllowedNil sets the value for SyndicationAllowed to be an explicit nil

### UnsetSyndicationAllowed
`func (o *RightsMetadata) UnsetSyndicationAllowed()`

UnsetSyndicationAllowed ensures that no value is present for SyndicationAllowed, not even an explicit nil
### GetEmbargoUntil

`func (o *RightsMetadata) GetEmbargoUntil() time.Time`

GetEmbargoUntil returns the EmbargoUntil field if non-nil, zero value otherwise.

### GetEmbargoUntilOk

`func (o *RightsMetadata) GetEmbargoUntilOk() (*time.Time, bool)`

GetEmbargoUntilOk returns a tuple with the EmbargoUntil field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEmbargoUntil

`func (o *RightsMetadata) SetEmbargoUntil(v time.Time)`

SetEmbargoUntil sets EmbargoUntil field to given value.

### HasEmbargoUntil

`func (o *RightsMetadata) HasEmbargoUntil() bool`

HasEmbargoUntil returns a boolean if a field has been set.

### SetEmbargoUntilNil

`func (o *RightsMetadata) SetEmbargoUntilNil(b bool)`

 SetEmbargoUntilNil sets the value for EmbargoUntil to be an explicit nil

### UnsetEmbargoUntil
`func (o *RightsMetadata) UnsetEmbargoUntil()`

UnsetEmbargoUntil ensures that no value is present for EmbargoUntil, not even an explicit nil
### GetContactEmail

`func (o *RightsMetadata) GetContactEmail() string`

GetContactEmail returns the ContactEmail field if non-nil, zero value otherwise.

### GetContactEmailOk

`func (o *RightsMetadata) GetContactEmailOk() (*string, bool)`

GetContactEmailOk returns a tuple with the ContactEmail field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetContactEmail

`func (o *RightsMetadata) SetContactEmail(v string)`

SetContactEmail sets ContactEmail field to given value.

### HasContactEmail

`func (o *RightsMetadata) HasContactEmail() bool`

HasContactEmail returns a boolean if a field has been set.

### SetContactEmailNil

`func (o *RightsMetadata) SetContactEmailNil(b bool)`

 SetContactEmailNil sets the value for ContactEmail to be an explicit nil

### UnsetContactEmail
`func (o *RightsMetadata) UnsetContactEmail()`

UnsetContactEmail ensures that no value is present for ContactEmail, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


