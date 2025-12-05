# LicensingAgreementCreateResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | **string** |  | 
**AgreementName** | **string** |  | 
**ApiKey** | **string** |  | 
**ApiKeyPrefix** | **string** |  | 
**Status** | [**AgreementStatus**](AgreementStatus.md) |  | 
**CreatedAt** | **time.Time** |  | 

## Methods

### NewLicensingAgreementCreateResponse

`func NewLicensingAgreementCreateResponse(id string, agreementName string, apiKey string, apiKeyPrefix string, status AgreementStatus, createdAt time.Time, ) *LicensingAgreementCreateResponse`

NewLicensingAgreementCreateResponse instantiates a new LicensingAgreementCreateResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewLicensingAgreementCreateResponseWithDefaults

`func NewLicensingAgreementCreateResponseWithDefaults() *LicensingAgreementCreateResponse`

NewLicensingAgreementCreateResponseWithDefaults instantiates a new LicensingAgreementCreateResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *LicensingAgreementCreateResponse) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *LicensingAgreementCreateResponse) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *LicensingAgreementCreateResponse) SetId(v string)`

SetId sets Id field to given value.


### GetAgreementName

`func (o *LicensingAgreementCreateResponse) GetAgreementName() string`

GetAgreementName returns the AgreementName field if non-nil, zero value otherwise.

### GetAgreementNameOk

`func (o *LicensingAgreementCreateResponse) GetAgreementNameOk() (*string, bool)`

GetAgreementNameOk returns a tuple with the AgreementName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAgreementName

`func (o *LicensingAgreementCreateResponse) SetAgreementName(v string)`

SetAgreementName sets AgreementName field to given value.


### GetApiKey

`func (o *LicensingAgreementCreateResponse) GetApiKey() string`

GetApiKey returns the ApiKey field if non-nil, zero value otherwise.

### GetApiKeyOk

`func (o *LicensingAgreementCreateResponse) GetApiKeyOk() (*string, bool)`

GetApiKeyOk returns a tuple with the ApiKey field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetApiKey

`func (o *LicensingAgreementCreateResponse) SetApiKey(v string)`

SetApiKey sets ApiKey field to given value.


### GetApiKeyPrefix

`func (o *LicensingAgreementCreateResponse) GetApiKeyPrefix() string`

GetApiKeyPrefix returns the ApiKeyPrefix field if non-nil, zero value otherwise.

### GetApiKeyPrefixOk

`func (o *LicensingAgreementCreateResponse) GetApiKeyPrefixOk() (*string, bool)`

GetApiKeyPrefixOk returns a tuple with the ApiKeyPrefix field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetApiKeyPrefix

`func (o *LicensingAgreementCreateResponse) SetApiKeyPrefix(v string)`

SetApiKeyPrefix sets ApiKeyPrefix field to given value.


### GetStatus

`func (o *LicensingAgreementCreateResponse) GetStatus() AgreementStatus`

GetStatus returns the Status field if non-nil, zero value otherwise.

### GetStatusOk

`func (o *LicensingAgreementCreateResponse) GetStatusOk() (*AgreementStatus, bool)`

GetStatusOk returns a tuple with the Status field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatus

`func (o *LicensingAgreementCreateResponse) SetStatus(v AgreementStatus)`

SetStatus sets Status field to given value.


### GetCreatedAt

`func (o *LicensingAgreementCreateResponse) GetCreatedAt() time.Time`

GetCreatedAt returns the CreatedAt field if non-nil, zero value otherwise.

### GetCreatedAtOk

`func (o *LicensingAgreementCreateResponse) GetCreatedAtOk() (*time.Time, bool)`

GetCreatedAtOk returns a tuple with the CreatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreatedAt

`func (o *LicensingAgreementCreateResponse) SetCreatedAt(v time.Time)`

SetCreatedAt sets CreatedAt field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


