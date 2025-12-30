# PublicKeyRegisterRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**PublicKeyPem** | **string** | PEM-encoded public key (Ed25519 or RSA) | 
**KeyName** | Pointer to **NullableString** |  | [optional] 
**KeyAlgorithm** | Pointer to **string** | Key algorithm (Ed25519, RSA-2048, RSA-4096) | [optional] [default to "Ed25519"]

## Methods

### NewPublicKeyRegisterRequest

`func NewPublicKeyRegisterRequest(publicKeyPem string, ) *PublicKeyRegisterRequest`

NewPublicKeyRegisterRequest instantiates a new PublicKeyRegisterRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewPublicKeyRegisterRequestWithDefaults

`func NewPublicKeyRegisterRequestWithDefaults() *PublicKeyRegisterRequest`

NewPublicKeyRegisterRequestWithDefaults instantiates a new PublicKeyRegisterRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetPublicKeyPem

`func (o *PublicKeyRegisterRequest) GetPublicKeyPem() string`

GetPublicKeyPem returns the PublicKeyPem field if non-nil, zero value otherwise.

### GetPublicKeyPemOk

`func (o *PublicKeyRegisterRequest) GetPublicKeyPemOk() (*string, bool)`

GetPublicKeyPemOk returns a tuple with the PublicKeyPem field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPublicKeyPem

`func (o *PublicKeyRegisterRequest) SetPublicKeyPem(v string)`

SetPublicKeyPem sets PublicKeyPem field to given value.


### GetKeyName

`func (o *PublicKeyRegisterRequest) GetKeyName() string`

GetKeyName returns the KeyName field if non-nil, zero value otherwise.

### GetKeyNameOk

`func (o *PublicKeyRegisterRequest) GetKeyNameOk() (*string, bool)`

GetKeyNameOk returns a tuple with the KeyName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetKeyName

`func (o *PublicKeyRegisterRequest) SetKeyName(v string)`

SetKeyName sets KeyName field to given value.

### HasKeyName

`func (o *PublicKeyRegisterRequest) HasKeyName() bool`

HasKeyName returns a boolean if a field has been set.

### SetKeyNameNil

`func (o *PublicKeyRegisterRequest) SetKeyNameNil(b bool)`

 SetKeyNameNil sets the value for KeyName to be an explicit nil

### UnsetKeyName
`func (o *PublicKeyRegisterRequest) UnsetKeyName()`

UnsetKeyName ensures that no value is present for KeyName, not even an explicit nil
### GetKeyAlgorithm

`func (o *PublicKeyRegisterRequest) GetKeyAlgorithm() string`

GetKeyAlgorithm returns the KeyAlgorithm field if non-nil, zero value otherwise.

### GetKeyAlgorithmOk

`func (o *PublicKeyRegisterRequest) GetKeyAlgorithmOk() (*string, bool)`

GetKeyAlgorithmOk returns a tuple with the KeyAlgorithm field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetKeyAlgorithm

`func (o *PublicKeyRegisterRequest) SetKeyAlgorithm(v string)`

SetKeyAlgorithm sets KeyAlgorithm field to given value.

### HasKeyAlgorithm

`func (o *PublicKeyRegisterRequest) HasKeyAlgorithm() bool`

HasKeyAlgorithm returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


