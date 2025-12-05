# MerkleProofInfo

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**RootHash** | **string** | Merkle tree root hash | 
**Verified** | **bool** | Whether proof is valid | 
**ProofUrl** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewMerkleProofInfo

`func NewMerkleProofInfo(rootHash string, verified bool, ) *MerkleProofInfo`

NewMerkleProofInfo instantiates a new MerkleProofInfo object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMerkleProofInfoWithDefaults

`func NewMerkleProofInfoWithDefaults() *MerkleProofInfo`

NewMerkleProofInfoWithDefaults instantiates a new MerkleProofInfo object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetRootHash

`func (o *MerkleProofInfo) GetRootHash() string`

GetRootHash returns the RootHash field if non-nil, zero value otherwise.

### GetRootHashOk

`func (o *MerkleProofInfo) GetRootHashOk() (*string, bool)`

GetRootHashOk returns a tuple with the RootHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRootHash

`func (o *MerkleProofInfo) SetRootHash(v string)`

SetRootHash sets RootHash field to given value.


### GetVerified

`func (o *MerkleProofInfo) GetVerified() bool`

GetVerified returns the Verified field if non-nil, zero value otherwise.

### GetVerifiedOk

`func (o *MerkleProofInfo) GetVerifiedOk() (*bool, bool)`

GetVerifiedOk returns a tuple with the Verified field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVerified

`func (o *MerkleProofInfo) SetVerified(v bool)`

SetVerified sets Verified field to given value.


### GetProofUrl

`func (o *MerkleProofInfo) GetProofUrl() string`

GetProofUrl returns the ProofUrl field if non-nil, zero value otherwise.

### GetProofUrlOk

`func (o *MerkleProofInfo) GetProofUrlOk() (*string, bool)`

GetProofUrlOk returns a tuple with the ProofUrl field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetProofUrl

`func (o *MerkleProofInfo) SetProofUrl(v string)`

SetProofUrl sets ProofUrl field to given value.

### HasProofUrl

`func (o *MerkleProofInfo) HasProofUrl() bool`

HasProofUrl returns a boolean if a field has been set.

### SetProofUrlNil

`func (o *MerkleProofInfo) SetProofUrlNil(b bool)`

 SetProofUrlNil sets the value for ProofUrl to be an explicit nil

### UnsetProofUrl
`func (o *MerkleProofInfo) UnsetProofUrl()`

UnsetProofUrl ensures that no value is present for ProofUrl, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


