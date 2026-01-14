# SignatureVerification

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**SignerId** | **string** | Signer identifier | 
**SignerName** | Pointer to **NullableString** |  | [optional] 
**Algorithm** | **string** | Signature algorithm used | 
**PublicKeyFingerprint** | **string** | Public key fingerprint | 
**SignatureValid** | **bool** | Whether signature is valid | 
**SignedAt** | Pointer to **NullableTime** |  | [optional] 

## Methods

### NewSignatureVerification

`func NewSignatureVerification(signerId string, algorithm string, publicKeyFingerprint string, signatureValid bool, ) *SignatureVerification`

NewSignatureVerification instantiates a new SignatureVerification object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewSignatureVerificationWithDefaults

`func NewSignatureVerificationWithDefaults() *SignatureVerification`

NewSignatureVerificationWithDefaults instantiates a new SignatureVerification object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSignerId

`func (o *SignatureVerification) GetSignerId() string`

GetSignerId returns the SignerId field if non-nil, zero value otherwise.

### GetSignerIdOk

`func (o *SignatureVerification) GetSignerIdOk() (*string, bool)`

GetSignerIdOk returns a tuple with the SignerId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignerId

`func (o *SignatureVerification) SetSignerId(v string)`

SetSignerId sets SignerId field to given value.


### GetSignerName

`func (o *SignatureVerification) GetSignerName() string`

GetSignerName returns the SignerName field if non-nil, zero value otherwise.

### GetSignerNameOk

`func (o *SignatureVerification) GetSignerNameOk() (*string, bool)`

GetSignerNameOk returns a tuple with the SignerName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignerName

`func (o *SignatureVerification) SetSignerName(v string)`

SetSignerName sets SignerName field to given value.

### HasSignerName

`func (o *SignatureVerification) HasSignerName() bool`

HasSignerName returns a boolean if a field has been set.

### SetSignerNameNil

`func (o *SignatureVerification) SetSignerNameNil(b bool)`

 SetSignerNameNil sets the value for SignerName to be an explicit nil

### UnsetSignerName
`func (o *SignatureVerification) UnsetSignerName()`

UnsetSignerName ensures that no value is present for SignerName, not even an explicit nil
### GetAlgorithm

`func (o *SignatureVerification) GetAlgorithm() string`

GetAlgorithm returns the Algorithm field if non-nil, zero value otherwise.

### GetAlgorithmOk

`func (o *SignatureVerification) GetAlgorithmOk() (*string, bool)`

GetAlgorithmOk returns a tuple with the Algorithm field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAlgorithm

`func (o *SignatureVerification) SetAlgorithm(v string)`

SetAlgorithm sets Algorithm field to given value.


### GetPublicKeyFingerprint

`func (o *SignatureVerification) GetPublicKeyFingerprint() string`

GetPublicKeyFingerprint returns the PublicKeyFingerprint field if non-nil, zero value otherwise.

### GetPublicKeyFingerprintOk

`func (o *SignatureVerification) GetPublicKeyFingerprintOk() (*string, bool)`

GetPublicKeyFingerprintOk returns a tuple with the PublicKeyFingerprint field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPublicKeyFingerprint

`func (o *SignatureVerification) SetPublicKeyFingerprint(v string)`

SetPublicKeyFingerprint sets PublicKeyFingerprint field to given value.


### GetSignatureValid

`func (o *SignatureVerification) GetSignatureValid() bool`

GetSignatureValid returns the SignatureValid field if non-nil, zero value otherwise.

### GetSignatureValidOk

`func (o *SignatureVerification) GetSignatureValidOk() (*bool, bool)`

GetSignatureValidOk returns a tuple with the SignatureValid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignatureValid

`func (o *SignatureVerification) SetSignatureValid(v bool)`

SetSignatureValid sets SignatureValid field to given value.


### GetSignedAt

`func (o *SignatureVerification) GetSignedAt() time.Time`

GetSignedAt returns the SignedAt field if non-nil, zero value otherwise.

### GetSignedAtOk

`func (o *SignatureVerification) GetSignedAtOk() (*time.Time, bool)`

GetSignedAtOk returns a tuple with the SignedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignedAt

`func (o *SignatureVerification) SetSignedAt(v time.Time)`

SetSignedAt sets SignedAt field to given value.

### HasSignedAt

`func (o *SignatureVerification) HasSignedAt() bool`

HasSignedAt returns a boolean if a field has been set.

### SetSignedAtNil

`func (o *SignatureVerification) SetSignedAtNil(b bool)`

 SetSignedAtNil sets the value for SignedAt to be an explicit nil

### UnsetSignedAt
`func (o *SignatureVerification) UnsetSignedAt()`

UnsetSignedAt ensures that no value is present for SignedAt, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


