# EncodeToolRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**OriginalText** | **string** | The original text to embed metadata into. | 
**Target** | Pointer to **NullableString** |  | [optional] 
**MetadataFormat** | Pointer to **NullableString** |  | [optional] 
**AiInfo** | Pointer to **map[string]interface{}** |  | [optional] 
**CustomMetadata** | Pointer to **map[string]interface{}** |  | [optional] 

## Methods

### NewEncodeToolRequest

`func NewEncodeToolRequest(originalText string, ) *EncodeToolRequest`

NewEncodeToolRequest instantiates a new EncodeToolRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewEncodeToolRequestWithDefaults

`func NewEncodeToolRequestWithDefaults() *EncodeToolRequest`

NewEncodeToolRequestWithDefaults instantiates a new EncodeToolRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetOriginalText

`func (o *EncodeToolRequest) GetOriginalText() string`

GetOriginalText returns the OriginalText field if non-nil, zero value otherwise.

### GetOriginalTextOk

`func (o *EncodeToolRequest) GetOriginalTextOk() (*string, bool)`

GetOriginalTextOk returns a tuple with the OriginalText field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOriginalText

`func (o *EncodeToolRequest) SetOriginalText(v string)`

SetOriginalText sets OriginalText field to given value.


### GetTarget

`func (o *EncodeToolRequest) GetTarget() string`

GetTarget returns the Target field if non-nil, zero value otherwise.

### GetTargetOk

`func (o *EncodeToolRequest) GetTargetOk() (*string, bool)`

GetTargetOk returns a tuple with the Target field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTarget

`func (o *EncodeToolRequest) SetTarget(v string)`

SetTarget sets Target field to given value.

### HasTarget

`func (o *EncodeToolRequest) HasTarget() bool`

HasTarget returns a boolean if a field has been set.

### SetTargetNil

`func (o *EncodeToolRequest) SetTargetNil(b bool)`

 SetTargetNil sets the value for Target to be an explicit nil

### UnsetTarget
`func (o *EncodeToolRequest) UnsetTarget()`

UnsetTarget ensures that no value is present for Target, not even an explicit nil
### GetMetadataFormat

`func (o *EncodeToolRequest) GetMetadataFormat() string`

GetMetadataFormat returns the MetadataFormat field if non-nil, zero value otherwise.

### GetMetadataFormatOk

`func (o *EncodeToolRequest) GetMetadataFormatOk() (*string, bool)`

GetMetadataFormatOk returns a tuple with the MetadataFormat field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMetadataFormat

`func (o *EncodeToolRequest) SetMetadataFormat(v string)`

SetMetadataFormat sets MetadataFormat field to given value.

### HasMetadataFormat

`func (o *EncodeToolRequest) HasMetadataFormat() bool`

HasMetadataFormat returns a boolean if a field has been set.

### SetMetadataFormatNil

`func (o *EncodeToolRequest) SetMetadataFormatNil(b bool)`

 SetMetadataFormatNil sets the value for MetadataFormat to be an explicit nil

### UnsetMetadataFormat
`func (o *EncodeToolRequest) UnsetMetadataFormat()`

UnsetMetadataFormat ensures that no value is present for MetadataFormat, not even an explicit nil
### GetAiInfo

`func (o *EncodeToolRequest) GetAiInfo() map[string]interface{}`

GetAiInfo returns the AiInfo field if non-nil, zero value otherwise.

### GetAiInfoOk

`func (o *EncodeToolRequest) GetAiInfoOk() (*map[string]interface{}, bool)`

GetAiInfoOk returns a tuple with the AiInfo field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAiInfo

`func (o *EncodeToolRequest) SetAiInfo(v map[string]interface{})`

SetAiInfo sets AiInfo field to given value.

### HasAiInfo

`func (o *EncodeToolRequest) HasAiInfo() bool`

HasAiInfo returns a boolean if a field has been set.

### SetAiInfoNil

`func (o *EncodeToolRequest) SetAiInfoNil(b bool)`

 SetAiInfoNil sets the value for AiInfo to be an explicit nil

### UnsetAiInfo
`func (o *EncodeToolRequest) UnsetAiInfo()`

UnsetAiInfo ensures that no value is present for AiInfo, not even an explicit nil
### GetCustomMetadata

`func (o *EncodeToolRequest) GetCustomMetadata() map[string]interface{}`

GetCustomMetadata returns the CustomMetadata field if non-nil, zero value otherwise.

### GetCustomMetadataOk

`func (o *EncodeToolRequest) GetCustomMetadataOk() (*map[string]interface{}, bool)`

GetCustomMetadataOk returns a tuple with the CustomMetadata field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCustomMetadata

`func (o *EncodeToolRequest) SetCustomMetadata(v map[string]interface{})`

SetCustomMetadata sets CustomMetadata field to given value.

### HasCustomMetadata

`func (o *EncodeToolRequest) HasCustomMetadata() bool`

HasCustomMetadata returns a boolean if a field has been set.

### SetCustomMetadataNil

`func (o *EncodeToolRequest) SetCustomMetadataNil(b bool)`

 SetCustomMetadataNil sets the value for CustomMetadata to be an explicit nil

### UnsetCustomMetadata
`func (o *EncodeToolRequest) UnsetCustomMetadata()`

UnsetCustomMetadata ensures that no value is present for CustomMetadata, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


