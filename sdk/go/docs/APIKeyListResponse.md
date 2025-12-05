# APIKeyListResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Keys** | **[]map[string]interface{}** | List of API keys | 
**Total** | **int32** | Total number of keys | 

## Methods

### NewAPIKeyListResponse

`func NewAPIKeyListResponse(keys []map[string]interface{}, total int32, ) *APIKeyListResponse`

NewAPIKeyListResponse instantiates a new APIKeyListResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewAPIKeyListResponseWithDefaults

`func NewAPIKeyListResponseWithDefaults() *APIKeyListResponse`

NewAPIKeyListResponseWithDefaults instantiates a new APIKeyListResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetKeys

`func (o *APIKeyListResponse) GetKeys() []map[string]interface{}`

GetKeys returns the Keys field if non-nil, zero value otherwise.

### GetKeysOk

`func (o *APIKeyListResponse) GetKeysOk() (*[]map[string]interface{}, bool)`

GetKeysOk returns a tuple with the Keys field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetKeys

`func (o *APIKeyListResponse) SetKeys(v []map[string]interface{})`

SetKeys sets Keys field to given value.


### GetTotal

`func (o *APIKeyListResponse) GetTotal() int32`

GetTotal returns the Total field if non-nil, zero value otherwise.

### GetTotalOk

`func (o *APIKeyListResponse) GetTotalOk() (*int32, bool)`

GetTotalOk returns a tuple with the Total field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotal

`func (o *APIKeyListResponse) SetTotal(v int32)`

SetTotal sets Total field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


