# QuotaMetric

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | **string** | Human-readable metric name | 
**Used** | **int32** | Amount used this period | 
**Limit** | **int32** | Period limit (-1 for unlimited) | 
**Remaining** | **int32** | Amount remaining (-1 for unlimited) | 
**PercentageUsed** | **float32** | Percentage of limit used | 

## Methods

### NewQuotaMetric

`func NewQuotaMetric(name string, used int32, limit int32, remaining int32, percentageUsed float32, ) *QuotaMetric`

NewQuotaMetric instantiates a new QuotaMetric object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewQuotaMetricWithDefaults

`func NewQuotaMetricWithDefaults() *QuotaMetric`

NewQuotaMetricWithDefaults instantiates a new QuotaMetric object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *QuotaMetric) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *QuotaMetric) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *QuotaMetric) SetName(v string)`

SetName sets Name field to given value.


### GetUsed

`func (o *QuotaMetric) GetUsed() int32`

GetUsed returns the Used field if non-nil, zero value otherwise.

### GetUsedOk

`func (o *QuotaMetric) GetUsedOk() (*int32, bool)`

GetUsedOk returns a tuple with the Used field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUsed

`func (o *QuotaMetric) SetUsed(v int32)`

SetUsed sets Used field to given value.


### GetLimit

`func (o *QuotaMetric) GetLimit() int32`

GetLimit returns the Limit field if non-nil, zero value otherwise.

### GetLimitOk

`func (o *QuotaMetric) GetLimitOk() (*int32, bool)`

GetLimitOk returns a tuple with the Limit field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLimit

`func (o *QuotaMetric) SetLimit(v int32)`

SetLimit sets Limit field to given value.


### GetRemaining

`func (o *QuotaMetric) GetRemaining() int32`

GetRemaining returns the Remaining field if non-nil, zero value otherwise.

### GetRemainingOk

`func (o *QuotaMetric) GetRemainingOk() (*int32, bool)`

GetRemainingOk returns a tuple with the Remaining field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRemaining

`func (o *QuotaMetric) SetRemaining(v int32)`

SetRemaining sets Remaining field to given value.


### GetPercentageUsed

`func (o *QuotaMetric) GetPercentageUsed() float32`

GetPercentageUsed returns the PercentageUsed field if non-nil, zero value otherwise.

### GetPercentageUsedOk

`func (o *QuotaMetric) GetPercentageUsedOk() (*float32, bool)`

GetPercentageUsedOk returns a tuple with the PercentageUsed field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPercentageUsed

`func (o *QuotaMetric) SetPercentageUsed(v float32)`

SetPercentageUsed sets PercentageUsed field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


