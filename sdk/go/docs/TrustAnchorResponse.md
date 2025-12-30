# TrustAnchorResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**SignerId** | **string** | The signer identifier | 
**SignerName** | **string** | Human-readable signer name | 
**PublicKey** | **string** | PEM-encoded public key | 
**PublicKeyAlgorithm** | Pointer to **string** | Key algorithm | [optional] [default to "Ed25519"]
**KeyId** | Pointer to **NullableString** |  | [optional] 
**IssuedAt** | Pointer to **NullableString** |  | [optional] 
**ExpiresAt** | Pointer to **NullableString** |  | [optional] 
**Revoked** | Pointer to **bool** | Whether the key has been revoked | [optional] [default to false]
**TrustAnchorType** | Pointer to **string** | Type of trust anchor | [optional] [default to "organization"]

## Methods

### NewTrustAnchorResponse

`func NewTrustAnchorResponse(signerId string, signerName string, publicKey string, ) *TrustAnchorResponse`

NewTrustAnchorResponse instantiates a new TrustAnchorResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewTrustAnchorResponseWithDefaults

`func NewTrustAnchorResponseWithDefaults() *TrustAnchorResponse`

NewTrustAnchorResponseWithDefaults instantiates a new TrustAnchorResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSignerId

`func (o *TrustAnchorResponse) GetSignerId() string`

GetSignerId returns the SignerId field if non-nil, zero value otherwise.

### GetSignerIdOk

`func (o *TrustAnchorResponse) GetSignerIdOk() (*string, bool)`

GetSignerIdOk returns a tuple with the SignerId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignerId

`func (o *TrustAnchorResponse) SetSignerId(v string)`

SetSignerId sets SignerId field to given value.


### GetSignerName

`func (o *TrustAnchorResponse) GetSignerName() string`

GetSignerName returns the SignerName field if non-nil, zero value otherwise.

### GetSignerNameOk

`func (o *TrustAnchorResponse) GetSignerNameOk() (*string, bool)`

GetSignerNameOk returns a tuple with the SignerName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignerName

`func (o *TrustAnchorResponse) SetSignerName(v string)`

SetSignerName sets SignerName field to given value.


### GetPublicKey

`func (o *TrustAnchorResponse) GetPublicKey() string`

GetPublicKey returns the PublicKey field if non-nil, zero value otherwise.

### GetPublicKeyOk

`func (o *TrustAnchorResponse) GetPublicKeyOk() (*string, bool)`

GetPublicKeyOk returns a tuple with the PublicKey field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPublicKey

`func (o *TrustAnchorResponse) SetPublicKey(v string)`

SetPublicKey sets PublicKey field to given value.


### GetPublicKeyAlgorithm

`func (o *TrustAnchorResponse) GetPublicKeyAlgorithm() string`

GetPublicKeyAlgorithm returns the PublicKeyAlgorithm field if non-nil, zero value otherwise.

### GetPublicKeyAlgorithmOk

`func (o *TrustAnchorResponse) GetPublicKeyAlgorithmOk() (*string, bool)`

GetPublicKeyAlgorithmOk returns a tuple with the PublicKeyAlgorithm field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPublicKeyAlgorithm

`func (o *TrustAnchorResponse) SetPublicKeyAlgorithm(v string)`

SetPublicKeyAlgorithm sets PublicKeyAlgorithm field to given value.

### HasPublicKeyAlgorithm

`func (o *TrustAnchorResponse) HasPublicKeyAlgorithm() bool`

HasPublicKeyAlgorithm returns a boolean if a field has been set.

### GetKeyId

`func (o *TrustAnchorResponse) GetKeyId() string`

GetKeyId returns the KeyId field if non-nil, zero value otherwise.

### GetKeyIdOk

`func (o *TrustAnchorResponse) GetKeyIdOk() (*string, bool)`

GetKeyIdOk returns a tuple with the KeyId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetKeyId

`func (o *TrustAnchorResponse) SetKeyId(v string)`

