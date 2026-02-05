# VerificationServiceC2PAInfo

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ManifestUrl** | Pointer to **NullableString** |  | [optional] 
**ManifestHash** | Pointer to **NullableString** |  | [optional] 
**Validated** | Pointer to **bool** |  | [optional] [default to false]
**ValidationType** | Pointer to **NullableString** |  | [optional] 
**Assertions** | Pointer to **[]map[string]interface{}** |  | [optional] 
**CertificateChain** | Pointer to **[]string** |  | [optional] 

## Methods

### NewVerificationServiceC2PAInfo

`func NewVerificationServiceC2PAInfo() *VerificationServiceC2PAInfo`

NewVerificationServiceC2PAInfo instantiates a new VerificationServiceC2PAInfo object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewVerificationServiceC2PAInfoWithDefaults

`func NewVerificationServiceC2PAInfoWithDefaults() *VerificationServiceC2PAInfo`

NewVerificationServiceC2PAInfoWithDefaults instantiates a new VerificationServiceC2PAInfo object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetManifestUrl

`func (o *VerificationServiceC2PAInfo) GetManifestUrl() string`

GetManifestUrl returns the ManifestUrl field if non-nil, zero value otherwise.

### GetManifestUrlOk

`func (o *VerificationServiceC2PAInfo) GetManifestUrlOk() (*string, bool)`

GetManifestUrlOk returns a tuple with the ManifestUrl field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetManifestUrl

`func (o *VerificationServiceC2PAInfo) SetManifestUrl(v string)`

SetManifestUrl sets ManifestUrl field to given value.

### HasManifestUrl

`func (o *VerificationServiceC2PAInfo) HasManifestUrl() bool`

HasManifestUrl returns a boolean if a field has been set.

### SetManifestUrlNil

`func (o *VerificationServiceC2PAInfo) SetManifestUrlNil(b bool)`

 SetManifestUrlNil sets the value for ManifestUrl to be an explicit nil

### UnsetManifestUrl
`func (o *VerificationServiceC2PAInfo) UnsetManifestUrl()`

UnsetManifestUrl ensures that no value is present for ManifestUrl, not even an explicit nil
### GetManifestHash

`func (o *VerificationServiceC2PAInfo) GetManifestHash() string`

GetManifestHash returns the ManifestHash field if non-nil, zero value otherwise.

### GetManifestHashOk

`func (o *VerificationServiceC2PAInfo) GetManifestHashOk() (*string, bool)`

GetManifestHashOk returns a tuple with the ManifestHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetManifestHash

`func (o *VerificationServiceC2PAInfo) SetManifestHash(v string)`

SetManifestHash sets ManifestHash field to given value.

### HasManifestHash

`func (o *VerificationServiceC2PAInfo) HasManifestHash() bool`

HasManifestHash returns a boolean if a field has been set.

### SetManifestHashNil

`func (o *VerificationServiceC2PAInfo) SetManifestHashNil(b bool)`

 SetManifestHashNil sets the value for ManifestHash to be an explicit nil

### UnsetManifestHash
`func (o *VerificationServiceC2PAInfo) UnsetManifestHash()`

UnsetManifestHash ensures that no value is present for ManifestHash, not even an explicit nil
### GetValidated

`func (o *VerificationServiceC2PAInfo) GetValidated() bool`

GetValidated returns the Validated field if non-nil, zero value otherwise.

### GetValidatedOk

`func (o *VerificationServiceC2PAInfo) GetValidatedOk() (*bool, bool)`

GetValidatedOk returns a tuple with the Validated field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetValidated

`func (o *VerificationServiceC2PAInfo) SetValidated(v bool)`

SetValidated sets Validated field to given value.

### HasValidated

`func (o *VerificationServiceC2PAInfo) HasValidated() bool`

HasValidated returns a boolean if a field has been set.

### GetValidationType

`func (o *VerificationServiceC2PAInfo) GetValidationType() string`

GetValidationType returns the ValidationType field if non-nil, zero value otherwise.

### GetValidationTypeOk

`func (o *VerificationServiceC2PAInfo) GetValidationTypeOk() (*string, bool)`

GetValidationTypeOk returns a tuple with the ValidationType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetValidationType

`func (o *VerificationServiceC2PAInfo) SetValidationType(v string)`

SetValidationType sets ValidationType field to given value.

### HasValidationType

`func (o *VerificationServiceC2PAInfo) HasValidationType() bool`

HasValidationType returns a boolean if a field has been set.

### SetValidationTypeNil

`func (o *VerificationServiceC2PAInfo) SetValidationTypeNil(b bool)`

 SetValidationTypeNil sets the value for ValidationType to be an explicit nil

### UnsetValidationType
`func (o *VerificationServiceC2PAInfo) UnsetValidationType()`

UnsetValidationType ensures that no value is present for ValidationType, not even an explicit nil
### GetAssertions

`func (o *VerificationServiceC2PAInfo) GetAssertions() []map[string]interface{}`

GetAssertions returns the Assertions field if non-nil, zero value otherwise.

### GetAssertionsOk

`func (o *VerificationServiceC2PAInfo) GetAssertionsOk() (*[]map[string]interface{}, bool)`

GetAssertionsOk returns a tuple with the Assertions field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAssertions

`func (o *VerificationServiceC2PAInfo) SetAssertions(v []map[string]interface{})`

SetAssertions sets Assertions field to given value.

### HasAssertions

`func (o *VerificationServiceC2PAInfo) HasAssertions() bool`

HasAssertions returns a boolean if a field has been set.

### SetAssertionsNil

`func (o *VerificationServiceC2PAInfo) SetAssertionsNil(b bool)`

 SetAssertionsNil sets the value for Assertions to be an explicit nil

### UnsetAssertions
`func (o *VerificationServiceC2PAInfo) UnsetAssertions()`

UnsetAssertions ensures that no value is present for Assertions, not even an explicit nil
### GetCertificateChain

`func (o *VerificationServiceC2PAInfo) GetCertificateChain() []string`

GetCertificateChain returns the CertificateChain field if non-nil, zero value otherwise.

### GetCertificateChainOk

`func (o *VerificationServiceC2PAInfo) GetCertificateChainOk() (*[]string, bool)`

GetCertificateChainOk returns a tuple with the CertificateChain field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCertificateChain

`func (o *VerificationServiceC2PAInfo) SetCertificateChain(v []string)`

SetCertificateChain sets CertificateChain field to given value.

### HasCertificateChain

`func (o *VerificationServiceC2PAInfo) HasCertificateChain() bool`

HasCertificateChain returns a boolean if a field has been set.

### SetCertificateChainNil

`func (o *VerificationServiceC2PAInfo) SetCertificateChainNil(b bool)`

 SetCertificateChainNil sets the value for CertificateChain to be an explicit nil

### UnsetCertificateChain
`func (o *VerificationServiceC2PAInfo) UnsetCertificateChain()`

UnsetCertificateChain ensures that no value is present for CertificateChain, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


