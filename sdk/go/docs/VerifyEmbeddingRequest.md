# VerifyEmbeddingRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**RefId** | **string** | Reference ID (8 hex characters) | 
**Signature** | **string** | Signature (8+ hex characters) | 

## Methods

### NewVerifyEmbeddingRequest

`func NewVerifyEmbeddingRequest(refId string, signature string, ) *VerifyEmbeddingRequest`

NewVerifyEmbeddingRequest instantiates a new VerifyEmbeddingRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewVerifyEmbeddingRequestWithDefaults

`func NewVerifyEmbeddingRequestWithDefaults() *VerifyEmbeddingRequest`

NewVerifyEmbeddingRequestWithDefaults instantiates a new VerifyEmbeddingRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetRefId

`func (o *VerifyEmbeddingRequest) GetRefId() string`

GetRefId returns the RefId field if non-nil, zero value otherwise.

### GetRefIdOk

`func (o *VerifyEmbeddingRequest) GetRefIdOk() (*string, bool)`

GetRefIdOk returns a tuple with the RefId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRefId

`func (o *VerifyEmbeddingRequest) SetRefId(v string)`

SetRefId sets RefId field to given value.


### GetSignature

`func (o *VerifyEmbeddingRequest) GetSignature() string`

GetSignature returns the Signature field if non-nil, zero value otherwise.

### GetSignatureOk

`func (o *VerifyEmbeddingRequest) GetSignatureOk() (*string, bool)`

GetSignatureOk returns a tuple with the Signature field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignature

`func (o *VerifyEmbeddingRequest) SetSignature(v string)`

SetSignature sets Signature field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


