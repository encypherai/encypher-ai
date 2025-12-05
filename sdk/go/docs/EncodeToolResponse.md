# EncodeToolResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**EncodedText** | **string** | Text with embedded metadata. | 
**Metadata** | Pointer to **map[string]interface{}** |  | [optional] 
**Error** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewEncodeToolResponse

`func NewEncodeToolResponse(encodedText string, ) *EncodeToolResponse`

NewEncodeToolResponse instantiates a new EncodeToolResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewEncodeToolResponseWithDefaults

`func NewEncodeToolResponseWithDefaults() *EncodeToolResponse`

NewEncodeToolResponseWithDefaults instantiates a new EncodeToolResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetEncodedText

`func (o *EncodeToolResponse) GetEncodedText() string`

GetEncodedText returns the EncodedText field if non-nil, zero value otherwise.

### GetEncodedTextOk

`func (o *EncodeToolResponse) GetEncodedTextOk() (*string, bool)`

GetEncodedTextOk returns a tuple with the EncodedText field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEncodedText

`func (o *EncodeToolResponse) SetEncodedText(v string)`

SetEncodedText sets EncodedText field to given value.


### GetMetadata

`func (o *EncodeToolResponse) GetMetadata() map[string]interface{}`

GetMetadata returns the Metadata field if non-nil, zero value otherwise.

### GetMetadataOk

`func (o *EncodeToolResponse) GetMetadataOk() (*map[string]interface{}, bool)`

GetMetadataOk returns a tuple with the Metadata field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMetadata

`func (o *EncodeToolResponse) SetMetadata(v map[string]interface{})`

SetMetadata sets Metadata field to given value.

### HasMetadata

`func (o *EncodeToolResponse) HasMetadata() bool`

HasMetadata returns a boolean if a field has been set.

### SetMetadataNil

`func (o *EncodeToolResponse) SetMetadataNil(b bool)`

 SetMetadataNil sets the value for Metadata to be an explicit nil

### UnsetMetadata
`func (o *EncodeToolResponse) UnsetMetadata()`

UnsetMetadata ensures that no value is present for Metadata, not even an explicit nil
### GetError

`func (o *EncodeToolResponse) GetError() string`

GetError returns the Error field if non-nil, zero value otherwise.

### GetErrorOk

`func (o *EncodeToolResponse) GetErrorOk() (*string, bool)`

GetErrorOk returns a tuple with the Error field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetError

`func (o *EncodeToolResponse) SetError(v string)`

SetError sets Error field to given value.

### HasError

`func (o *EncodeToolResponse) HasError() bool`

HasError returns a boolean if a field has been set.

### SetErrorNil

`func (o *EncodeToolResponse) SetErrorNil(b bool)`

 SetErrorNil sets the value for Error to be an explicit nil

### UnsetError
`func (o *EncodeToolResponse) UnsetError()`

UnsetError ensures that no value is present for Error, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


