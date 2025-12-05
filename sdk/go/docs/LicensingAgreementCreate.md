# LicensingAgreementCreate

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**AgreementName** | **string** |  | 
**AiCompanyName** | **string** |  | 
**AiCompanyEmail** | **string** |  | 
**AgreementType** | Pointer to [**AgreementType**](AgreementType.md) |  | [optional] 
**TotalValue** | [**TotalValue**](TotalValue.md) |  | 
**Currency** | Pointer to **string** |  | [optional] [default to "USD"]
**StartDate** | **string** |  | 
**EndDate** | **string** |  | 
**ContentTypes** | Pointer to **[]string** |  | [optional] 
**MinWordCount** | Pointer to **NullableInt32** |  | [optional] 

## Methods

### NewLicensingAgreementCreate

`func NewLicensingAgreementCreate(agreementName string, aiCompanyName string, aiCompanyEmail string, totalValue TotalValue, startDate string, endDate string, ) *LicensingAgreementCreate`

NewLicensingAgreementCreate instantiates a new LicensingAgreementCreate object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewLicensingAgreementCreateWithDefaults

`func NewLicensingAgreementCreateWithDefaults() *LicensingAgreementCreate`

NewLicensingAgreementCreateWithDefaults instantiates a new LicensingAgreementCreate object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetAgreementName

`func (o *LicensingAgreementCreate) GetAgreementName() string`

GetAgreementName returns the AgreementName field if non-nil, zero value otherwise.

### GetAgreementNameOk

`func (o *LicensingAgreementCreate) GetAgreementNameOk() (*string, bool)`

GetAgreementNameOk returns a tuple with the AgreementName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAgreementName

`func (o *LicensingAgreementCreate) SetAgreementName(v string)`

SetAgreementName sets AgreementName field to given value.


### GetAiCompanyName

`func (o *LicensingAgreementCreate) GetAiCompanyName() string`

GetAiCompanyName returns the AiCompanyName field if non-nil, zero value otherwise.

### GetAiCompanyNameOk

`func (o *LicensingAgreementCreate) GetAiCompanyNameOk() (*string, bool)`

GetAiCompanyNameOk returns a tuple with the AiCompanyName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAiCompanyName

`func (o *LicensingAgreementCreate) SetAiCompanyName(v string)`

SetAiCompanyName sets AiCompanyName field to given value.


### GetAiCompanyEmail

`func (o *LicensingAgreementCreate) GetAiCompanyEmail() string`

GetAiCompanyEmail returns the AiCompanyEmail field if non-nil, zero value otherwise.

### GetAiCompanyEmailOk

`func (o *LicensingAgreementCreate) GetAiCompanyEmailOk() (*string, bool)`

GetAiCompanyEmailOk returns a tuple with the AiCompanyEmail field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAiCompanyEmail

`func (o *LicensingAgreementCreate) SetAiCompanyEmail(v string)`

SetAiCompanyEmail sets AiCompanyEmail field to given value.


### GetAgreementType

`func (o *LicensingAgreementCreate) GetAgreementType() AgreementType`

GetAgreementType returns the AgreementType field if non-nil, zero value otherwise.

### GetAgreementTypeOk

`func (o *LicensingAgreementCreate) GetAgreementTypeOk() (*AgreementType, bool)`

GetAgreementTypeOk returns a tuple with the AgreementType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAgreementType

`func (o *LicensingAgreementCreate) SetAgreementType(v AgreementType)`

SetAgreementType sets AgreementType field to given value.

### HasAgreementType

`func (o *LicensingAgreementCreate) HasAgreementType() bool`

HasAgreementType returns a boolean if a field has been set.

### GetTotalValue

`func (o *LicensingAgreementCreate) GetTotalValue() TotalValue`

GetTotalValue returns the TotalValue field if non-nil, zero value otherwise.

### GetTotalValueOk

