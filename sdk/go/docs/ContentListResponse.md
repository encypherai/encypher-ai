# ContentListResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Content** | [**[]ContentMetadata**](ContentMetadata.md) |  | 
**Total** | **int32** |  | 
**QuotaRemaining** | Pointer to **NullableInt32** |  | [optional] 

## Methods

### NewContentListResponse

`func NewContentListResponse(content []ContentMetadata, total int32, ) *ContentListResponse`

NewContentListResponse instantiates a new ContentListResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewContentListResponseWithDefaults

`func NewContentListResponseWithDefaults() *ContentListResponse`

NewContentListResponseWithDefaults instantiates a new ContentListResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetContent

`func (o *ContentListResponse) GetContent() []ContentMetadata`

GetContent returns the Content field if non-nil, zero value otherwise.

### GetContentOk

`func (o *ContentListResponse) GetContentOk() (*[]ContentMetadata, bool)`

GetContentOk returns a tuple with the Content field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetContent

`func (o *ContentListResponse) SetContent(v []ContentMetadata)`

SetContent sets Content field to given value.


### GetTotal

`func (o *ContentListResponse) GetTotal() int32`

GetTotal returns the Total field if non-nil, zero value otherwise.

### GetTotalOk

`func (o *ContentListResponse) GetTotalOk() (*int32, bool)`

GetTotalOk returns a tuple with the Total field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotal

`func (o *ContentListResponse) SetTotal(v int32)`

SetTotal sets Total field to given value.


### GetQuotaRemaining

`func (o *ContentListResponse) GetQuotaRemaining() int32`

GetQuotaRemaining returns the QuotaRemaining field if non-nil, zero value otherwise.

### GetQuotaRemainingOk

`func (o *ContentListResponse) GetQuotaRemainingOk() (*int32, bool)`

GetQuotaRemainingOk returns a tuple with the QuotaRemaining field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetQuotaRemaining

`func (o *ContentListResponse) SetQuotaRemaining(v int32)`

SetQuotaRemaining sets QuotaRemaining field to given value.

### HasQuotaRemaining

`func (o *ContentListResponse) HasQuotaRemaining() bool`

HasQuotaRemaining returns a boolean if a field has been set.

### SetQuotaRemainingNil

`func (o *ContentListResponse) SetQuotaRemainingNil(b bool)`

 SetQuotaRemainingNil sets the value for QuotaRemaining to be an explicit nil

### UnsetQuotaRemaining
`func (o *ContentListResponse) UnsetQuotaRemaining()`

UnsetQuotaRemaining ensures that no value is present for QuotaRemaining, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


