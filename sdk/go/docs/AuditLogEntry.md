# AuditLogEntry

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | **string** |  | 
**Timestamp** | **string** |  | 
**Action** | **string** |  | 
**ActorId** | **string** |  | 
**ActorType** | **string** |  | 
**ResourceType** | **string** |  | 
**ResourceId** | Pointer to **NullableString** |  | [optional] 
**Details** | Pointer to **map[string]interface{}** |  | [optional] 
**IpAddress** | Pointer to **NullableString** |  | [optional] 
**UserAgent** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewAuditLogEntry

`func NewAuditLogEntry(id string, timestamp string, action string, actorId string, actorType string, resourceType string, ) *AuditLogEntry`

NewAuditLogEntry instantiates a new AuditLogEntry object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewAuditLogEntryWithDefaults

`func NewAuditLogEntryWithDefaults() *AuditLogEntry`

NewAuditLogEntryWithDefaults instantiates a new AuditLogEntry object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *AuditLogEntry) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *AuditLogEntry) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *AuditLogEntry) SetId(v string)`

SetId sets Id field to given value.


### GetTimestamp

`func (o *AuditLogEntry) GetTimestamp() string`

GetTimestamp returns the Timestamp field if non-nil, zero value otherwise.

### GetTimestampOk

`func (o *AuditLogEntry) GetTimestampOk() (*string, bool)`

GetTimestampOk returns a tuple with the Timestamp field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTimestamp

`func (o *AuditLogEntry) SetTimestamp(v string)`

SetTimestamp sets Timestamp field to given value.


### GetAction

`func (o *AuditLogEntry) GetAction() string`

GetAction returns the Action field if non-nil, zero value otherwise.

### GetActionOk

`func (o *AuditLogEntry) GetActionOk() (*string, bool)`

GetActionOk returns a tuple with the Action field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAction

`func (o *AuditLogEntry) SetAction(v string)`

SetAction sets Action field to given value.


### GetActorId

`func (o *AuditLogEntry) GetActorId() string`

GetActorId returns the ActorId field if non-nil, zero value otherwise.

### GetActorIdOk

`func (o *AuditLogEntry) GetActorIdOk() (*string, bool)`

GetActorIdOk returns a tuple with the ActorId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetActorId

`func (o *AuditLogEntry) SetActorId(v string)`

SetActorId sets ActorId field to given value.


### GetActorType

`func (o *AuditLogEntry) GetActorType() string`

GetActorType returns the ActorType field if non-nil, zero value otherwise.

### GetActorTypeOk

`func (o *AuditLogEntry) GetActorTypeOk() (*string, bool)`

GetActorTypeOk returns a tuple with the ActorType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetActorType

`func (o *AuditLogEntry) SetActorType(v string)`

SetActorType sets ActorType field to given value.


### GetResourceType

`func (o *AuditLogEntry) GetResourceType() string`

GetResourceType returns the ResourceType field if non-nil, zero value otherwise.

### GetResourceTypeOk

`func (o *AuditLogEntry) GetResourceTypeOk() (*string, bool)`

GetResourceTypeOk returns a tuple with the ResourceType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetResourceType

`func (o *AuditLogEntry) SetResourceType(v string)`

SetResourceType sets ResourceType field to given value.


### GetResourceId

`func (o *AuditLogEntry) GetResourceId() string`

GetResourceId returns the ResourceId field if non-nil, zero value otherwise.

### GetResourceIdOk

`func (o *AuditLogEntry) GetResourceIdOk() (*string, bool)`

GetResourceIdOk returns a tuple with the ResourceId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetResourceId

`func (o *AuditLogEntry) SetResourceId(v string)`

SetResourceId sets ResourceId field to given value.

### HasResourceId

`func (o *AuditLogEntry) HasResourceId() bool`

HasResourceId returns a boolean if a field has been set.

### SetResourceIdNil

`func (o *AuditLogEntry) SetResourceIdNil(b bool)`

 SetResourceIdNil sets the value for ResourceId to be an explicit nil

### UnsetResourceId
`func (o *AuditLogEntry) UnsetResourceId()`

UnsetResourceId ensures that no value is present for ResourceId, not even an explicit nil
### GetDetails

`func (o *AuditLogEntry) GetDetails() map[string]interface{}`

GetDetails returns the Details field if non-nil, zero value otherwise.

### GetDetailsOk

`func (o *AuditLogEntry) GetDetailsOk() (*map[string]interface{}, bool)`

GetDetailsOk returns a tuple with the Details field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDetails

`func (o *AuditLogEntry) SetDetails(v map[string]interface{})`

SetDetails sets Details field to given value.

### HasDetails

`func (o *AuditLogEntry) HasDetails() bool`

HasDetails returns a boolean if a field has been set.

### SetDetailsNil

`func (o *AuditLogEntry) SetDetailsNil(b bool)`

 SetDetailsNil sets the value for Details to be an explicit nil

### UnsetDetails
`func (o *AuditLogEntry) UnsetDetails()`

UnsetDetails ensures that no value is present for Details, not even an explicit nil
### GetIpAddress

`func (o *AuditLogEntry) GetIpAddress() string`

GetIpAddress returns the IpAddress field if non-nil, zero value otherwise.

### GetIpAddressOk

`func (o *AuditLogEntry) GetIpAddressOk() (*string, bool)`

GetIpAddressOk returns a tuple with the IpAddress field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIpAddress

`func (o *AuditLogEntry) SetIpAddress(v string)`

SetIpAddress sets IpAddress field to given value.

### HasIpAddress

`func (o *AuditLogEntry) HasIpAddress() bool`

HasIpAddress returns a boolean if a field has been set.

### SetIpAddressNil

`func (o *AuditLogEntry) SetIpAddressNil(b bool)`

 SetIpAddressNil sets the value for IpAddress to be an explicit nil

### UnsetIpAddress
`func (o *AuditLogEntry) UnsetIpAddress()`

UnsetIpAddress ensures that no value is present for IpAddress, not even an explicit nil
### GetUserAgent

`func (o *AuditLogEntry) GetUserAgent() string`

GetUserAgent returns the UserAgent field if non-nil, zero value otherwise.

### GetUserAgentOk

`func (o *AuditLogEntry) GetUserAgentOk() (*string, bool)`

GetUserAgentOk returns a tuple with the UserAgent field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUserAgent

`func (o *AuditLogEntry) SetUserAgent(v string)`

SetUserAgent sets UserAgent field to given value.

### HasUserAgent

`func (o *AuditLogEntry) HasUserAgent() bool`

HasUserAgent returns a boolean if a field has been set.

### SetUserAgentNil

`func (o *AuditLogEntry) SetUserAgentNil(b bool)`

 SetUserAgentNil sets the value for UserAgent to be an explicit nil

### UnsetUserAgent
`func (o *AuditLogEntry) UnsetUserAgent()`

UnsetUserAgent ensures that no value is present for UserAgent, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


