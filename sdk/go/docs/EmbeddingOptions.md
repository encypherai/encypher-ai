# EmbeddingOptions

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Format** | Pointer to **string** | Output format: plain, html, markdown, json | [optional] [default to "plain"]
**Method** | Pointer to **string** | Embedding method: invisible (zero-width Unicode), data-attribute, span, comment | [optional] [default to "invisible"]
**IncludeText** | Pointer to **bool** | Whether to return text with embeddings in response | [optional] [default to true]

## Methods

### NewEmbeddingOptions

`func NewEmbeddingOptions() *EmbeddingOptions`

NewEmbeddingOptions instantiates a new EmbeddingOptions object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewEmbeddingOptionsWithDefaults

`func NewEmbeddingOptionsWithDefaults() *EmbeddingOptions`

NewEmbeddingOptionsWithDefaults instantiates a new EmbeddingOptions object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetFormat

`func (o *EmbeddingOptions) GetFormat() string`

GetFormat returns the Format field if non-nil, zero value otherwise.

### GetFormatOk

`func (o *EmbeddingOptions) GetFormatOk() (*string, bool)`

GetFormatOk returns a tuple with the Format field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFormat

`func (o *EmbeddingOptions) SetFormat(v string)`

SetFormat sets Format field to given value.

### HasFormat

`func (o *EmbeddingOptions) HasFormat() bool`

HasFormat returns a boolean if a field has been set.

### GetMethod

`func (o *EmbeddingOptions) GetMethod() string`

GetMethod returns the Method field if non-nil, zero value otherwise.

### GetMethodOk

`func (o *EmbeddingOptions) GetMethodOk() (*string, bool)`

GetMethodOk returns a tuple with the Method field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMethod

`func (o *EmbeddingOptions) SetMethod(v string)`

SetMethod sets Method field to given value.

### HasMethod

`func (o *EmbeddingOptions) HasMethod() bool`

HasMethod returns a boolean if a field has been set.

### GetIncludeText

`func (o *EmbeddingOptions) GetIncludeText() bool`

GetIncludeText returns the IncludeText field if non-nil, zero value otherwise.

### GetIncludeTextOk

`func (o *EmbeddingOptions) GetIncludeTextOk() (*bool, bool)`

GetIncludeTextOk returns a tuple with the IncludeText field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIncludeText

`func (o *EmbeddingOptions) SetIncludeText(v bool)`

SetIncludeText sets IncludeText field to given value.

### HasIncludeText

`func (o *EmbeddingOptions) HasIncludeText() bool`

HasIncludeText returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


