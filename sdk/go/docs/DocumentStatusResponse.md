# DocumentStatusResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DocumentId** | **string** |  | 
**OrganizationId** | **string** |  | 
**Revoked** | **bool** |  | 
**RevokedAt** | Pointer to **NullableString** |  | [optional] 
**RevokedReason** | Pointer to **NullableString** |  | [optional] 
**RevokedReasonDetail** | Pointer to **NullableString** |  | [optional] 
**ReinstatedAt** | Pointer to **NullableString** |  | [optional] 
**StatusListUrl** | Pointer to **NullableString** |  | [optional] 
**StatusListIndex** | Pointer to **NullableInt32** |  | [optional] 
**StatusBitIndex** | Pointer to **NullableInt32** |  | [optional] 

## Methods

### NewDocumentStatusResponse

`func NewDocumentStatusResponse(documentId string, organizationId string, revoked bool, ) *DocumentStatusResponse`

NewDocumentStatusResponse instantiates a new DocumentStatusResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewDocumentStatusResponseWithDefaults

`func NewDocumentStatusResponseWithDefaults() *DocumentStatusResponse`

NewDocumentStatusResponseWithDefaults instantiates a new DocumentStatusResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDocumentId

`func (o *DocumentStatusResponse) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *DocumentStatusResponse) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *DocumentStatusResponse) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetOrganizationId

`func (o *DocumentStatusResponse) GetOrganizationId() string`

GetOrganizationId returns the OrganizationId field if non-nil, zero value otherwise.

### GetOrganizationIdOk

`func (o *DocumentStatusResponse) GetOrganizationIdOk() (*string, bool)`

GetOrganizationIdOk returns a tuple with the OrganizationId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationId

`func (o *DocumentStatusResponse) SetOrganizationId(v string)`

SetOrganizationId sets OrganizationId field to given value.


### GetRevoked

`func (o *DocumentStatusResponse) GetRevoked() bool`

GetRevoked returns the Revoked field if non-nil, zero value otherwise.

### GetRevokedOk

`func (o *DocumentStatusResponse) GetRevokedOk() (*bool, bool)`

GetRevokedOk returns a tuple with the Revoked field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRevoked

`func (o *DocumentStatusResponse) SetRevoked(v bool)`

SetRevoked sets Revoked field to given value.


### GetRevokedAt

`func (o *DocumentStatusResponse) GetRevokedAt() string`

GetRevokedAt returns the RevokedAt field if non-nil, zero value otherwise.

### GetRevokedAtOk

`func (o *DocumentStatusResponse) GetRevokedAtOk() (*string, bool)`

GetRevokedAtOk returns a tuple with the RevokedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRevokedAt

`func (o *DocumentStatusResponse) SetRevokedAt(v string)`

SetRevokedAt sets RevokedAt field to given value.

### HasRevokedAt

`func (o *DocumentStatusResponse) HasRevokedAt() bool`

HasRevokedAt returns a boolean if a field has been set.

### SetRevokedAtNil

`func (o *DocumentStatusResponse) SetRevokedAtNil(b bool)`

 SetRevokedAtNil sets the value for RevokedAt to be an explicit nil

### UnsetRevokedAt
`func (o *DocumentStatusResponse) UnsetRevokedAt()`

UnsetRevokedAt ensures that no value is present for RevokedAt, not even an explicit nil
### GetRevokedReason

`func (o *DocumentStatusResponse) GetRevokedReason() string`

GetRevokedReason returns the RevokedReason field if non-nil, zero value otherwise.

### GetRevokedReasonOk

`func (o *DocumentStatusResponse) GetRevokedReasonOk() (*string, bool)`

GetRevokedReasonOk returns a tuple with the RevokedReason field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRevokedReason

`func (o *DocumentStatusResponse) SetRevokedReason(v string)`

SetRevokedReason sets RevokedReason field to given value.

### HasRevokedReason

`func (o *DocumentStatusResponse) HasRevokedReason() bool`

HasRevokedReason returns a boolean if a field has been set.

### SetRevokedReasonNil

`func (o *DocumentStatusResponse) SetRevokedReasonNil(b bool)`

 SetRevokedReasonNil sets the value for RevokedReason to be an explicit nil

### UnsetRevokedReason
`func (o *DocumentStatusResponse) UnsetRevokedReason()`

UnsetRevokedReason ensures that no value is present for RevokedReason, not even an explicit nil
### GetRevokedReasonDetail

`func (o *DocumentStatusResponse) GetRevokedReasonDetail() string`

GetRevokedReasonDetail returns the RevokedReasonDetail field if non-nil, zero value otherwise.

### GetRevokedReasonDetailOk

`func (o *DocumentStatusResponse) GetRevokedReasonDetailOk() (*string, bool)`

GetRevokedReasonDetailOk returns a tuple with the RevokedReasonDetail field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRevokedReasonDetail

`func (o *DocumentStatusResponse) SetRevokedReasonDetail(v string)`

SetRevokedReasonDetail sets RevokedReasonDetail field to given value.

### HasRevokedReasonDetail

`func (o *DocumentStatusResponse) HasRevokedReasonDetail() bool`

HasRevokedReasonDetail returns a boolean if a field has been set.

### SetRevokedReasonDetailNil

`func (o *DocumentStatusResponse) SetRevokedReasonDetailNil(b bool)`

 SetRevokedReasonDetailNil sets the value for RevokedReasonDetail to be an explicit nil

### UnsetRevokedReasonDetail
`func (o *DocumentStatusResponse) UnsetRevokedReasonDetail()`

UnsetRevokedReasonDetail ensures that no value is present for RevokedReasonDetail, not even an explicit nil
### GetReinstatedAt

`func (o *DocumentStatusResponse) GetReinstatedAt() string`

GetReinstatedAt returns the ReinstatedAt field if non-nil, zero value otherwise.

### GetReinstatedAtOk

`func (o *DocumentStatusResponse) GetReinstatedAtOk() (*string, bool)`

GetReinstatedAtOk returns a tuple with the ReinstatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetReinstatedAt

`func (o *DocumentStatusResponse) SetReinstatedAt(v string)`

SetReinstatedAt sets ReinstatedAt field to given value.

### HasReinstatedAt

`func (o *DocumentStatusResponse) HasReinstatedAt() bool`

HasReinstatedAt returns a boolean if a field has been set.

### SetReinstatedAtNil

`func (o *DocumentStatusResponse) SetReinstatedAtNil(b bool)`

 SetReinstatedAtNil sets the value for ReinstatedAt to be an explicit nil

### UnsetReinstatedAt
`func (o *DocumentStatusResponse) UnsetReinstatedAt()`

UnsetReinstatedAt ensures that no value is present for ReinstatedAt, not even an explicit nil
### GetStatusListUrl

`func (o *DocumentStatusResponse) GetStatusListUrl() string`

GetStatusListUrl returns the StatusListUrl field if non-nil, zero value otherwise.

### GetStatusListUrlOk

`func (o *DocumentStatusResponse) GetStatusListUrlOk() (*string, bool)`

GetStatusListUrlOk returns a tuple with the StatusListUrl field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatusListUrl

`func (o *DocumentStatusResponse) SetStatusListUrl(v string)`

SetStatusListUrl sets StatusListUrl field to given value.

### HasStatusListUrl

`func (o *DocumentStatusResponse) HasStatusListUrl() bool`

HasStatusListUrl returns a boolean if a field has been set.

### SetStatusListUrlNil

`func (o *DocumentStatusResponse) SetStatusListUrlNil(b bool)`

 SetStatusListUrlNil sets the value for StatusListUrl to be an explicit nil

### UnsetStatusListUrl
`func (o *DocumentStatusResponse) UnsetStatusListUrl()`

UnsetStatusListUrl ensures that no value is present for StatusListUrl, not even an explicit nil
### GetStatusListIndex

`func (o *DocumentStatusResponse) GetStatusListIndex() int32`

GetStatusListIndex returns the StatusListIndex field if non-nil, zero value otherwise.

### GetStatusListIndexOk

`func (o *DocumentStatusResponse) GetStatusListIndexOk() (*int32, bool)`

GetStatusListIndexOk returns a tuple with the StatusListIndex field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatusListIndex

`func (o *DocumentStatusResponse) SetStatusListIndex(v int32)`

SetStatusListIndex sets StatusListIndex field to given value.

### HasStatusListIndex

`func (o *DocumentStatusResponse) HasStatusListIndex() bool`

HasStatusListIndex returns a boolean if a field has been set.

### SetStatusListIndexNil

`func (o *DocumentStatusResponse) SetStatusListIndexNil(b bool)`

 SetStatusListIndexNil sets the value for StatusListIndex to be an explicit nil

### UnsetStatusListIndex
`func (o *DocumentStatusResponse) UnsetStatusListIndex()`

UnsetStatusListIndex ensures that no value is present for StatusListIndex, not even an explicit nil
### GetStatusBitIndex

`func (o *DocumentStatusResponse) GetStatusBitIndex() int32`

GetStatusBitIndex returns the StatusBitIndex field if non-nil, zero value otherwise.

### GetStatusBitIndexOk

`func (o *DocumentStatusResponse) GetStatusBitIndexOk() (*int32, bool)`

GetStatusBitIndexOk returns a tuple with the StatusBitIndex field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetStatusBitIndex

`func (o *DocumentStatusResponse) SetStatusBitIndex(v int32)`

SetStatusBitIndex sets StatusBitIndex field to given value.

### HasStatusBitIndex

`func (o *DocumentStatusResponse) HasStatusBitIndex() bool`

HasStatusBitIndex returns a boolean if a field has been set.

### SetStatusBitIndexNil

`func (o *DocumentStatusResponse) SetStatusBitIndexNil(b bool)`

 SetStatusBitIndexNil sets the value for StatusBitIndex to be an explicit nil

### UnsetStatusBitIndex
`func (o *DocumentStatusResponse) UnsetStatusBitIndex()`

UnsetStatusBitIndex ensures that no value is present for StatusBitIndex, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


