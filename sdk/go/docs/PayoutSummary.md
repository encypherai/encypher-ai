# PayoutSummary

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | **string** |  | 
**PeriodStart** | **string** |  | 
**PeriodEnd** | **string** |  | 
**TotalEarningsCents** | **int32** |  | 
**PayoutAmountCents** | **int32** |  | 
**Currency** | **string** |  | 
**Status** | **string** |  | 
**PaidAt** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewPayoutSummary

`func NewPayoutSummary(id string, periodStart string, periodEnd string, totalEarningsCents int32, payoutAmountCents int32, currency string, status string, ) *PayoutSummary`

NewPayoutSummary instantiates a new PayoutSummary object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewPayoutSummaryWithDefaults

`func NewPayoutSummaryWithDefaults() *PayoutSummary`

NewPayoutSummaryWithDefaults instantiates a new PayoutSummary object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *PayoutSummary) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *PayoutSummary) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *PayoutSummary) SetId(v string)`

SetId sets Id field to given value.


### GetPeriodStart

`func (o *PayoutSummary) GetPeriodStart() string`

GetPeriodStart returns the PeriodStart field if non-nil, zero value otherwise.

### GetPeriodStartOk

`func (o *PayoutSummary) GetPeriodStartOk() (*string, bool)`

GetPeriodStartOk returns a tuple with the PeriodStart field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPeriodStart

`func (o *PayoutSummary) SetPeriodStart(v string)`

SetPeriodStart sets PeriodStart field to given value.


### GetPeriodEnd

`func (o *PayoutSummary) GetPeriodEnd() string`

GetPeriodEnd returns the PeriodEnd field if non-nil, zero value otherwise.

### GetPeriodEndOk

`func (o *PayoutSummary) GetPeriodEndOk() (*string, bool)`

GetPeriodEndOk returns a tuple with the PeriodEnd field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPeriodEnd

`func (o *PayoutSummary) SetPeriodEnd(v string)`

SetPeriodEnd sets PeriodEnd field to given value.


### GetTotalEarningsCents

`func (o *PayoutSummary) GetTotalEarningsCents() int32`

GetTotalEarningsCents returns the TotalEarningsCents field if non-nil, zero value otherwise.

### GetTotalEarningsCentsOk

`func (o *PayoutSummary) GetTotalEarningsCentsOk() (*int32, bool)`

GetTotalEarningsCentsOk returns a tuple with the TotalEarningsCents field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalEarningsCents

`func (o *PayoutSummary) SetTotalEarningsCents(v int32)`

SetTotalEarningsCents sets TotalEarningsCents field to given value.


### GetPayoutAmountCents

`func (o *PayoutSummary) GetPayoutAmountCents() int32`

GetPayoutAmountCents returns the PayoutAmountCents field if non-nil, zero value otherwise.

### GetPayoutAmountCentsOk

`func (o *PayoutSummary) GetPayoutAmountCentsOk() (*int32, bool)`

GetPayoutAmountCentsOk returns a tuple with the PayoutAmountCents field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPayoutAmountCents

`func (o *PayoutSummary) SetPayoutAmountCents(v int32)`

SetPayoutAmountCents sets PayoutAmountCents field to given value.


### GetCurrency

`func (o *PayoutSummary) GetCurrency() string`

GetCurrency returns the Currency field if non-nil, zero value otherwise.

### GetCurrencyOk

`func (o *PayoutSummary) GetCurrencyOk() (*string, bool)`

GetCurrencyOk returns a tuple with the Currency field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCurrency

`func (o *PayoutSummary) SetCurrency(v string)`

SetCurrency sets Currency field to given value.


### GetStatus

`func (o *PayoutSummary) GetStatus() string`

GetStatus returns the Status field if non-nil, zero value otherwise.

### GetStatusOk

`func (o *PayoutSummary) GetStatusOk() (*string, bool)`

GetStatusOk returns a tuple with the Status field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatus

`func (o *PayoutSummary) SetStatus(v string)`

SetStatus sets Status field to given value.


### GetPaidAt

`func (o *PayoutSummary) GetPaidAt() string`

GetPaidAt returns the PaidAt field if non-nil, zero value otherwise.

### GetPaidAtOk

`func (o *PayoutSummary) GetPaidAtOk() (*string, bool)`

GetPaidAtOk returns a tuple with the PaidAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPaidAt

`func (o *PayoutSummary) SetPaidAt(v string)`

SetPaidAt sets PaidAt field to given value.

### HasPaidAt

`func (o *PayoutSummary) HasPaidAt() bool`

HasPaidAt returns a boolean if a field has been set.

### SetPaidAtNil

`func (o *PayoutSummary) SetPaidAtNil(b bool)`

 SetPaidAtNil sets the value for PaidAt to be an explicit nil

### UnsetPaidAt
`func (o *PayoutSummary) UnsetPaidAt()`

UnsetPaidAt ensures that no value is present for PaidAt, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


