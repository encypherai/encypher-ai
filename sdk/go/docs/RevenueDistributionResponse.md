# RevenueDistributionResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | **string** |  | 
**AgreementId** | **string** |  | 
**PeriodStart** | **string** |  | 
**PeriodEnd** | **string** |  | 
**TotalRevenue** | **string** |  | 
**EncypherShare** | **string** |  | 
**MemberPool** | **string** |  | 
**Status** | [**DistributionStatus**](DistributionStatus.md) |  | 
**CreatedAt** | **time.Time** |  | 
**ProcessedAt** | **NullableTime** |  | 
**MemberRevenues** | Pointer to [**[]MemberRevenueDetail**](MemberRevenueDetail.md) |  | [optional] 

## Methods

### NewRevenueDistributionResponse

`func NewRevenueDistributionResponse(id string, agreementId string, periodStart string, periodEnd string, totalRevenue string, encypherShare string, memberPool string, status DistributionStatus, createdAt time.Time, processedAt NullableTime, ) *RevenueDistributionResponse`

NewRevenueDistributionResponse instantiates a new RevenueDistributionResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewRevenueDistributionResponseWithDefaults

`func NewRevenueDistributionResponseWithDefaults() *RevenueDistributionResponse`

NewRevenueDistributionResponseWithDefaults instantiates a new RevenueDistributionResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *RevenueDistributionResponse) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *RevenueDistributionResponse) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *RevenueDistributionResponse) SetId(v string)`

SetId sets Id field to given value.


### GetAgreementId

`func (o *RevenueDistributionResponse) GetAgreementId() string`

GetAgreementId returns the AgreementId field if non-nil, zero value otherwise.

### GetAgreementIdOk

`func (o *RevenueDistributionResponse) GetAgreementIdOk() (*string, bool)`

GetAgreementIdOk returns a tuple with the AgreementId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAgreementId

`func (o *RevenueDistributionResponse) SetAgreementId(v string)`

SetAgreementId sets AgreementId field to given value.


### GetPeriodStart

`func (o *RevenueDistributionResponse) GetPeriodStart() string`

GetPeriodStart returns the PeriodStart field if non-nil, zero value otherwise.

### GetPeriodStartOk

`func (o *RevenueDistributionResponse) GetPeriodStartOk() (*string, bool)`

GetPeriodStartOk returns a tuple with the PeriodStart field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPeriodStart

`func (o *RevenueDistributionResponse) SetPeriodStart(v string)`

SetPeriodStart sets PeriodStart field to given value.


### GetPeriodEnd

`func (o *RevenueDistributionResponse) GetPeriodEnd() string`

GetPeriodEnd returns the PeriodEnd field if non-nil, zero value otherwise.

### GetPeriodEndOk

`func (o *RevenueDistributionResponse) GetPeriodEndOk() (*string, bool)`

GetPeriodEndOk returns a tuple with the PeriodEnd field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPeriodEnd

`func (o *RevenueDistributionResponse) SetPeriodEnd(v string)`

SetPeriodEnd sets PeriodEnd field to given value.


### GetTotalRevenue

`func (o *RevenueDistributionResponse) GetTotalRevenue() string`

GetTotalRevenue returns the TotalRevenue field if non-nil, zero value otherwise.

### GetTotalRevenueOk

`func (o *RevenueDistributionResponse) GetTotalRevenueOk() (*string, bool)`

GetTotalRevenueOk returns a tuple with the TotalRevenue field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalRevenue

`func (o *RevenueDistributionResponse) SetTotalRevenue(v string)`

SetTotalRevenue sets TotalRevenue field to given value.


### GetEncypherShare

`func (o *RevenueDistributionResponse) GetEncypherShare() string`

GetEncypherShare returns the EncypherShare field if non-nil, zero value otherwise.

### GetEncypherShareOk

`func (o *RevenueDistributionResponse) GetEncypherShareOk() (*string, bool)`

GetEncypherShareOk returns a tuple with the EncypherShare field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEncypherShare

`func (o *RevenueDistributionResponse) SetEncypherShare(v string)`

SetEncypherShare sets EncypherShare field to given value.


### GetMemberPool

`func (o *RevenueDistributionResponse) GetMemberPool() string`

GetMemberPool returns the MemberPool field if non-nil, zero value otherwise.

### GetMemberPoolOk

`func (o *RevenueDistributionResponse) GetMemberPoolOk() (*string, bool)`

GetMemberPoolOk returns a tuple with the MemberPool field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMemberPool

`func (o *RevenueDistributionResponse) SetMemberPool(v string)`

SetMemberPool sets MemberPool field to given value.


### GetStatus

`func (o *RevenueDistributionResponse) GetStatus() DistributionStatus`

GetStatus returns the Status field if non-nil, zero value otherwise.

### GetStatusOk

`func (o *RevenueDistributionResponse) GetStatusOk() (*DistributionStatus, bool)`

GetStatusOk returns a tuple with the Status field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatus

`func (o *RevenueDistributionResponse) SetStatus(v DistributionStatus)`

SetStatus sets Status field to given value.


### GetCreatedAt

`func (o *RevenueDistributionResponse) GetCreatedAt() time.Time`

GetCreatedAt returns the CreatedAt field if non-nil, zero value otherwise.

### GetCreatedAtOk

`func (o *RevenueDistributionResponse) GetCreatedAtOk() (*time.Time, bool)`

GetCreatedAtOk returns a tuple with the CreatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreatedAt

`func (o *RevenueDistributionResponse) SetCreatedAt(v time.Time)`

SetCreatedAt sets CreatedAt field to given value.


### GetProcessedAt

`func (o *RevenueDistributionResponse) GetProcessedAt() time.Time`

GetProcessedAt returns the ProcessedAt field if non-nil, zero value otherwise.

### GetProcessedAtOk

`func (o *RevenueDistributionResponse) GetProcessedAtOk() (*time.Time, bool)`

GetProcessedAtOk returns a tuple with the ProcessedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetProcessedAt

`func (o *RevenueDistributionResponse) SetProcessedAt(v time.Time)`

SetProcessedAt sets ProcessedAt field to given value.


### SetProcessedAtNil

`func (o *RevenueDistributionResponse) SetProcessedAtNil(b bool)`

 SetProcessedAtNil sets the value for ProcessedAt to be an explicit nil

### UnsetProcessedAt
`func (o *RevenueDistributionResponse) UnsetProcessedAt()`

UnsetProcessedAt ensures that no value is present for ProcessedAt, not even an explicit nil
### GetMemberRevenues

`func (o *RevenueDistributionResponse) GetMemberRevenues() []MemberRevenueDetail`

GetMemberRevenues returns the MemberRevenues field if non-nil, zero value otherwise.

### GetMemberRevenuesOk

`func (o *RevenueDistributionResponse) GetMemberRevenuesOk() (*[]MemberRevenueDetail, bool)`

GetMemberRevenuesOk returns a tuple with the MemberRevenues field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMemberRevenues

`func (o *RevenueDistributionResponse) SetMemberRevenues(v []MemberRevenueDetail)`

SetMemberRevenues sets MemberRevenues field to given value.

### HasMemberRevenues

`func (o *RevenueDistributionResponse) HasMemberRevenues() bool`

HasMemberRevenues returns a boolean if a field has been set.

### SetMemberRevenuesNil

`func (o *RevenueDistributionResponse) SetMemberRevenuesNil(b bool)`

 SetMemberRevenuesNil sets the value for MemberRevenues to be an explicit nil

### UnsetMemberRevenues
`func (o *RevenueDistributionResponse) UnsetMemberRevenues()`

UnsetMemberRevenues ensures that no value is present for MemberRevenues, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