SetKeyId sets KeyId field to given value.

### HasKeyId

`func (o *TrustAnchorResponse) HasKeyId() bool`

HasKeyId returns a boolean if a field has been set.

### SetKeyIdNil

`func (o *TrustAnchorResponse) SetKeyIdNil(b bool)`

 SetKeyIdNil sets the value for KeyId to be an explicit nil

### UnsetKeyId
`func (o *TrustAnchorResponse) UnsetKeyId()`

UnsetKeyId ensures that no value is present for KeyId, not even an explicit nil
### GetIssuedAt

`func (o *TrustAnchorResponse) GetIssuedAt() string`

GetIssuedAt returns the IssuedAt field if non-nil, zero value otherwise.

### GetIssuedAtOk

`func (o *TrustAnchorResponse) GetIssuedAtOk() (*string, bool)`

GetIssuedAtOk returns a tuple with the IssuedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIssuedAt

`func (o *TrustAnchorResponse) SetIssuedAt(v string)`

SetIssuedAt sets IssuedAt field to given value.

### HasIssuedAt

`func (o *TrustAnchorResponse) HasIssuedAt() bool`

HasIssuedAt returns a boolean if a field has been set.

### SetIssuedAtNil

`func (o *TrustAnchorResponse) SetIssuedAtNil(b bool)`

 SetIssuedAtNil sets the value for IssuedAt to be an explicit nil

### UnsetIssuedAt
`func (o *TrustAnchorResponse) UnsetIssuedAt()`

UnsetIssuedAt ensures that no value is present for IssuedAt, not even an explicit nil
### GetExpiresAt

`func (o *TrustAnchorResponse) GetExpiresAt() string`

GetExpiresAt returns the ExpiresAt field if non-nil, zero value otherwise.

### GetExpiresAtOk

`func (o *TrustAnchorResponse) GetExpiresAtOk() (*string, bool)`

GetExpiresAtOk returns a tuple with the ExpiresAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetExpiresAt

`func (o *TrustAnchorResponse) SetExpiresAt(v string)`

SetExpiresAt sets ExpiresAt field to given value.

### HasExpiresAt

`func (o *TrustAnchorResponse) HasExpiresAt() bool`

HasExpiresAt returns a boolean if a field has been set.

### SetExpiresAtNil

`func (o *TrustAnchorResponse) SetExpiresAtNil(b bool)`

 SetExpiresAtNil sets the value for ExpiresAt to be an explicit nil

### UnsetExpiresAt
`func (o *TrustAnchorResponse) UnsetExpiresAt()`

UnsetExpiresAt ensures that no value is present for ExpiresAt, not even an explicit nil
### GetRevoked

`func (o *TrustAnchorResponse) GetRevoked() bool`

GetRevoked returns the Revoked field if non-nil, zero value otherwise.

### GetRevokedOk

`func (o *TrustAnchorResponse) GetRevokedOk() (*bool, bool)`

GetRevokedOk returns a tuple with the Revoked field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRevoked

`func (o *TrustAnchorResponse) SetRevoked(v bool)`

SetRevoked sets Revoked field to given value.

### HasRevoked

`func (o *TrustAnchorResponse) HasRevoked() bool`

HasRevoked returns a boolean if a field has been set.

### GetTrustAnchorType

`func (o *TrustAnchorResponse) GetTrustAnchorType() string`

GetTrustAnchorType returns the TrustAnchorType field if non-nil, zero value otherwise.

### GetTrustAnchorTypeOk

`func (o *TrustAnchorResponse) GetTrustAnchorTypeOk() (*string, bool)`

GetTrustAnchorTypeOk returns a tuple with the TrustAnchorType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTrustAnchorType

`func (o *TrustAnchorResponse) SetTrustAnchorType(v string)`

SetTrustAnchorType sets TrustAnchorType field to given value.

### HasTrustAnchorType

`func (o *TrustAnchorResponse) HasTrustAnchorType() bool`

HasTrustAnchorType returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


