# ContentInfo

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**TextPreview** | Pointer to **NullableString** |  | [optional] 
**LeafHash** | **string** | Cryptographic hash of full content | 
**LeafIndex** | **int32** | Position in document | 

## Methods

### NewContentInfo

`func NewContentInfo(leafHash string, leafIndex int32, ) *ContentInfo`

NewContentInfo instantiates a new ContentInfo object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewContentInfoWithDefaults

`func NewContentInfoWithDefaults() *ContentInfo`

NewContentInfoWithDefaults instantiates a new ContentInfo object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetTextPreview

`func (o *ContentInfo) GetTextPreview() string`

GetTextPreview returns the TextPreview field if non-nil, zero value otherwise.

### GetTextPreviewOk

`func (o *ContentInfo) GetTextPreviewOk() (*string, bool)`

GetTextPreviewOk returns a tuple with the TextPreview field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTextPreview

`func (o *ContentInfo) SetTextPreview(v string)`

SetTextPreview sets TextPreview field to given value.

### HasTextPreview

`func (o *ContentInfo) HasTextPreview() bool`

HasTextPreview returns a boolean if a field has been set.

### SetTextPreviewNil

`func (o *ContentInfo) SetTextPreviewNil(b bool)`

 SetTextPreviewNil sets the value for TextPreview to be an explicit nil

### UnsetTextPreview
`func (o *ContentInfo) UnsetTextPreview()`

UnsetTextPreview ensures that no value is present for TextPreview, not even an explicit nil
### GetLeafHash

`func (o *ContentInfo) GetLeafHash() string`

GetLeafHash returns the LeafHash field if non-nil, zero value otherwise.

### GetLeafHashOk

`func (o *ContentInfo) GetLeafHashOk() (*string, bool)`

GetLeafHashOk returns a tuple with the LeafHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLeafHash

`func (o *ContentInfo) SetLeafHash(v string)`

SetLeafHash sets LeafHash field to given value.


### GetLeafIndex

`func (o *ContentInfo) GetLeafIndex() int32`

GetLeafIndex returns the LeafIndex field if non-nil, zero value otherwise.

### GetLeafIndexOk

`func (o *ContentInfo) GetLeafIndexOk() (*int32, bool)`

GetLeafIndexOk returns a tuple with the LeafIndex field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLeafIndex

`func (o *ContentInfo) SetLeafIndex(v int32)`

SetLeafIndex sets LeafIndex field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


