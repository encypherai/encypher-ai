# CertificateUploadRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**CertificatePem** | **string** | PEM-encoded X.509 certificate (must chain to C2PA trusted CA) | 
**ChainPem** | Pointer to **NullableString** |  | [optional] 
**KeyName** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewCertificateUploadRequest

`func NewCertificateUploadRequest(certificatePem string, ) *CertificateUploadRequest`

NewCertificateUploadRequest instantiates a new CertificateUploadRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewCertificateUploadRequestWithDefaults

`func NewCertificateUploadRequestWithDefaults() *CertificateUploadRequest`

NewCertificateUploadRequestWithDefaults instantiates a new CertificateUploadRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetCertificatePem

`func (o *CertificateUploadRequest) GetCertificatePem() string`

GetCertificatePem returns the CertificatePem field if non-nil, zero value otherwise.

### GetCertificatePemOk

`func (o *CertificateUploadRequest) GetCertificatePemOk() (*string, bool)`

GetCertificatePemOk returns a tuple with the CertificatePem field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCertificatePem

`func (o *CertificateUploadRequest) SetCertificatePem(v string)`

SetCertificatePem sets CertificatePem field to given value.


### GetChainPem

`func (o *CertificateUploadRequest) GetChainPem() string`

GetChainPem returns the ChainPem field if non-nil, zero value otherwise.

### GetChainPemOk

`func (o *CertificateUploadRequest) GetChainPemOk() (*string, bool)`

GetChainPemOk returns a tuple with the ChainPem field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetChainPem

`func (o *CertificateUploadRequest) SetChainPem(v string)`

SetChainPem sets ChainPem field to given value.

### HasChainPem

`func (o *CertificateUploadRequest) HasChainPem() bool`

HasChainPem returns a boolean if a field has been set.

### SetChainPemNil

`func (o *CertificateUploadRequest) SetChainPemNil(b bool)`

 SetChainPemNil sets the value for ChainPem to be an explicit nil

### UnsetChainPem
`func (o *CertificateUploadRequest) UnsetChainPem()`

UnsetChainPem ensures that no value is present for ChainPem, not even an explicit nil
### GetKeyName

`func (o *CertificateUploadRequest) GetKeyName() string`

GetKeyName returns the KeyName field if non-nil, zero value otherwise.

### GetKeyNameOk

`func (o *CertificateUploadRequest) GetKeyNameOk() (*string, bool)`

GetKeyNameOk returns a tuple with the KeyName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetKeyName

`func (o *CertificateUploadRequest) SetKeyName(v string)`

SetKeyName sets KeyName field to given value.

### HasKeyName

`func (o *CertificateUploadRequest) HasKeyName() bool`

HasKeyName returns a boolean if a field has been set.

### SetKeyNameNil

`func (o *CertificateUploadRequest) SetKeyNameNil(b bool)`

 SetKeyNameNil sets the value for KeyName to be an explicit nil

### UnsetKeyName
`func (o *CertificateUploadRequest) UnsetKeyName()`

UnsetKeyName ensures that no value is present for KeyName, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


