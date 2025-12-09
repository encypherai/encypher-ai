# CoalitionDashboardResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**OrganizationId** | **string** |  | 
**Tier** | **string** |  | 
**PublisherSharePercent** | **int32** |  | 
**CoalitionMember** | **bool** |  | 
**OptedOut** | **bool** |  | 
**CurrentPeriod** | [**ContentStats**](ContentStats.md) |  | 
**LifetimeEarningsCents** | **int32** |  | 
**PendingEarningsCents** | **int32** |  | 
**PaidEarningsCents** | **int32** |  | 
**RecentEarnings** | [**[]EarningsSummary**](EarningsSummary.md) |  | 
**RecentPayouts** | [**[]PayoutSummary**](PayoutSummary.md) |  | 

## Methods

### NewCoalitionDashboardResponse

`func NewCoalitionDashboardResponse(organizationId string, tier string, publisherSharePercent int32, coalitionMember bool, optedOut bool, currentPeriod ContentStats, lifetimeEarningsCents int32, pendingEarningsCents int32, paidEarningsCents int32, recentEarnings []EarningsSummary, recentPayouts []PayoutSummary, ) *CoalitionDashboardResponse`

NewCoalitionDashboardResponse instantiates a new CoalitionDashboardResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewCoalitionDashboardResponseWithDefaults

`func NewCoalitionDashboardResponseWithDefaults() *CoalitionDashboardResponse`

NewCoalitionDashboardResponseWithDefaults instantiates a new CoalitionDashboardResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetOrganizationId

`func (o *CoalitionDashboardResponse) GetOrganizationId() string`

GetOrganizationId returns the OrganizationId field if non-nil, zero value otherwise.

### GetOrganizationIdOk

`func (o *CoalitionDashboardResponse) GetOrganizationIdOk() (*string, bool)`

GetOrganizationIdOk returns a tuple with the OrganizationId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationId

`func (o *CoalitionDashboardResponse) SetOrganizationId(v string)`

SetOrganizationId sets OrganizationId field to given value.


### GetTier

`func (o *CoalitionDashboardResponse) GetTier() string`

GetTier returns the Tier field if non-nil, zero value otherwise.

### GetTierOk

`func (o *CoalitionDashboardResponse) GetTierOk() (*string, bool)`

GetTierOk returns a tuple with the Tier field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTier

`func (o *CoalitionDashboardResponse) SetTier(v string)`

SetTier sets Tier field to given value.


### GetPublisherSharePercent

`func (o *CoalitionDashboardResponse) GetPublisherSharePercent() int32`

GetPublisherSharePercent returns the PublisherSharePercent field if non-nil, zero value otherwise.

### GetPublisherSharePercentOk

`func (o *CoalitionDashboardResponse) GetPublisherSharePercentOk() (*int32, bool)`

GetPublisherSharePercentOk returns a tuple with the PublisherSharePercent field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPublisherSharePercent

`func (o *CoalitionDashboardResponse) SetPublisherSharePercent(v int32)`

SetPublisherSharePercent sets PublisherSharePercent field to given value.


### GetCoalitionMember

`func (o *CoalitionDashboardResponse) GetCoalitionMember() bool`

GetCoalitionMember returns the CoalitionMember field if non-nil, zero value otherwise.

### GetCoalitionMemberOk

`func (o *CoalitionDashboardResponse) GetCoalitionMemberOk() (*bool, bool)`

GetCoalitionMemberOk returns a tuple with the CoalitionMember field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCoalitionMember

`func (o *CoalitionDashboardResponse) SetCoalitionMember(v bool)`

SetCoalitionMember sets CoalitionMember field to given value.


### GetOptedOut

`func (o *CoalitionDashboardResponse) GetOptedOut() bool`

GetOptedOut returns the OptedOut field if non-nil, zero value otherwise.

### GetOptedOutOk

`func (o *CoalitionDashboardResponse) GetOptedOutOk() (*bool, bool)`

