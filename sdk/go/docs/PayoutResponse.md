# PayoutResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DistributionId** | **string** |  | 
**TotalMembersPaid** | **int32** |  | 
**TotalAmountPaid** | **string** |  | 
**FailedPayments** | Pointer to **[]string** |  | [optional] [default to []]

## Methods

### NewPayoutResponse

`func NewPayoutResponse(distributionId string, totalMembersPaid int32, totalAmountPaid string, ) *PayoutResponse`

NewPayoutResponse instantiates a new PayoutResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewPayoutResponseWithDefaults

`func NewPayoutResponseWithDefaults() *PayoutResponse`

NewPayoutResponseWithDefaults instantiates a new PayoutResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDistributionId

`func (o *PayoutResponse) GetDistributionId() string`

GetDistributionId returns the DistributionId field if non-nil, zero value otherwise.

### GetDistributionIdOk

`func (o *PayoutResponse) GetDistributionIdOk() (*string, bool)`

GetDistributionIdOk returns a tuple with the DistributionId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDistributionId

`func (o *PayoutResponse) SetDistributionId(v string)`

SetDistributionId sets DistributionId field to given value.


### GetTotalMembersPaid

`func (o *PayoutResponse) GetTotalMembersPaid() int32`

GetTotalMembersPaid returns the TotalMembersPaid field if non-nil, zero value otherwise.

### GetTotalMembersPaidOk

`func (o *PayoutResponse) GetTotalMembersPaidOk() (*int32, bool)`

GetTotalMembersPaidOk returns a tuple with the TotalMembersPaid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalMembersPaid

`func (o *PayoutResponse) SetTotalMembersPaid(v int32)`

SetTotalMembersPaid sets TotalMembersPaid field to given value.


### GetTotalAmountPaid

`func (o *PayoutResponse) GetTotalAmountPaid() string`

GetTotalAmountPaid returns the TotalAmountPaid field if non-nil, zero value otherwise.

### GetTotalAmountPaidOk

`func (o *PayoutResponse) GetTotalAmountPaidOk() (*string, bool)`

GetTotalAmountPaidOk returns a tuple with the TotalAmountPaid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalAmountPaid

`func (o *PayoutResponse) SetTotalAmountPaid(v string)`

SetTotalAmountPaid sets TotalAmountPaid field to given value.


### GetFailedPayments

`func (o *PayoutResponse) GetFailedPayments() []string`

GetFailedPayments returns the FailedPayments field if non-nil, zero value otherwise.

### GetFailedPaymentsOk

`func (o *PayoutResponse) GetFailedPaymentsOk() (*[]string, bool)`

GetFailedPaymentsOk returns a tuple with the FailedPayments field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFailedPayments

`func (o *PayoutResponse) SetFailedPayments(v []string)`

SetFailedPayments sets FailedPayments field to given value.

### HasFailedPayments

`func (o *PayoutResponse) HasFailedPayments() bool`

HasFailedPayments returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


