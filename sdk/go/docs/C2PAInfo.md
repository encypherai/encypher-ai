# C2PAInfo

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ManifestUrl** | **string** | C2PA manifest URL | 
**ManifestHash** | Pointer to **NullableString** |  | [optional] 
**Verified** | **bool** | Whether manifest is verified | 
**VerificationDetails** | Pointer to **map[string]interface{}** |  | [optional] 

## Methods

### NewC2PAInfo

`func NewC2PAInfo(manifestUrl string, verified bool, ) *C2PAInfo`

NewC2PAInfo instantiates a new C2PAInfo object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewC2PAInfoWithDefaults

`func NewC2PAInfoWithDefaults() *C2PAInfo`

NewC2PAInfoWithDefaults instantiates a new C2PAInfo object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetManifestUrl

`func (o *C2PAInfo) GetManifestUrl() string`

GetManifestUrl returns the ManifestUrl field if non-nil, zero value otherwise.

### GetManifestUrlOk

`func (o *C2PAInfo) GetManifestUrlOk() (*string, bool)`

GetManifestUrlOk returns a tuple with the ManifestUrl field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetManifestUrl

`func (o *C2PAInfo) SetManifestUrl(v string)`

SetManifestUrl sets ManifestUrl field to given value.


### GetManifestHash

`func (o *C2PAInfo) GetManifestHash() string`

GetManifestHash returns the ManifestHash field if non-nil, zero value otherwise.

### GetManifestHashOk

`func (o *C2PAInfo) GetManifestHashOk() (*string, bool)`

GetManifestHashOk returns a tuple with the ManifestHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetManifestHash

`func (o *C2PAInfo) SetManifestHash(v string)`

SetManifestHash sets ManifestHash field to given value.

### HasManifestHash

`func (o *C2PAInfo) HasManifestHash() bool`

HasManifestHash returns a boolean if a field has been set.

### SetManifestHashNil

`func (o *C2PAInfo) SetManifestHashNil(b bool)`

 SetManifestHashNil sets the value for ManifestHash to be an explicit nil

### UnsetManifestHash
`func (o *C2PAInfo) UnsetManifestHash()`

UnsetManifestHash ensures that no value is present for ManifestHash, not even an explicit nil
### GetVerified

`func (o *C2PAInfo) GetVerified() bool`

GetVerified returns the Verified field if non-nil, zero value otherwise.

### GetVerifiedOk

`func (o *C2PAInfo) GetVerifiedOk() (*bool, bool)`

GetVerifiedOk returns a tuple with the Verified field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVerified

`func (o *C2PAInfo) SetVerified(v bool)`

SetVerified sets Verified field to given value.


### GetVerificationDetails

`func (o *C2PAInfo) GetVerificationDetails() map[string]interface{}`

GetVerificationDetails returns the VerificationDetails field if non-nil, zero value otherwise.

### GetVerificationDetailsOk

`func (o *C2PAInfo) GetVerificationDetailsOk() (*map[string]interface{}, bool)`

GetVerificationDetailsOk returns a tuple with the VerificationDetails field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVerificationDetails

`func (o *C2PAInfo) SetVerificationDetails(v map[string]interface{})`

SetVerificationDetails sets VerificationDetails field to given value.

### HasVerificationDetails

`func (o *C2PAInfo) HasVerificationDetails() bool`

HasVerificationDetails returns a boolean if a field has been set.

### SetVerificationDetailsNil

`func (o *C2PAInfo) SetVerificationDetailsNil(b bool)`

 SetVerificationDetailsNil sets the value for VerificationDetails to be an explicit nil

### UnsetVerificationDetails
`func (o *C2PAInfo) UnsetVerificationDetails()`

UnsetVerificationDetails ensures that no value is present for VerificationDetails, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


