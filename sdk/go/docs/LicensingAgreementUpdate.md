# LicensingAgreementUpdate

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**AgreementName** | Pointer to **NullableString** |  | [optional] 
**TotalValue** | Pointer to [**NullableTotalValue1**](TotalValue1.md) |  | [optional] 
**EndDate** | Pointer to **NullableString** |  | [optional] 
**ContentTypes** | Pointer to **[]string** |  | [optional] 
**MinWordCount** | Pointer to **NullableInt32** |  | [optional] 
**Status** | Pointer to [**NullableAgreementStatus**](AgreementStatus.md) |  | [optional] 

## Methods

### NewLicensingAgreementUpdate

`func NewLicensingAgreementUpdate() *LicensingAgreementUpdate`

NewLicensingAgreementUpdate instantiates a new LicensingAgreementUpdate object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewLicensingAgreementUpdateWithDefaults

`func NewLicensingAgreementUpdateWithDefaults() *LicensingAgreementUpdate`

NewLicensingAgreementUpdateWithDefaults instantiates a new LicensingAgreementUpdate object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetAgreementName

`func (o *LicensingAgreementUpdate) GetAgreementName() string`

GetAgreementName returns the AgreementName field if non-nil, zero value otherwise.

### GetAgreementNameOk

`func (o *LicensingAgreementUpdate) GetAgreementNameOk() (*string, bool)`

GetAgreementNameOk returns a tuple with the AgreementName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAgreementName

`func (o *LicensingAgreementUpdate) SetAgreementName(v string)`

SetAgreementName sets AgreementName field to given value.

### HasAgreementName

`func (o *LicensingAgreementUpdate) HasAgreementName() bool`

HasAgreementName returns a boolean if a field has been set.

### SetAgreementNameNil

`func (o *LicensingAgreementUpdate) SetAgreementNameNil(b bool)`

 SetAgreementNameNil sets the value for AgreementName to be an explicit nil

### UnsetAgreementName
`func (o *LicensingAgreementUpdate) UnsetAgreementName()`

UnsetAgreementName ensures that no value is present for AgreementName, not even an explicit nil
### GetTotalValue

`func (o *LicensingAgreementUpdate) GetTotalValue() TotalValue1`

GetTotalValue returns the TotalValue field if non-nil, zero value otherwise.

### GetTotalValueOk

`func (o *LicensingAgreementUpdate) GetTotalValueOk() (*TotalValue1, bool)`

GetTotalValueOk returns a tuple with the TotalValue field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalValue

`func (o *LicensingAgreementUpdate) SetTotalValue(v TotalValue1)`

SetTotalValue sets TotalValue field to given value.

### HasTotalValue

`func (o *LicensingAgreementUpdate) HasTotalValue() bool`

HasTotalValue returns a boolean if a field has been set.

### SetTotalValueNil

`func (o *LicensingAgreementUpdate) SetTotalValueNil(b bool)`

 SetTotalValueNil sets the value for TotalValue to be an explicit nil

### UnsetTotalValue
`func (o *LicensingAgreementUpdate) UnsetTotalValue()`

UnsetTotalValue ensures that no value is present for TotalValue, not even an explicit nil
### GetEndDate

`func (o *LicensingAgreementUpdate) GetEndDate() string`

GetEndDate returns the EndDate field if non-nil, zero value otherwise.

### GetEndDateOk

`func (o *LicensingAgreementUpdate) GetEndDateOk() (*string, bool)`

GetEndDateOk returns a tuple with the EndDate field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEndDate

`func (o *LicensingAgreementUpdate) SetEndDate(v string)`

SetEndDate sets EndDate field to given value.

### HasEndDate

`func (o *LicensingAgreementUpdate) HasEndDate() bool`

HasEndDate returns a boolean if a field has been set.

### SetEndDateNil

`func (o *LicensingAgreementUpdate) SetEndDateNil(b bool)`

 SetEndDateNil sets the value for EndDate to be an explicit nil

### UnsetEndDate
`func (o *LicensingAgreementUpdate) UnsetEndDate()`

UnsetEndDate ensures that no value is present for EndDate, not even an explicit nil
### GetContentTypes

`func (o *LicensingAgreementUpdate) GetContentTypes() []string`

GetContentTypes returns the ContentTypes field if non-nil, zero value otherwise.

### GetContentTypesOk

`func (o *LicensingAgreementUpdate) GetContentTypesOk() (*[]string, bool)`

GetContentTypesOk returns a tuple with the ContentTypes field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetContentTypes

`func (o *LicensingAgreementUpdate) SetContentTypes(v []string)`

SetContentTypes sets ContentTypes field to given value.

### HasContentTypes

`func (o *LicensingAgreementUpdate) HasContentTypes() bool`

HasContentTypes returns a boolean if a field has been set.

### SetContentTypesNil

`func (o *LicensingAgreementUpdate) SetContentTypesNil(b bool)`

 SetContentTypesNil sets the value for ContentTypes to be an explicit nil

### UnsetContentTypes
`func (o *LicensingAgreementUpdate) UnsetContentTypes()`

UnsetContentTypes ensures that no value is present for ContentTypes, not even an explicit nil
### GetMinWordCount

`func (o *LicensingAgreementUpdate) GetMinWordCount() int32`

GetMinWordCount returns the MinWordCount field if non-nil, zero value otherwise.

### GetMinWordCountOk

`func (o *LicensingAgreementUpdate) GetMinWordCountOk() (*int32, bool)`

GetMinWordCountOk returns a tuple with the MinWordCount field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMinWordCount

`func (o *LicensingAgreementUpdate) SetMinWordCount(v int32)`

SetMinWordCount sets MinWordCount field to given value.

### HasMinWordCount

`func (o *LicensingAgreementUpdate) HasMinWordCount() bool`

HasMinWordCount returns a boolean if a field has been set.

### SetMinWordCountNil

`func (o *LicensingAgreementUpdate) SetMinWordCountNil(b bool)`

 SetMinWordCountNil sets the value for MinWordCount to be an explicit nil

### UnsetMinWordCount
`func (o *LicensingAgreementUpdate) UnsetMinWordCount()`

UnsetMinWordCount ensures that no value is present for MinWordCount, not even an explicit nil
### GetStatus

`func (o *LicensingAgreementUpdate) GetStatus() AgreementStatus`

GetStatus returns the Status field if non-nil, zero value otherwise.

### GetStatusOk

`func (o *LicensingAgreementUpdate) GetStatusOk() (*AgreementStatus, bool)`

GetStatusOk returns a tuple with the Status field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatus

`func (o *LicensingAgreementUpdate) SetStatus(v AgreementStatus)`

SetStatus sets Status field to given value.

### HasStatus

`func (o *LicensingAgreementUpdate) HasStatus() bool`

HasStatus returns a boolean if a field has been set.

### SetStatusNil

`func (o *LicensingAgreementUpdate) SetStatusNil(b bool)`

 SetStatusNil sets the value for Status to be an explicit nil

### UnsetStatus
`func (o *LicensingAgreementUpdate) UnsetStatus()`

UnsetStatus ensures that no value is present for Status, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


