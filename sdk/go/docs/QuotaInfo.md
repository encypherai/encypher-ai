# QuotaInfo

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**OrganizationId** | **string** |  | 
**Tier** | **string** |  | 
**PeriodStart** | **string** |  | 
**PeriodEnd** | **string** |  | 
**Metrics** | [**map[string]QuotaMetric**](QuotaMetric.md) |  | 
**ResetDate** | **string** |  | 

## Methods

### NewQuotaInfo

`func NewQuotaInfo(organizationId string, tier string, periodStart string, periodEnd string, metrics map[string]QuotaMetric, resetDate string, ) *QuotaInfo`

NewQuotaInfo instantiates a new QuotaInfo object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewQuotaInfoWithDefaults

`func NewQuotaInfoWithDefaults() *QuotaInfo`

NewQuotaInfoWithDefaults instantiates a new QuotaInfo object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetOrganizationId

`func (o *QuotaInfo) GetOrganizationId() string`

GetOrganizationId returns the OrganizationId field if non-nil, zero value otherwise.

### GetOrganizationIdOk

`func (o *QuotaInfo) GetOrganizationIdOk() (*string, bool)`

GetOrganizationIdOk returns a tuple with the OrganizationId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationId

`func (o *QuotaInfo) SetOrganizationId(v string)`

SetOrganizationId sets OrganizationId field to given value.


### GetTier

`func (o *QuotaInfo) GetTier() string`

GetTier returns the Tier field if non-nil, zero value otherwise.

### GetTierOk

`func (o *QuotaInfo) GetTierOk() (*string, bool)`

GetTierOk returns a tuple with the Tier field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTier

`func (o *QuotaInfo) SetTier(v string)`

SetTier sets Tier field to given value.


### GetPeriodStart

`func (o *QuotaInfo) GetPeriodStart() string`

GetPeriodStart returns the PeriodStart field if non-nil, zero value otherwise.

### GetPeriodStartOk

`func (o *QuotaInfo) GetPeriodStartOk() (*string, bool)`

GetPeriodStartOk returns a tuple with the PeriodStart field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPeriodStart

`func (o *QuotaInfo) SetPeriodStart(v string)`

SetPeriodStart sets PeriodStart field to given value.


### GetPeriodEnd

`func (o *QuotaInfo) GetPeriodEnd() string`

GetPeriodEnd returns the PeriodEnd field if non-nil, zero value otherwise.

### GetPeriodEndOk

`func (o *QuotaInfo) GetPeriodEndOk() (*string, bool)`

GetPeriodEndOk returns a tuple with the PeriodEnd field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPeriodEnd

`func (o *QuotaInfo) SetPeriodEnd(v string)`

SetPeriodEnd sets PeriodEnd field to given value.


### GetMetrics

`func (o *QuotaInfo) GetMetrics() map[string]QuotaMetric`

GetMetrics returns the Metrics field if non-nil, zero value otherwise.

### GetMetricsOk

`func (o *QuotaInfo) GetMetricsOk() (*map[string]QuotaMetric, bool)`

GetMetricsOk returns a tuple with the Metrics field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMetrics

`func (o *QuotaInfo) SetMetrics(v map[string]QuotaMetric)`

SetMetrics sets Metrics field to given value.


### GetResetDate

`func (o *QuotaInfo) GetResetDate() string`

GetResetDate returns the ResetDate field if non-nil, zero value otherwise.

### GetResetDateOk

`func (o *QuotaInfo) GetResetDateOk() (*string, bool)`

GetResetDateOk returns a tuple with the ResetDate field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetResetDate

`func (o *QuotaInfo) SetResetDate(v string)`

SetResetDate sets ResetDate field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


