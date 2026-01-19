# BatchVerifyRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**References** | [**[]VerifyEmbeddingRequest**](VerifyEmbeddingRequest.md) | List of embeddings to verify | 

## Methods

### NewBatchVerifyRequest

`func NewBatchVerifyRequest(references []VerifyEmbeddingRequest, ) *BatchVerifyRequest`

NewBatchVerifyRequest instantiates a new BatchVerifyRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewBatchVerifyRequestWithDefaults

`func NewBatchVerifyRequestWithDefaults() *BatchVerifyRequest`

NewBatchVerifyRequestWithDefaults instantiates a new BatchVerifyRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetReferences

`func (o *BatchVerifyRequest) GetReferences() []VerifyEmbeddingRequest`

GetReferences returns the References field if non-nil, zero value otherwise.

### GetReferencesOk

`func (o *BatchVerifyRequest) GetReferencesOk() (*[]VerifyEmbeddingRequest, bool)`

GetReferencesOk returns a tuple with the References field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetReferences

`func (o *BatchVerifyRequest) SetReferences(v []VerifyEmbeddingRequest)`

SetReferences sets References field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


