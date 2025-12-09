# PayoutCreate

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DistributionId** | **string** |  | 
**PaymentMethod** | Pointer to **string** |  | [optional] [default to "stripe"]

## Methods

### NewPayoutCreate

`func NewPayoutCreate(distributionId string, ) *PayoutCreate`

NewPayoutCreate instantiates a new PayoutCreate object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewPayoutCreateWithDefaults

`func NewPayoutCreateWithDefaults() *PayoutCreate`

NewPayoutCreateWithDefaults instantiates a new PayoutCreate object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDistributionId

`func (o *PayoutCreate) GetDistributionId() string`

GetDistributionId returns the DistributionId field if non-nil, zero value otherwise.

### GetDistributionIdOk

`func (o *PayoutCreate) GetDistributionIdOk() (*string, bool)`

GetDistributionIdOk returns a tuple with the DistributionId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDistributionId

`func (o *PayoutCreate) SetDistributionId(v string)`

SetDistributionId sets DistributionId field to given value.


### GetPaymentMethod

`func (o *PayoutCreate) GetPaymentMethod() string`

GetPaymentMethod returns the PaymentMethod field if non-nil, zero value otherwise.

### GetPaymentMethodOk

`func (o *PayoutCreate) GetPaymentMethodOk() (*string, bool)`

GetPaymentMethodOk returns a tuple with the PaymentMethod field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPaymentMethod

`func (o *PayoutCreate) SetPaymentMethod(v string)`

SetPaymentMethod sets PaymentMethod field to given value.

### HasPaymentMethod

`func (o *PayoutCreate) HasPaymentMethod() bool`

HasPaymentMethod returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


