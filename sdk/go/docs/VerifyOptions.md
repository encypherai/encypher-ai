# VerifyOptions

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**IncludeMerkleProof** | Pointer to **bool** | Include Merkle proof details (requires API key) | [optional] [default to false]
**IncludeRawManifest** | Pointer to **bool** | Include raw C2PA manifest data | [optional] [default to false]

## Methods

### NewVerifyOptions

`func NewVerifyOptions() *VerifyOptions`

NewVerifyOptions instantiates a new VerifyOptions object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewVerifyOptionsWithDefaults

`func NewVerifyOptionsWithDefaults() *VerifyOptions`

NewVerifyOptionsWithDefaults instantiates a new VerifyOptions object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetIncludeMerkleProof

`func (o *VerifyOptions) GetIncludeMerkleProof() bool`

GetIncludeMerkleProof returns the IncludeMerkleProof field if non-nil, zero value otherwise.

### GetIncludeMerkleProofOk

`func (o *VerifyOptions) GetIncludeMerkleProofOk() (*bool, bool)`

GetIncludeMerkleProofOk returns a tuple with the IncludeMerkleProof field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIncludeMerkleProof

`func (o *VerifyOptions) SetIncludeMerkleProof(v bool)`

SetIncludeMerkleProof sets IncludeMerkleProof field to given value.

### HasIncludeMerkleProof

`func (o *VerifyOptions) HasIncludeMerkleProof() bool`

HasIncludeMerkleProof returns a boolean if a field has been set.

### GetIncludeRawManifest

`func (o *VerifyOptions) GetIncludeRawManifest() bool`

GetIncludeRawManifest returns the IncludeRawManifest field if non-nil, zero value otherwise.

### GetIncludeRawManifestOk

`func (o *VerifyOptions) GetIncludeRawManifestOk() (*bool, bool)`

GetIncludeRawManifestOk returns a tuple with the IncludeRawManifest field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIncludeRawManifest

`func (o *VerifyOptions) SetIncludeRawManifest(v bool)`

SetIncludeRawManifest sets IncludeRawManifest field to given value.

### HasIncludeRawManifest

`func (o *VerifyOptions) HasIncludeRawManifest() bool`

HasIncludeRawManifest returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


