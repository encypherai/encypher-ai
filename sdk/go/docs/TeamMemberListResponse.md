# TeamMemberListResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**OrganizationId** | **string** |  | 
**Members** | [**[]TeamMember**](TeamMember.md) |  | 
**Total** | **int32** |  | 
**MaxMembers** | **int32** |  | 

## Methods

### NewTeamMemberListResponse

`func NewTeamMemberListResponse(organizationId string, members []TeamMember, total int32, maxMembers int32, ) *TeamMemberListResponse`

NewTeamMemberListResponse instantiates a new TeamMemberListResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewTeamMemberListResponseWithDefaults

`func NewTeamMemberListResponseWithDefaults() *TeamMemberListResponse`

NewTeamMemberListResponseWithDefaults instantiates a new TeamMemberListResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetOrganizationId

`func (o *TeamMemberListResponse) GetOrganizationId() string`

GetOrganizationId returns the OrganizationId field if non-nil, zero value otherwise.

### GetOrganizationIdOk

`func (o *TeamMemberListResponse) GetOrganizationIdOk() (*string, bool)`

GetOrganizationIdOk returns a tuple with the OrganizationId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationId

`func (o *TeamMemberListResponse) SetOrganizationId(v string)`

SetOrganizationId sets OrganizationId field to given value.


### GetMembers

`func (o *TeamMemberListResponse) GetMembers() []TeamMember`

GetMembers returns the Members field if non-nil, zero value otherwise.

### GetMembersOk

`func (o *TeamMemberListResponse) GetMembersOk() (*[]TeamMember, bool)`

GetMembersOk returns a tuple with the Members field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMembers

`func (o *TeamMemberListResponse) SetMembers(v []TeamMember)`

SetMembers sets Members field to given value.


### GetTotal

`func (o *TeamMemberListResponse) GetTotal() int32`

GetTotal returns the Total field if non-nil, zero value otherwise.

### GetTotalOk

`func (o *TeamMemberListResponse) GetTotalOk() (*int32, bool)`

GetTotalOk returns a tuple with the Total field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotal

`func (o *TeamMemberListResponse) SetTotal(v int32)`

SetTotal sets Total field to given value.


### GetMaxMembers

`func (o *TeamMemberListResponse) GetMaxMembers() int32`

GetMaxMembers returns the MaxMembers field if non-nil, zero value otherwise.

### GetMaxMembersOk

`func (o *TeamMemberListResponse) GetMaxMembersOk() (*int32, bool)`

GetMaxMembersOk returns a tuple with the MaxMembers field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMaxMembers

`func (o *TeamMemberListResponse) SetMaxMembers(v int32)`

SetMaxMembers sets MaxMembers field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


