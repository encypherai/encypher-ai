# C2PAInfo

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ManifestUrl** | **string** | C2PA manifest URL | 
**ManifestHash** | Pointer to **NullableString** |  | [optional] 
**Validated** | **bool** | Whether the manifest passed validation | 
**ValidationType** | **string** | Validation semantics. | 
**ValidationDetails** | Pointer to **map[string]interface{}** |  | [optional] 

## Methods

### NewC2PAInfo

`func NewC2PAInfo(manifestUrl string, validated bool, validationType string, ) *C2PAInfo`

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
### GetValidated

`func (o *C2PAInfo) GetValidated() bool`

GetValidated returns the Validated field if non-nil, zero value otherwise.

### GetValidatedOk

`func (o *C2PAInfo) GetValidatedOk() (*bool, bool)`

GetValidatedOk returns a tuple with the Validated field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetValidated

`func (o *C2PAInfo) SetValidated(v bool)`

SetValidated sets Validated field to given value.


### GetValidationType

`func (o *C2PAInfo) GetValidationType() string`

GetValidationType returns the ValidationType field if non-nil, zero value otherwise.

### GetValidationTypeOk

`func (o *C2PAInfo) GetValidationTypeOk() (*string, bool)`

GetValidationTypeOk returns a tuple with the ValidationType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetValidationType

`func (o *C2PAInfo) SetValidationType(v string)`

SetValidationType sets ValidationType field to given value.


### GetValidationDetails

`func (o *C2PAInfo) GetValidationDetails() map[string]interface{}`

GetValidationDetails returns the ValidationDetails field if non-nil, zero value otherwise.

### GetValidationDetailsOk

`func (o *C2PAInfo) GetValidationDetailsOk() (*map[string]interface{}, bool)`

GetValidationDetailsOk returns a tuple with the ValidationDetails field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetValidationDetails

`func (o *C2PAInfo) SetValidationDetails(v map[string]interface{})`

SetValidationDetails sets ValidationDetails field to given value.

### HasValidationDetails

`func (o *C2PAInfo) HasValidationDetails() bool`

HasValidationDetails returns a boolean if a field has been set.

### SetValidationDetailsNil

`func (o *C2PAInfo) SetValidationDetailsNil(b bool)`

 SetValidationDetailsNil sets the value for ValidationDetails to be an explicit nil

### UnsetValidationDetails
`func (o *C2PAInfo) UnsetValidationDetails()`

UnsetValidationDetails ensures that no value is present for ValidationDetails, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