`func (o *LicensingAgreementCreate) GetTotalValueOk() (*TotalValue, bool)`

GetTotalValueOk returns a tuple with the TotalValue field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalValue

`func (o *LicensingAgreementCreate) SetTotalValue(v TotalValue)`

SetTotalValue sets TotalValue field to given value.


### GetCurrency

`func (o *LicensingAgreementCreate) GetCurrency() string`

GetCurrency returns the Currency field if non-nil, zero value otherwise.

### GetCurrencyOk

`func (o *LicensingAgreementCreate) GetCurrencyOk() (*string, bool)`

GetCurrencyOk returns a tuple with the Currency field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCurrency

`func (o *LicensingAgreementCreate) SetCurrency(v string)`

SetCurrency sets Currency field to given value.

### HasCurrency

`func (o *LicensingAgreementCreate) HasCurrency() bool`

HasCurrency returns a boolean if a field has been set.

### GetStartDate

`func (o *LicensingAgreementCreate) GetStartDate() string`

GetStartDate returns the StartDate field if non-nil, zero value otherwise.

### GetStartDateOk

`func (o *LicensingAgreementCreate) GetStartDateOk() (*string, bool)`

GetStartDateOk returns a tuple with the StartDate field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStartDate

`func (o *LicensingAgreementCreate) SetStartDate(v string)`

SetStartDate sets StartDate field to given value.


### GetEndDate

`func (o *LicensingAgreementCreate) GetEndDate() string`

GetEndDate returns the EndDate field if non-nil, zero value otherwise.

### GetEndDateOk

`func (o *LicensingAgreementCreate) GetEndDateOk() (*string, bool)`

GetEndDateOk returns a tuple with the EndDate field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEndDate

`func (o *LicensingAgreementCreate) SetEndDate(v string)`

SetEndDate sets EndDate field to given value.


### GetContentTypes

`func (o *LicensingAgreementCreate) GetContentTypes() []string`

GetContentTypes returns the ContentTypes field if non-nil, zero value otherwise.

### GetContentTypesOk

`func (o *LicensingAgreementCreate) GetContentTypesOk() (*[]string, bool)`

GetContentTypesOk returns a tuple with the ContentTypes field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetContentTypes

`func (o *LicensingAgreementCreate) SetContentTypes(v []string)`

SetContentTypes sets ContentTypes field to given value.

### HasContentTypes

`func (o *LicensingAgreementCreate) HasContentTypes() bool`

HasContentTypes returns a boolean if a field has been set.

### SetContentTypesNil

`func (o *LicensingAgreementCreate) SetContentTypesNil(b bool)`

 SetContentTypesNil sets the value for ContentTypes to be an explicit nil

### UnsetContentTypes
`func (o *LicensingAgreementCreate) UnsetContentTypes()`

UnsetContentTypes ensures that no value is present for ContentTypes, not even an explicit nil
### GetMinWordCount

`func (o *LicensingAgreementCreate) GetMinWordCount() int32`

GetMinWordCount returns the MinWordCount field if non-nil, zero value otherwise.

### GetMinWordCountOk

`func (o *LicensingAgreementCreate) GetMinWordCountOk() (*int32, bool)`

GetMinWordCountOk returns a tuple with the MinWordCount field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMinWordCount

`func (o *LicensingAgreementCreate) SetMinWordCount(v int32)`

SetMinWordCount sets MinWordCount field to given value.

### HasMinWordCount

`func (o *LicensingAgreementCreate) HasMinWordCount() bool`

HasMinWordCount returns a boolean if a field has been set.

### SetMinWordCountNil

`func (o *LicensingAgreementCreate) SetMinWordCountNil(b bool)`

 SetMinWordCountNil sets the value for MinWordCount to be an explicit nil

### UnsetMinWordCount
`func (o *LicensingAgreementCreate) UnsetMinWordCount()`

UnsetMinWordCount ensures that no value is present for MinWordCount, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


