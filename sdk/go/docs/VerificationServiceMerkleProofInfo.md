# VerificationServiceMerkleProofInfo

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**RootHash** | Pointer to **NullableString** |  | [optional] 
**LeafHash** | Pointer to **NullableString** |  | [optional] 
**LeafIndex** | Pointer to **NullableInt32** |  | [optional] 
**ProofPath** | Pointer to **[]string** |  | [optional] 
**Verified** | Pointer to **bool** |  | [optional] [default to false]

## Methods

### NewVerificationServiceMerkleProofInfo

`func NewVerificationServiceMerkleProofInfo() *VerificationServiceMerkleProofInfo`

NewVerificationServiceMerkleProofInfo instantiates a new VerificationServiceMerkleProofInfo object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewVerificationServiceMerkleProofInfoWithDefaults

`func NewVerificationServiceMerkleProofInfoWithDefaults() *VerificationServiceMerkleProofInfo`

NewVerificationServiceMerkleProofInfoWithDefaults instantiates a new VerificationServiceMerkleProofInfo object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetRootHash

`func (o *VerificationServiceMerkleProofInfo) GetRootHash() string`

GetRootHash returns the RootHash field if non-nil, zero value otherwise.

### GetRootHashOk

`func (o *VerificationServiceMerkleProofInfo) GetRootHashOk() (*string, bool)`

GetRootHashOk returns a tuple with the RootHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRootHash

`func (o *VerificationServiceMerkleProofInfo) SetRootHash(v string)`

SetRootHash sets RootHash field to given value.

### HasRootHash

`func (o *VerificationServiceMerkleProofInfo) HasRootHash() bool`

HasRootHash returns a boolean if a field has been set.

### SetRootHashNil

`func (o *VerificationServiceMerkleProofInfo) SetRootHashNil(b bool)`

 SetRootHashNil sets the value for RootHash to be an explicit nil

### UnsetRootHash
`func (o *VerificationServiceMerkleProofInfo) UnsetRootHash()`

UnsetRootHash ensures that no value is present for RootHash, not even an explicit nil
### GetLeafHash

`func (o *VerificationServiceMerkleProofInfo) GetLeafHash() string`

GetLeafHash returns the LeafHash field if non-nil, zero value otherwise.

### GetLeafHashOk

`func (o *VerificationServiceMerkleProofInfo) GetLeafHashOk() (*string, bool)`

GetLeafHashOk returns a tuple with the LeafHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLeafHash

`func (o *VerificationServiceMerkleProofInfo) SetLeafHash(v string)`

SetLeafHash sets LeafHash field to given value.

### HasLeafHash

`func (o *VerificationServiceMerkleProofInfo) HasLeafHash() bool`

HasLeafHash returns a boolean if a field has been set.

### SetLeafHashNil

`func (o *VerificationServiceMerkleProofInfo) SetLeafHashNil(b bool)`

 SetLeafHashNil sets the value for LeafHash to be an explicit nil

### UnsetLeafHash
`func (o *VerificationServiceMerkleProofInfo) UnsetLeafHash()`

UnsetLeafHash ensures that no value is present for LeafHash, not even an explicit nil
### GetLeafIndex

`func (o *VerificationServiceMerkleProofInfo) GetLeafIndex() int32`

GetLeafIndex returns the LeafIndex field if non-nil, zero value otherwise.

### GetLeafIndexOk

`func (o *VerificationServiceMerkleProofInfo) GetLeafIndexOk() (*int32, bool)`

GetLeafIndexOk returns a tuple with the LeafIndex field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLeafIndex

`func (o *VerificationServiceMerkleProofInfo) SetLeafIndex(v int32)`

SetLeafIndex sets LeafIndex field to given value.

### HasLeafIndex

`func (o *VerificationServiceMerkleProofInfo) HasLeafIndex() bool`

HasLeafIndex returns a boolean if a field has been set.

### SetLeafIndexNil

`func (o *VerificationServiceMerkleProofInfo) SetLeafIndexNil(b bool)`

 SetLeafIndexNil sets the value for LeafIndex to be an explicit nil

### UnsetLeafIndex
`func (o *VerificationServiceMerkleProofInfo) UnsetLeafIndex()`

UnsetLeafIndex ensures that no value is present for LeafIndex, not even an explicit nil
### GetProofPath

`func (o *VerificationServiceMerkleProofInfo) GetProofPath() []string`

GetProofPath returns the ProofPath field if non-nil, zero value otherwise.

### GetProofPathOk

`func (o *VerificationServiceMerkleProofInfo) GetProofPathOk() (*[]string, bool)`

GetProofPathOk returns a tuple with the ProofPath field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetProofPath

`func (o *VerificationServiceMerkleProofInfo) SetProofPath(v []string)`

SetProofPath sets ProofPath field to given value.

### HasProofPath

`func (o *VerificationServiceMerkleProofInfo) HasProofPath() bool`

HasProofPath returns a boolean if a field has been set.

### SetProofPathNil

`func (o *VerificationServiceMerkleProofInfo) SetProofPathNil(b bool)`

 SetProofPathNil sets the value for ProofPath to be an explicit nil

### UnsetProofPath
`func (o *VerificationServiceMerkleProofInfo) UnsetProofPath()`

UnsetProofPath ensures that no value is present for ProofPath, not even an explicit nil
### GetVerified

`func (o *VerificationServiceMerkleProofInfo) GetVerified() bool`

GetVerified returns the Verified field if non-nil, zero value otherwise.

### GetVerifiedOk

`func (o *VerificationServiceMerkleProofInfo) GetVerifiedOk() (*bool, bool)`

GetVerifiedOk returns a tuple with the Verified field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVerified

`func (o *VerificationServiceMerkleProofInfo) SetVerified(v bool)`

SetVerified sets Verified field to given value.

### HasVerified

`func (o *VerificationServiceMerkleProofInfo) HasVerified() bool`

HasVerified returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