GetOptedOutOk returns a tuple with the OptedOut field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOptedOut

`func (o *CoalitionDashboardResponse) SetOptedOut(v bool)`

SetOptedOut sets OptedOut field to given value.


### GetCurrentPeriod

`func (o *CoalitionDashboardResponse) GetCurrentPeriod() ContentStats`

GetCurrentPeriod returns the CurrentPeriod field if non-nil, zero value otherwise.

### GetCurrentPeriodOk

`func (o *CoalitionDashboardResponse) GetCurrentPeriodOk() (*ContentStats, bool)`

GetCurrentPeriodOk returns a tuple with the CurrentPeriod field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCurrentPeriod

`func (o *CoalitionDashboardResponse) SetCurrentPeriod(v ContentStats)`

SetCurrentPeriod sets CurrentPeriod field to given value.


### GetLifetimeEarningsCents

`func (o *CoalitionDashboardResponse) GetLifetimeEarningsCents() int32`

GetLifetimeEarningsCents returns the LifetimeEarningsCents field if non-nil, zero value otherwise.

### GetLifetimeEarningsCentsOk

`func (o *CoalitionDashboardResponse) GetLifetimeEarningsCentsOk() (*int32, bool)`

GetLifetimeEarningsCentsOk returns a tuple with the LifetimeEarningsCents field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLifetimeEarningsCents

`func (o *CoalitionDashboardResponse) SetLifetimeEarningsCents(v int32)`

SetLifetimeEarningsCents sets LifetimeEarningsCents field to given value.


### GetPendingEarningsCents

`func (o *CoalitionDashboardResponse) GetPendingEarningsCents() int32`

GetPendingEarningsCents returns the PendingEarningsCents field if non-nil, zero value otherwise.

### GetPendingEarningsCentsOk

`func (o *CoalitionDashboardResponse) GetPendingEarningsCentsOk() (*int32, bool)`

GetPendingEarningsCentsOk returns a tuple with the PendingEarningsCents field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPendingEarningsCents

`func (o *CoalitionDashboardResponse) SetPendingEarningsCents(v int32)`

SetPendingEarningsCents sets PendingEarningsCents field to given value.


### GetPaidEarningsCents

`func (o *CoalitionDashboardResponse) GetPaidEarningsCents() int32`

GetPaidEarningsCents returns the PaidEarningsCents field if non-nil, zero value otherwise.

### GetPaidEarningsCentsOk

`func (o *CoalitionDashboardResponse) GetPaidEarningsCentsOk() (*int32, bool)`

GetPaidEarningsCentsOk returns a tuple with the PaidEarningsCents field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPaidEarningsCents

`func (o *CoalitionDashboardResponse) SetPaidEarningsCents(v int32)`

SetPaidEarningsCents sets PaidEarningsCents field to given value.


### GetRecentEarnings

`func (o *CoalitionDashboardResponse) GetRecentEarnings() []EarningsSummary`

GetRecentEarnings returns the RecentEarnings field if non-nil, zero value otherwise.

### GetRecentEarningsOk

`func (o *CoalitionDashboardResponse) GetRecentEarningsOk() (*[]EarningsSummary, bool)`

GetRecentEarningsOk returns a tuple with the RecentEarnings field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRecentEarnings

`func (o *CoalitionDashboardResponse) SetRecentEarnings(v []EarningsSummary)`

SetRecentEarnings sets RecentEarnings field to given value.


### GetRecentPayouts

`func (o *CoalitionDashboardResponse) GetRecentPayouts() []PayoutSummary`

GetRecentPayouts returns the RecentPayouts field if non-nil, zero value otherwise.

### GetRecentPayoutsOk

`func (o *CoalitionDashboardResponse) GetRecentPayoutsOk() (*[]PayoutSummary, bool)`

GetRecentPayoutsOk returns a tuple with the RecentPayouts field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRecentPayouts

`func (o *CoalitionDashboardResponse) SetRecentPayouts(v []PayoutSummary)`

SetRecentPayouts sets RecentPayouts field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


