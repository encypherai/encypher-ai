# RevokeRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Reason** | [**RevocationReason**](RevocationReason.md) | Revocation reason code | 
**ReasonDetail** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewRevokeRequest

`func NewRevokeRequest(reason RevocationReason, ) *RevokeRequest`

NewRevokeRequest instantiates a new RevokeRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewRevokeRequestWithDefaults

`func NewRevokeRequestWithDefaults() *RevokeRequest`

NewRevokeRequestWithDefaults instantiates a new RevokeRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetReason

`func (o *RevokeRequest) GetReason() RevocationReason`

GetReason returns the Reason field if non-nil, zero value otherwise.

### GetReasonOk

`func (o *RevokeRequest) GetReasonOk() (*RevocationReason, bool)`

GetReasonOk returns a tuple with the Reason field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetReason

`func (o *RevokeRequest) SetReason(v RevocationReason)`

SetReason sets Reason field to given value.


### GetReasonDetail

`func (o *RevokeRequest) GetReasonDetail() string`

GetReasonDetail returns the ReasonDetail field if non-nil, zero value otherwise.

### GetReasonDetailOk

`func (o *RevokeRequest) GetReasonDetailOk() (*string, bool)`

GetReasonDetailOk returns a tuple with the ReasonDetail field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetReasonDetail

`func (o *RevokeRequest) SetReasonDetail(v string)`

SetReasonDetail sets ReasonDetail field to given value.

### HasReasonDetail

`func (o *RevokeRequest) HasReasonDetail() bool`

HasReasonDetail returns a boolean if a field has been set.

### SetReasonDetailNil

`func (o *RevokeRequest) SetReasonDetailNil(b bool)`

 SetReasonDetailNil sets the value for ReasonDetail to be an explicit nil

### UnsetReasonDetail
`func (o *RevokeRequest) UnsetReasonDetail()`

UnsetReasonDetail ensures that no value is present for ReasonDetail, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


