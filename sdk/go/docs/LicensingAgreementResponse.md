# LicensingAgreementResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | **string** |  | 
**AgreementName** | **string** |  | 
**AiCompanyId** | **string** |  | 
**AgreementType** | [**AgreementType**](AgreementType.md) |  | 
**TotalValue** | **string** |  | 
**Currency** | **string** |  | 
**StartDate** | **string** |  | 
**EndDate** | **string** |  | 
**ContentTypes** | **[]string** |  | 
**MinWordCount** | **NullableInt32** |  | 
**Status** | [**AgreementStatus**](AgreementStatus.md) |  | 
**CreatedAt** | **time.Time** |  | 
**UpdatedAt** | **time.Time** |  | 

## Methods

### NewLicensingAgreementResponse

`func NewLicensingAgreementResponse(id string, agreementName string, aiCompanyId string, agreementType AgreementType, totalValue string, currency string, startDate string, endDate string, contentTypes []string, minWordCount NullableInt32, status AgreementStatus, createdAt time.Time, updatedAt time.Time, ) *LicensingAgreementResponse`

NewLicensingAgreementResponse instantiates a new LicensingAgreementResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewLicensingAgreementResponseWithDefaults

`func NewLicensingAgreementResponseWithDefaults() *LicensingAgreementResponse`

