# SignatureVerify

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Content** | **string** |  | 
**Signature** | **string** |  | 
**PublicKeyPem** | **string** |  | 

## Methods

### NewSignatureVerify

`func NewSignatureVerify(content string, signature string, publicKeyPem string, ) *SignatureVerify`

NewSignatureVerify instantiates a new SignatureVerify object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewSignatureVerifyWithDefaults

`func NewSignatureVerifyWithDefaults() *SignatureVerify`

NewSignatureVerifyWithDefaults instantiates a new SignatureVerify object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetContent

`func (o *SignatureVerify) GetContent() string`

GetContent returns the Content field if non-nil, zero value otherwise.

### GetContentOk

`func (o *SignatureVerify) GetContentOk() (*string, bool)`

GetContentOk returns a tuple with the Content field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetContent

`func (o *SignatureVerify) SetContent(v string)`

SetContent sets Content field to given value.


### GetSignature

`func (o *SignatureVerify) GetSignature() string`

GetSignature returns the Signature field if non-nil, zero value otherwise.

### GetSignatureOk

`func (o *SignatureVerify) GetSignatureOk() (*string, bool)`

GetSignatureOk returns a tuple with the Signature field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignature

`func (o *SignatureVerify) SetSignature(v string)`

SetSignature sets Signature field to given value.


### GetPublicKeyPem

`func (o *SignatureVerify) GetPublicKeyPem() string`

GetPublicKeyPem returns the PublicKeyPem field if non-nil, zero value otherwise.

### GetPublicKeyPemOk

`func (o *SignatureVerify) GetPublicKeyPemOk() (*string, bool)`

GetPublicKeyPemOk returns a tuple with the PublicKeyPem field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPublicKeyPem

`func (o *SignatureVerify) SetPublicKeyPem(v string)`

SetPublicKeyPem sets PublicKeyPem field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


