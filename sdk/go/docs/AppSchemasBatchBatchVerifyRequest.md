# AppSchemasBatchBatchVerifyRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Mode** | **string** | Processing mode: &#39;c2pa&#39; or &#39;embeddings&#39; | 
**SegmentationLevel** | Pointer to **NullableString** |  | [optional] 
**IdempotencyKey** | **string** | Caller-supplied key used to deduplicate retries | 
**Items** | [**[]BatchItemPayload**](BatchItemPayload.md) | Documents to process (max 100) | 
**FailFast** | Pointer to **bool** | Abort remaining items upon the first error when set to true | [optional] [default to false]

## Methods

### NewAppSchemasBatchBatchVerifyRequest

`func NewAppSchemasBatchBatchVerifyRequest(mode string, idempotencyKey string, items []BatchItemPayload, ) *AppSchemasBatchBatchVerifyRequest`

NewAppSchemasBatchBatchVerifyRequest instantiates a new AppSchemasBatchBatchVerifyRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewAppSchemasBatchBatchVerifyRequestWithDefaults

`func NewAppSchemasBatchBatchVerifyRequestWithDefaults() *AppSchemasBatchBatchVerifyRequest`

NewAppSchemasBatchBatchVerifyRequestWithDefaults instantiates a new AppSchemasBatchBatchVerifyRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetMode

`func (o *AppSchemasBatchBatchVerifyRequest) GetMode() string`

GetMode returns the Mode field if non-nil, zero value otherwise.

### GetModeOk

`func (o *AppSchemasBatchBatchVerifyRequest) GetModeOk() (*string, bool)`

GetModeOk returns a tuple with the Mode field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMode

`func (o *AppSchemasBatchBatchVerifyRequest) SetMode(v string)`

SetMode sets Mode field to given value.


### GetSegmentationLevel

`func (o *AppSchemasBatchBatchVerifyRequest) GetSegmentationLevel() string`

GetSegmentationLevel returns the SegmentationLevel field if non-nil, zero value otherwise.

### GetSegmentationLevelOk

`func (o *AppSchemasBatchBatchVerifyRequest) GetSegmentationLevelOk() (*string, bool)`

GetSegmentationLevelOk returns a tuple with the SegmentationLevel field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSegmentationLevel

`func (o *AppSchemasBatchBatchVerifyRequest) SetSegmentationLevel(v string)`

SetSegmentationLevel sets SegmentationLevel field to given value.

### HasSegmentationLevel

`func (o *AppSchemasBatchBatchVerifyRequest) HasSegmentationLevel() bool`

HasSegmentationLevel returns a boolean if a field has been set.

### SetSegmentationLevelNil

`func (o *AppSchemasBatchBatchVerifyRequest) SetSegmentationLevelNil(b bool)`

 SetSegmentationLevelNil sets the value for SegmentationLevel to be an explicit nil

### UnsetSegmentationLevel
`func (o *AppSchemasBatchBatchVerifyRequest) UnsetSegmentationLevel()`

UnsetSegmentationLevel ensures that no value is present for SegmentationLevel, not even an explicit nil
### GetIdempotencyKey

`func (o *AppSchemasBatchBatchVerifyRequest) GetIdempotencyKey() string`

GetIdempotencyKey returns the IdempotencyKey field if non-nil, zero value otherwise.

### GetIdempotencyKeyOk

`func (o *AppSchemasBatchBatchVerifyRequest) GetIdempotencyKeyOk() (*string, bool)`

GetIdempotencyKeyOk returns a tuple with the IdempotencyKey field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIdempotencyKey

`func (o *AppSchemasBatchBatchVerifyRequest) SetIdempotencyKey(v string)`

SetIdempotencyKey sets IdempotencyKey field to given value.


### GetItems

`func (o *AppSchemasBatchBatchVerifyRequest) GetItems() []BatchItemPayload`

GetItems returns the Items field if non-nil, zero value otherwise.

### GetItemsOk

`func (o *AppSchemasBatchBatchVerifyRequest) GetItemsOk() (*[]BatchItemPayload, bool)`

GetItemsOk returns a tuple with the Items field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetItems

`func (o *AppSchemasBatchBatchVerifyRequest) SetItems(v []BatchItemPayload)`

SetItems sets Items field to given value.


### GetFailFast

`func (o *AppSchemasBatchBatchVerifyRequest) GetFailFast() bool`

GetFailFast returns the FailFast field if non-nil, zero value otherwise.

### GetFailFastOk

`func (o *AppSchemasBatchBatchVerifyRequest) GetFailFastOk() (*bool, bool)`

GetFailFastOk returns a tuple with the FailFast field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFailFast

`func (o *AppSchemasBatchBatchVerifyRequest) SetFailFast(v bool)`

SetFailFast sets FailFast field to given value.

### HasFailFast

`func (o *AppSchemasBatchBatchVerifyRequest) HasFailFast() bool`

HasFailFast returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


