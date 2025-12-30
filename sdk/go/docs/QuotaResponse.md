# QuotaResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | Pointer to **bool** |  | [optional] [default to true]
**Data** | [**QuotaInfo**](QuotaInfo.md) |  | 

## Methods

### NewQuotaResponse

`func NewQuotaResponse(data QuotaInfo, ) *QuotaResponse`

NewQuotaResponse instantiates a new QuotaResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewQuotaResponseWithDefaults

`func NewQuotaResponseWithDefaults() *QuotaResponse`

NewQuotaResponseWithDefaults instantiates a new QuotaResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *QuotaResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *QuotaResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *QuotaResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.

### HasSuccess

`func (o *QuotaResponse) HasSuccess() bool`

HasSuccess returns a boolean if a field has been set.

### GetData

`func (o *QuotaResponse) GetData() QuotaInfo`

GetData returns the Data field if non-nil, zero value otherwise.

### GetDataOk

`func (o *QuotaResponse) GetDataOk() (*QuotaInfo, bool)`

GetDataOk returns a tuple with the Data field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetData

`func (o *QuotaResponse) SetData(v QuotaInfo)`

SetData sets Data field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


