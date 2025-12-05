# UsageMetric

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | **string** |  | 
**Used** | **int32** |  | 
**Limit** | **int32** |  | 
**Remaining** | **int32** |  | 
**PercentageUsed** | **float32** |  | 
**Available** | **bool** |  | 

## Methods

### NewUsageMetric

`func NewUsageMetric(name string, used int32, limit int32, remaining int32, percentageUsed float32, available bool, ) *UsageMetric`

NewUsageMetric instantiates a new UsageMetric object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewUsageMetricWithDefaults

`func NewUsageMetricWithDefaults() *UsageMetric`

NewUsageMetricWithDefaults instantiates a new UsageMetric object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *UsageMetric) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *UsageMetric) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *UsageMetric) SetName(v string)`

SetName sets Name field to given value.


### GetUsed

`func (o *UsageMetric) GetUsed() int32`

GetUsed returns the Used field if non-nil, zero value otherwise.

### GetUsedOk

`func (o *UsageMetric) GetUsedOk() (*int32, bool)`

GetUsedOk returns a tuple with the Used field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUsed

`func (o *UsageMetric) SetUsed(v int32)`

SetUsed sets Used field to given value.


### GetLimit

`func (o *UsageMetric) GetLimit() int32`

GetLimit returns the Limit field if non-nil, zero value otherwise.

### GetLimitOk

`func (o *UsageMetric) GetLimitOk() (*int32, bool)`

GetLimitOk returns a tuple with the Limit field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLimit

`func (o *UsageMetric) SetLimit(v int32)`

SetLimit sets Limit field to given value.


### GetRemaining

`func (o *UsageMetric) GetRemaining() int32`

GetRemaining returns the Remaining field if non-nil, zero value otherwise.

### GetRemainingOk

`func (o *UsageMetric) GetRemainingOk() (*int32, bool)`

GetRemainingOk returns a tuple with the Remaining field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRemaining

`func (o *UsageMetric) SetRemaining(v int32)`

SetRemaining sets Remaining field to given value.


### GetPercentageUsed

`func (o *UsageMetric) GetPercentageUsed() float32`

GetPercentageUsed returns the PercentageUsed field if non-nil, zero value otherwise.

### GetPercentageUsedOk

`func (o *UsageMetric) GetPercentageUsedOk() (*float32, bool)`

GetPercentageUsedOk returns a tuple with the PercentageUsed field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPercentageUsed

`func (o *UsageMetric) SetPercentageUsed(v float32)`

SetPercentageUsed sets PercentageUsed field to given value.


### GetAvailable

`func (o *UsageMetric) GetAvailable() bool`

GetAvailable returns the Available field if non-nil, zero value otherwise.

### GetAvailableOk

`func (o *UsageMetric) GetAvailableOk() (*bool, bool)`

GetAvailableOk returns a tuple with the Available field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAvailable

`func (o *UsageMetric) SetAvailable(v bool)`

SetAvailable sets Available field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


