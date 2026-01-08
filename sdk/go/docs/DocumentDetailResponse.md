# DocumentDetailResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | Pointer to **bool** |  | [optional] [default to true]
**Data** | [**DocumentDetail**](DocumentDetail.md) |  | 

## Methods

### NewDocumentDetailResponse

`func NewDocumentDetailResponse(data DocumentDetail, ) *DocumentDetailResponse`

NewDocumentDetailResponse instantiates a new DocumentDetailResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewDocumentDetailResponseWithDefaults

`func NewDocumentDetailResponseWithDefaults() *DocumentDetailResponse`

NewDocumentDetailResponseWithDefaults instantiates a new DocumentDetailResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *DocumentDetailResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *DocumentDetailResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *DocumentDetailResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.

### HasSuccess

`func (o *DocumentDetailResponse) HasSuccess() bool`

HasSuccess returns a boolean if a field has been set.

### GetData

`func (o *DocumentDetailResponse) GetData() DocumentDetail`

GetData returns the Data field if non-nil, zero value otherwise.

### GetDataOk

`func (o *DocumentDetailResponse) GetDataOk() (*DocumentDetail, bool)`

GetDataOk returns a tuple with the Data field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetData

`func (o *DocumentDetailResponse) SetData(v DocumentDetail)`

SetData sets Data field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


