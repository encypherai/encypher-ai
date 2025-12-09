# ContentAccessTrack

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ContentId** | **int32** |  | 
**AccessType** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewContentAccessTrack

`func NewContentAccessTrack(contentId int32, ) *ContentAccessTrack`

NewContentAccessTrack instantiates a new ContentAccessTrack object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewContentAccessTrackWithDefaults

`func NewContentAccessTrackWithDefaults() *ContentAccessTrack`

NewContentAccessTrackWithDefaults instantiates a new ContentAccessTrack object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetContentId

`func (o *ContentAccessTrack) GetContentId() int32`

GetContentId returns the ContentId field if non-nil, zero value otherwise.

### GetContentIdOk

`func (o *ContentAccessTrack) GetContentIdOk() (*int32, bool)`

GetContentIdOk returns a tuple with the ContentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetContentId

`func (o *ContentAccessTrack) SetContentId(v int32)`

SetContentId sets ContentId field to given value.


### GetAccessType

`func (o *ContentAccessTrack) GetAccessType() string`

GetAccessType returns the AccessType field if non-nil, zero value otherwise.

### GetAccessTypeOk

`func (o *ContentAccessTrack) GetAccessTypeOk() (*string, bool)`

GetAccessTypeOk returns a tuple with the AccessType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAccessType

`func (o *ContentAccessTrack) SetAccessType(v string)`

SetAccessType sets AccessType field to given value.

### HasAccessType

`func (o *ContentAccessTrack) HasAccessType() bool`

HasAccessType returns a boolean if a field has been set.

### SetAccessTypeNil

`func (o *ContentAccessTrack) SetAccessTypeNil(b bool)`

 SetAccessTypeNil sets the value for AccessType to be an explicit nil

### UnsetAccessType
`func (o *ContentAccessTrack) UnsetAccessType()`

UnsetAccessType ensures that no value is present for AccessType, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


