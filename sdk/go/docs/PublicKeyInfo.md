# PublicKeyInfo

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | **string** | Key ID | 
**OrganizationId** | **string** | Organization that owns this key | 
**KeyName** | Pointer to **NullableString** |  | [optional] 
**KeyAlgorithm** | **string** | Key algorithm | 
**KeyFingerprint** | **string** | SHA-256 fingerprint of the public key | 
**PublicKeyPem** | **string** | PEM-encoded public key | 
**IsActive** | Pointer to **bool** | Whether key is active for verification | [optional] [default to true]
**CreatedAt** | **time.Time** | When key was registered | 
**LastUsedAt** | Pointer to **NullableTime** |  | [optional] 

## Methods

### NewPublicKeyInfo

`func NewPublicKeyInfo(id string, organizationId string, keyAlgorithm string, keyFingerprint string, publicKeyPem string, createdAt time.Time, ) *PublicKeyInfo`

NewPublicKeyInfo instantiates a new PublicKeyInfo object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewPublicKeyInfoWithDefaults

`func NewPublicKeyInfoWithDefaults() *PublicKeyInfo`

NewPublicKeyInfoWithDefaults instantiates a new PublicKeyInfo object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *PublicKeyInfo) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *PublicKeyInfo) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *PublicKeyInfo) SetId(v string)`

SetId sets Id field to given value.


### GetOrganizationId

`func (o *PublicKeyInfo) GetOrganizationId() string`

GetOrganizationId returns the OrganizationId field if non-nil, zero value otherwise.

### GetOrganizationIdOk

`func (o *PublicKeyInfo) GetOrganizationIdOk() (*string, bool)`

GetOrganizationIdOk returns a tuple with the OrganizationId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationId

`func (o *PublicKeyInfo) SetOrganizationId(v string)`

SetOrganizationId sets OrganizationId field to given value.


### GetKeyName

`func (o *PublicKeyInfo) GetKeyName() string`

GetKeyName returns the KeyName field if non-nil, zero value otherwise.

### GetKeyNameOk

`func (o *PublicKeyInfo) GetKeyNameOk() (*string, bool)`

GetKeyNameOk returns a tuple with the KeyName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetKeyName

`func (o *PublicKeyInfo) SetKeyName(v string)`

SetKeyName sets KeyName field to given value.

### HasKeyName

`func (o *PublicKeyInfo) HasKeyName() bool`

HasKeyName returns a boolean if a field has been set.

### SetKeyNameNil

`func (o *PublicKeyInfo) SetKeyNameNil(b bool)`

 SetKeyNameNil sets the value for KeyName to be an explicit nil

### UnsetKeyName
`func (o *PublicKeyInfo) UnsetKeyName()`

UnsetKeyName ensures that no value is present for KeyName, not even an explicit nil
### GetKeyAlgorithm

`func (o *PublicKeyInfo) GetKeyAlgorithm() string`

GetKeyAlgorithm returns the KeyAlgorithm field if non-nil, zero value otherwise.

### GetKeyAlgorithmOk

`func (o *PublicKeyInfo) GetKeyAlgorithmOk() (*string, bool)`

GetKeyAlgorithmOk returns a tuple with the KeyAlgorithm field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetKeyAlgorithm

`func (o *PublicKeyInfo) SetKeyAlgorithm(v string)`

SetKeyAlgorithm sets KeyAlgorithm field to given value.


### GetKeyFingerprint

`func (o *PublicKeyInfo) GetKeyFingerprint() string`

GetKeyFingerprint returns the KeyFingerprint field if non-nil, zero value otherwise.

### GetKeyFingerprintOk

`func (o *PublicKeyInfo) GetKeyFingerprintOk() (*string, bool)`

GetKeyFingerprintOk returns a tuple with the KeyFingerprint field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetKeyFingerprint

`func (o *PublicKeyInfo) SetKeyFingerprint(v string)`

SetKeyFingerprint sets KeyFingerprint field to given value.


### GetPublicKeyPem

`func (o *PublicKeyInfo) GetPublicKeyPem() string`

GetPublicKeyPem returns the PublicKeyPem field if non-nil, zero value otherwise.

### GetPublicKeyPemOk

`func (o *PublicKeyInfo) GetPublicKeyPemOk() (*string, bool)`

GetPublicKeyPemOk returns a tuple with the PublicKeyPem field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPublicKeyPem

`func (o *PublicKeyInfo) SetPublicKeyPem(v string)`

SetPublicKeyPem sets PublicKeyPem field to given value.


### GetIsActive

`func (o *PublicKeyInfo) GetIsActive() bool`

GetIsActive returns the IsActive field if non-nil, zero value otherwise.

### GetIsActiveOk

`func (o *PublicKeyInfo) GetIsActiveOk() (*bool, bool)`

GetIsActiveOk returns a tuple with the IsActive field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIsActive

`func (o *PublicKeyInfo) SetIsActive(v bool)`

SetIsActive sets IsActive field to given value.

### HasIsActive

`func (o *PublicKeyInfo) HasIsActive() bool`

HasIsActive returns a boolean if a field has been set.

### GetCreatedAt

`func (o *PublicKeyInfo) GetCreatedAt() time.Time`

GetCreatedAt returns the CreatedAt field if non-nil, zero value otherwise.

### GetCreatedAtOk

`func (o *PublicKeyInfo) GetCreatedAtOk() (*time.Time, bool)`

GetCreatedAtOk returns a tuple with the CreatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreatedAt

`func (o *PublicKeyInfo) SetCreatedAt(v time.Time)`

SetCreatedAt sets CreatedAt field to given value.


### GetLastUsedAt

`func (o *PublicKeyInfo) GetLastUsedAt() time.Time`

GetLastUsedAt returns the LastUsedAt field if non-nil, zero value otherwise.

### GetLastUsedAtOk

`func (o *PublicKeyInfo) GetLastUsedAtOk() (*time.Time, bool)`

GetLastUsedAtOk returns a tuple with the LastUsedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLastUsedAt

`func (o *PublicKeyInfo) SetLastUsedAt(v time.Time)`

SetLastUsedAt sets LastUsedAt field to given value.

### HasLastUsedAt

`func (o *PublicKeyInfo) HasLastUsedAt() bool`

HasLastUsedAt returns a boolean if a field has been set.

### SetLastUsedAtNil

`func (o *PublicKeyInfo) SetLastUsedAtNil(b bool)`

 SetLastUsedAtNil sets the value for LastUsedAt to be an explicit nil

### UnsetLastUsedAt
`func (o *PublicKeyInfo) UnsetLastUsedAt()`

UnsetLastUsedAt ensures that no value is present for LastUsedAt, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


