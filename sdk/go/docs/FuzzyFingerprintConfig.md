# FuzzyFingerprintConfig

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Enabled** | Pointer to **bool** | Whether to generate fuzzy fingerprints during encoding. | [optional] [default to false]
**Algorithm** | Pointer to **string** | Fingerprint algorithm (currently simhash). | [optional] [default to "simhash"]
**Levels** | Pointer to **[]string** | Segmentation levels to fingerprint. | [optional] 
**IncludeDocumentFingerprint** | Pointer to **bool** | Whether to include a document-level fingerprint. | [optional] [default to false]
**FingerprintBits** | Pointer to **int32** | Number of bits in the fingerprint. | [optional] [default to 64]
**BucketBits** | Pointer to **int32** | Number of high-order bits used for bucket indexing. | [optional] [default to 16]

## Methods

### NewFuzzyFingerprintConfig

`func NewFuzzyFingerprintConfig() *FuzzyFingerprintConfig`

NewFuzzyFingerprintConfig instantiates a new FuzzyFingerprintConfig object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewFuzzyFingerprintConfigWithDefaults

`func NewFuzzyFingerprintConfigWithDefaults() *FuzzyFingerprintConfig`

NewFuzzyFingerprintConfigWithDefaults instantiates a new FuzzyFingerprintConfig object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetEnabled

`func (o *FuzzyFingerprintConfig) GetEnabled() bool`

GetEnabled returns the Enabled field if non-nil, zero value otherwise.

### GetEnabledOk

`func (o *FuzzyFingerprintConfig) GetEnabledOk() (*bool, bool)`

GetEnabledOk returns a tuple with the Enabled field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEnabled

`func (o *FuzzyFingerprintConfig) SetEnabled(v bool)`

SetEnabled sets Enabled field to given value.

### HasEnabled

`func (o *FuzzyFingerprintConfig) HasEnabled() bool`

HasEnabled returns a boolean if a field has been set.

### GetAlgorithm

`func (o *FuzzyFingerprintConfig) GetAlgorithm() string`

GetAlgorithm returns the Algorithm field if non-nil, zero value otherwise.

### GetAlgorithmOk

`func (o *FuzzyFingerprintConfig) GetAlgorithmOk() (*string, bool)`

GetAlgorithmOk returns a tuple with the Algorithm field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAlgorithm

`func (o *FuzzyFingerprintConfig) SetAlgorithm(v string)`

SetAlgorithm sets Algorithm field to given value.

### HasAlgorithm

`func (o *FuzzyFingerprintConfig) HasAlgorithm() bool`

HasAlgorithm returns a boolean if a field has been set.

### GetLevels

`func (o *FuzzyFingerprintConfig) GetLevels() []string`

GetLevels returns the Levels field if non-nil, zero value otherwise.

### GetLevelsOk

`func (o *FuzzyFingerprintConfig) GetLevelsOk() (*[]string, bool)`

GetLevelsOk returns a tuple with the Levels field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLevels

`func (o *FuzzyFingerprintConfig) SetLevels(v []string)`

SetLevels sets Levels field to given value.

### HasLevels

`func (o *FuzzyFingerprintConfig) HasLevels() bool`

HasLevels returns a boolean if a field has been set.

### GetIncludeDocumentFingerprint

`func (o *FuzzyFingerprintConfig) GetIncludeDocumentFingerprint() bool`

GetIncludeDocumentFingerprint returns the IncludeDocumentFingerprint field if non-nil, zero value otherwise.

### GetIncludeDocumentFingerprintOk

`func (o *FuzzyFingerprintConfig) GetIncludeDocumentFingerprintOk() (*bool, bool)`

GetIncludeDocumentFingerprintOk returns a tuple with the IncludeDocumentFingerprint field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIncludeDocumentFingerprint

`func (o *FuzzyFingerprintConfig) SetIncludeDocumentFingerprint(v bool)`

SetIncludeDocumentFingerprint sets IncludeDocumentFingerprint field to given value.

### HasIncludeDocumentFingerprint

`func (o *FuzzyFingerprintConfig) HasIncludeDocumentFingerprint() bool`

HasIncludeDocumentFingerprint returns a boolean if a field has been set.

### GetFingerprintBits

`func (o *FuzzyFingerprintConfig) GetFingerprintBits() int32`

GetFingerprintBits returns the FingerprintBits field if non-nil, zero value otherwise.

### GetFingerprintBitsOk

`func (o *FuzzyFingerprintConfig) GetFingerprintBitsOk() (*int32, bool)`

GetFingerprintBitsOk returns a tuple with the FingerprintBits field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFingerprintBits

`func (o *FuzzyFingerprintConfig) SetFingerprintBits(v int32)`

SetFingerprintBits sets FingerprintBits field to given value.

### HasFingerprintBits

`func (o *FuzzyFingerprintConfig) HasFingerprintBits() bool`

HasFingerprintBits returns a boolean if a field has been set.

### GetBucketBits

`func (o *FuzzyFingerprintConfig) GetBucketBits() int32`

GetBucketBits returns the BucketBits field if non-nil, zero value otherwise.

### GetBucketBitsOk

`func (o *FuzzyFingerprintConfig) GetBucketBitsOk() (*int32, bool)`

GetBucketBitsOk returns a tuple with the BucketBits field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetBucketBits

`func (o *FuzzyFingerprintConfig) SetBucketBits(v int32)`

SetBucketBits sets BucketBits field to given value.

### HasBucketBits

`func (o *FuzzyFingerprintConfig) HasBucketBits() bool`

HasBucketBits returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


