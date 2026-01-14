# MerkleProofItem

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Hash** | **string** | Hash value at this node | 
**Position** | **string** | Position: &#39;left&#39; or &#39;right&#39; | 
**Level** | **int32** | Tree level (0 &#x3D; leaf) | 

## Methods

### NewMerkleProofItem

`func NewMerkleProofItem(hash string, position string, level int32, ) *MerkleProofItem`

NewMerkleProofItem instantiates a new MerkleProofItem object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMerkleProofItemWithDefaults

`func NewMerkleProofItemWithDefaults() *MerkleProofItem`

NewMerkleProofItemWithDefaults instantiates a new MerkleProofItem object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetHash

`func (o *MerkleProofItem) GetHash() string`

GetHash returns the Hash field if non-nil, zero value otherwise.

### GetHashOk

`func (o *MerkleProofItem) GetHashOk() (*string, bool)`

GetHashOk returns a tuple with the Hash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetHash

`func (o *MerkleProofItem) SetHash(v string)`

SetHash sets Hash field to given value.


### GetPosition

`func (o *MerkleProofItem) GetPosition() string`

GetPosition returns the Position field if non-nil, zero value otherwise.

### GetPositionOk

`func (o *MerkleProofItem) GetPositionOk() (*string, bool)`

GetPositionOk returns a tuple with the Position field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPosition

`func (o *MerkleProofItem) SetPosition(v string)`

SetPosition sets Position field to given value.


### GetLevel

`func (o *MerkleProofItem) GetLevel() int32`

GetLevel returns the Level field if non-nil, zero value otherwise.

### GetLevelOk

`func (o *MerkleProofItem) GetLevelOk() (*int32, bool)`

GetLevelOk returns a tuple with the Level field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLevel

`func (o *MerkleProofItem) SetLevel(v int32)`

SetLevel sets Level field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


