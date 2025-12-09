# LicenseInfo

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Type** | **string** | License type (e.g., &#39;All Rights Reserved&#39;, &#39;CC-BY-4.0&#39;) | 
**Url** | Pointer to **NullableString** |  | [optional] 
**ContactEmail** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewLicenseInfo

`func NewLicenseInfo(type_ string, ) *LicenseInfo`

NewLicenseInfo instantiates a new LicenseInfo object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewLicenseInfoWithDefaults

`func NewLicenseInfoWithDefaults() *LicenseInfo`

NewLicenseInfoWithDefaults instantiates a new LicenseInfo object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetType

`func (o *LicenseInfo) GetType() string`

GetType returns the Type field if non-nil, zero value otherwise.

### GetTypeOk

`func (o *LicenseInfo) GetTypeOk() (*string, bool)`

GetTypeOk returns a tuple with the Type field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetType

`func (o *LicenseInfo) SetType(v string)`

SetType sets Type field to given value.


### GetUrl

`func (o *LicenseInfo) GetUrl() string`

GetUrl returns the Url field if non-nil, zero value otherwise.

### GetUrlOk

`func (o *LicenseInfo) GetUrlOk() (*string, bool)`

GetUrlOk returns a tuple with the Url field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUrl

`func (o *LicenseInfo) SetUrl(v string)`

SetUrl sets Url field to given value.

### HasUrl

`func (o *LicenseInfo) HasUrl() bool`

HasUrl returns a boolean if a field has been set.

### SetUrlNil

`func (o *LicenseInfo) SetUrlNil(b bool)`

 SetUrlNil sets the value for Url to be an explicit nil

### UnsetUrl
`func (o *LicenseInfo) UnsetUrl()`

UnsetUrl ensures that no value is present for Url, not even an explicit nil
### GetContactEmail

`func (o *LicenseInfo) GetContactEmail() string`

GetContactEmail returns the ContactEmail field if non-nil, zero value otherwise.

### GetContactEmailOk

`func (o *LicenseInfo) GetContactEmailOk() (*string, bool)`

GetContactEmailOk returns a tuple with the ContactEmail field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetContactEmail

`func (o *LicenseInfo) SetContactEmail(v string)`

SetContactEmail sets ContactEmail field to given value.

### HasContactEmail

`func (o *LicenseInfo) HasContactEmail() bool`

HasContactEmail returns a boolean if a field has been set.

### SetContactEmailNil

`func (o *LicenseInfo) SetContactEmailNil(b bool)`

 SetContactEmailNil sets the value for ContactEmail to be an explicit nil

### UnsetContactEmail
`func (o *LicenseInfo) UnsetContactEmail()`

UnsetContactEmail ensures that no value is present for ContactEmail, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