NewLicensingAgreementResponseWithDefaults instantiates a new LicensingAgreementResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *LicensingAgreementResponse) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *LicensingAgreementResponse) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *LicensingAgreementResponse) SetId(v string)`

SetId sets Id field to given value.


### GetAgreementName

`func (o *LicensingAgreementResponse) GetAgreementName() string`

GetAgreementName returns the AgreementName field if non-nil, zero value otherwise.

### GetAgreementNameOk

`func (o *LicensingAgreementResponse) GetAgreementNameOk() (*string, bool)`

GetAgreementNameOk returns a tuple with the AgreementName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAgreementName

`func (o *LicensingAgreementResponse) SetAgreementName(v string)`

SetAgreementName sets AgreementName field to given value.


### GetAiCompanyId

`func (o *LicensingAgreementResponse) GetAiCompanyId() string`

GetAiCompanyId returns the AiCompanyId field if non-nil, zero value otherwise.

### GetAiCompanyIdOk

`func (o *LicensingAgreementResponse) GetAiCompanyIdOk() (*string, bool)`

GetAiCompanyIdOk returns a tuple with the AiCompanyId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAiCompanyId

`func (o *LicensingAgreementResponse) SetAiCompanyId(v string)`

SetAiCompanyId sets AiCompanyId field to given value.


### GetAgreementType

`func (o *LicensingAgreementResponse) GetAgreementType() AgreementType`

GetAgreementType returns the AgreementType field if non-nil, zero value otherwise.

### GetAgreementTypeOk

`func (o *LicensingAgreementResponse) GetAgreementTypeOk() (*AgreementType, bool)`

GetAgreementTypeOk returns a tuple with the AgreementType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAgreementType

`func (o *LicensingAgreementResponse) SetAgreementType(v AgreementType)`

SetAgreementType sets AgreementType field to given value.


### GetTotalValue

`func (o *LicensingAgreementResponse) GetTotalValue() string`

GetTotalValue returns the TotalValue field if non-nil, zero value otherwise.

### GetTotalValueOk

`func (o *LicensingAgreementResponse) GetTotalValueOk() (*string, bool)`

GetTotalValueOk returns a tuple with the TotalValue field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalValue

`func (o *LicensingAgreementResponse) SetTotalValue(v string)`

SetTotalValue sets TotalValue field to given value.


### GetCurrency

`func (o *LicensingAgreementResponse) GetCurrency() string`

GetCurrency returns the Currency field if non-nil, zero value otherwise.

### GetCurrencyOk

`func (o *LicensingAgreementResponse) GetCurrencyOk() (*string, bool)`

GetCurrencyOk returns a tuple with the Currency field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCurrency

`func (o *LicensingAgreementResponse) SetCurrency(v string)`

SetCurrency sets Currency field to given value.


### GetStartDate

`func (o *LicensingAgreementResponse) GetStartDate() string`

GetStartDate returns the StartDate field if non-nil, zero value otherwise.

### GetStartDateOk

`func (o *LicensingAgreementResponse) GetStartDateOk() (*string, bool)`

GetStartDateOk returns a tuple with the StartDate field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStartDate

`func (o *LicensingAgreementResponse) SetStartDate(v string)`

SetStartDate sets StartDate field to given value.


### GetEndDate

`func (o *LicensingAgreementResponse) GetEndDate() string`

GetEndDate returns the EndDate field if non-nil, zero value otherwise.

### GetEndDateOk

`func (o *LicensingAgreementResponse) GetEndDateOk() (*string, bool)`

GetEndDateOk returns a tuple with the EndDate field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEndDate

`func (o *LicensingAgreementResponse) SetEndDate(v string)`

SetEndDate sets EndDate field to given value.


### GetContentTypes

`func (o *LicensingAgreementResponse) GetContentTypes() []string`

GetContentTypes returns the ContentTypes field if non-nil, zero value otherwise.

### GetContentTypesOk

`func (o *LicensingAgreementResponse) GetContentTypesOk() (*[]string, bool)`

GetContentTypesOk returns a tuple with the ContentTypes field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetContentTypes

`func (o *LicensingAgreementResponse) SetContentTypes(v []string)`

SetContentTypes sets ContentTypes field to given value.


### SetContentTypesNil

`func (o *LicensingAgreementResponse) SetContentTypesNil(b bool)`

 SetContentTypesNil sets the value for ContentTypes to be an explicit nil

### UnsetContentTypes
`func (o *LicensingAgreementResponse) UnsetContentTypes()`

UnsetContentTypes ensures that no value is present for ContentTypes, not even an explicit nil
### GetMinWordCount

`func (o *LicensingAgreementResponse) GetMinWordCount() int32`

GetMinWordCount returns the MinWordCount field if non-nil, zero value otherwise.

### GetMinWordCountOk

`func (o *LicensingAgreementResponse) GetMinWordCountOk() (*int32, bool)`

GetMinWordCountOk returns a tuple with the MinWordCount field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMinWordCount

`func (o *LicensingAgreementResponse) SetMinWordCount(v int32)`

SetMinWordCount sets MinWordCount field to given value.


### SetMinWordCountNil

`func (o *LicensingAgreementResponse) SetMinWordCountNil(b bool)`

 SetMinWordCountNil sets the value for MinWordCount to be an explicit nil

### UnsetMinWordCount
`func (o *LicensingAgreementResponse) UnsetMinWordCount()`

UnsetMinWordCount ensures that no value is present for MinWordCount, not even an explicit nil
### GetStatus

`func (o *LicensingAgreementResponse) GetStatus() AgreementStatus`

GetStatus returns the Status field if non-nil, zero value otherwise.

### GetStatusOk

`func (o *LicensingAgreementResponse) GetStatusOk() (*AgreementStatus, bool)`

GetStatusOk returns a tuple with the Status field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatus

`func (o *LicensingAgreementResponse) SetStatus(v AgreementStatus)`

SetStatus sets Status field to given value.


### GetCreatedAt

`func (o *LicensingAgreementResponse) GetCreatedAt() time.Time`

GetCreatedAt returns the CreatedAt field if non-nil, zero value otherwise.

### GetCreatedAtOk

`func (o *LicensingAgreementResponse) GetCreatedAtOk() (*time.Time, bool)`

GetCreatedAtOk returns a tuple with the CreatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreatedAt

`func (o *LicensingAgreementResponse) SetCreatedAt(v time.Time)`

SetCreatedAt sets CreatedAt field to given value.


### GetUpdatedAt

`func (o *LicensingAgreementResponse) GetUpdatedAt() time.Time`

GetUpdatedAt returns the UpdatedAt field if non-nil, zero value otherwise.

### GetUpdatedAtOk

`func (o *LicensingAgreementResponse) GetUpdatedAtOk() (*time.Time, bool)`

GetUpdatedAtOk returns a tuple with the UpdatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUpdatedAt

`func (o *LicensingAgreementResponse) SetUpdatedAt(v time.Time)`

SetUpdatedAt sets UpdatedAt field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


