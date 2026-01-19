# FuzzySearchConfig

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Enabled** | Pointer to **bool** | Whether to run fuzzy fingerprint search. | [optional] [default to false]
**Algorithm** | Pointer to **string** | Fingerprint algorithm (currently simhash). | [optional] [default to "simhash"]
**Levels** | Pointer to **[]string** | Segmentation levels to search. | [optional] 
**SimilarityThreshold** | Pointer to **float32** | Similarity threshold for matches (0-1). | [optional] [default to 0.82]
**MaxCandidates** | Pointer to **int32** | Maximum number of candidate matches to return. | [optional] [default to 20]
**IncludeMerkleProof** | Pointer to **bool** | Whether to include Merkle proofs for matches. | [optional] [default to true]
**FallbackWhenNoBinding** | Pointer to **bool** | Only run fuzzy search when no embeddings are found. | [optional] [default to true]

## Methods

### NewFuzzySearchConfig

`func NewFuzzySearchConfig() *FuzzySearchConfig`

NewFuzzySearchConfig instantiates a new FuzzySearchConfig object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewFuzzySearchConfigWithDefaults

`func NewFuzzySearchConfigWithDefaults() *FuzzySearchConfig`

NewFuzzySearchConfigWithDefaults instantiates a new FuzzySearchConfig object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetEnabled

`func (o *FuzzySearchConfig) GetEnabled() bool`

GetEnabled returns the Enabled field if non-nil, zero value otherwise.

### GetEnabledOk

`func (o *FuzzySearchConfig) GetEnabledOk() (*bool, bool)`

GetEnabledOk returns a tuple with the Enabled field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEnabled

`func (o *FuzzySearchConfig) SetEnabled(v bool)`

SetEnabled sets Enabled field to given value.

### HasEnabled

`func (o *FuzzySearchConfig) HasEnabled() bool`

HasEnabled returns a boolean if a field has been set.

### GetAlgorithm

`func (o *FuzzySearchConfig) GetAlgorithm() string`

GetAlgorithm returns the Algorithm field if non-nil, zero value otherwise.

### GetAlgorithmOk

`func (o *FuzzySearchConfig) GetAlgorithmOk() (*string, bool)`

GetAlgorithmOk returns a tuple with the Algorithm field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAlgorithm

`func (o *FuzzySearchConfig) SetAlgorithm(v string)`

SetAlgorithm sets Algorithm field to given value.

### HasAlgorithm

`func (o *FuzzySearchConfig) HasAlgorithm() bool`

HasAlgorithm returns a boolean if a field has been set.

### GetLevels

`func (o *FuzzySearchConfig) GetLevels() []string`

GetLevels returns the Levels field if non-nil, zero value otherwise.

### GetLevelsOk

`func (o *FuzzySearchConfig) GetLevelsOk() (*[]string, bool)`

GetLevelsOk returns a tuple with the Levels field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLevels

`func (o *FuzzySearchConfig) SetLevels(v []string)`

SetLevels sets Levels field to given value.

### HasLevels

`func (o *FuzzySearchConfig) HasLevels() bool`

HasLevels returns a boolean if a field has been set.

### GetSimilarityThreshold

`func (o *FuzzySearchConfig) GetSimilarityThreshold() float32`

GetSimilarityThreshold returns the SimilarityThreshold field if non-nil, zero value otherwise.

### GetSimilarityThresholdOk

`func (o *FuzzySearchConfig) GetSimilarityThresholdOk() (*float32, bool)`

GetSimilarityThresholdOk returns a tuple with the SimilarityThreshold field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSimilarityThreshold

`func (o *FuzzySearchConfig) SetSimilarityThreshold(v float32)`

SetSimilarityThreshold sets SimilarityThreshold field to given value.

### HasSimilarityThreshold

`func (o *FuzzySearchConfig) HasSimilarityThreshold() bool`

HasSimilarityThreshold returns a boolean if a field has been set.

### GetMaxCandidates

`func (o *FuzzySearchConfig) GetMaxCandidates() int32`

GetMaxCandidates returns the MaxCandidates field if non-nil, zero value otherwise.

### GetMaxCandidatesOk

`func (o *FuzzySearchConfig) GetMaxCandidatesOk() (*int32, bool)`

GetMaxCandidatesOk returns a tuple with the MaxCandidates field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMaxCandidates

`func (o *FuzzySearchConfig) SetMaxCandidates(v int32)`

SetMaxCandidates sets MaxCandidates field to given value.

### HasMaxCandidates

`func (o *FuzzySearchConfig) HasMaxCandidates() bool`

HasMaxCandidates returns a boolean if a field has been set.

### GetIncludeMerkleProof

`func (o *FuzzySearchConfig) GetIncludeMerkleProof() bool`

GetIncludeMerkleProof returns the IncludeMerkleProof field if non-nil, zero value otherwise.

### GetIncludeMerkleProofOk

`func (o *FuzzySearchConfig) GetIncludeMerkleProofOk() (*bool, bool)`

GetIncludeMerkleProofOk returns a tuple with the IncludeMerkleProof field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIncludeMerkleProof

`func (o *FuzzySearchConfig) SetIncludeMerkleProof(v bool)`

SetIncludeMerkleProof sets IncludeMerkleProof field to given value.

### HasIncludeMerkleProof

`func (o *FuzzySearchConfig) HasIncludeMerkleProof() bool`

HasIncludeMerkleProof returns a boolean if a field has been set.

### GetFallbackWhenNoBinding

`func (o *FuzzySearchConfig) GetFallbackWhenNoBinding() bool`

GetFallbackWhenNoBinding returns the FallbackWhenNoBinding field if non-nil, zero value otherwise.

### GetFallbackWhenNoBindingOk

`func (o *FuzzySearchConfig) GetFallbackWhenNoBindingOk() (*bool, bool)`

GetFallbackWhenNoBindingOk returns a tuple with the FallbackWhenNoBinding field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFallbackWhenNoBinding

`func (o *FuzzySearchConfig) SetFallbackWhenNoBinding(v bool)`

SetFallbackWhenNoBinding sets FallbackWhenNoBinding field to given value.

### HasFallbackWhenNoBinding

`func (o *FuzzySearchConfig) HasFallbackWhenNoBinding() bool`

HasFallbackWhenNoBinding returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


