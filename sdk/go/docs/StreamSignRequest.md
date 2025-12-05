# StreamSignRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Text** | **string** | Content to sign while streaming progress | 
**DocumentId** | Pointer to **NullableString** |  | [optional] 
**DocumentTitle** | Pointer to **NullableString** |  | [optional] 
**DocumentType** | Pointer to **string** | Document type metadata | [optional] [default to "article"]
**RunId** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewStreamSignRequest

`func NewStreamSignRequest(text string, ) *StreamSignRequest`

NewStreamSignRequest instantiates a new StreamSignRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewStreamSignRequestWithDefaults

`func NewStreamSignRequestWithDefaults() *StreamSignRequest`

NewStreamSignRequestWithDefaults instantiates a new StreamSignRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetText

`func (o *StreamSignRequest) GetText() string`

GetText returns the Text field if non-nil, zero value otherwise.

### GetTextOk

`func (o *StreamSignRequest) GetTextOk() (*string, bool)`

GetTextOk returns a tuple with the Text field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetText

`func (o *StreamSignRequest) SetText(v string)`

SetText sets Text field to given value.


### GetDocumentId

`func (o *StreamSignRequest) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *StreamSignRequest) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *StreamSignRequest) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.

### HasDocumentId

`func (o *StreamSignRequest) HasDocumentId() bool`

HasDocumentId returns a boolean if a field has been set.

### SetDocumentIdNil

`func (o *StreamSignRequest) SetDocumentIdNil(b bool)`

 SetDocumentIdNil sets the value for DocumentId to be an explicit nil

### UnsetDocumentId
`func (o *StreamSignRequest) UnsetDocumentId()`

UnsetDocumentId ensures that no value is present for DocumentId, not even an explicit nil
### GetDocumentTitle

`func (o *StreamSignRequest) GetDocumentTitle() string`

GetDocumentTitle returns the DocumentTitle field if non-nil, zero value otherwise.

### GetDocumentTitleOk

`func (o *StreamSignRequest) GetDocumentTitleOk() (*string, bool)`

GetDocumentTitleOk returns a tuple with the DocumentTitle field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentTitle

`func (o *StreamSignRequest) SetDocumentTitle(v string)`

SetDocumentTitle sets DocumentTitle field to given value.

### HasDocumentTitle

`func (o *StreamSignRequest) HasDocumentTitle() bool`

HasDocumentTitle returns a boolean if a field has been set.

### SetDocumentTitleNil

`func (o *StreamSignRequest) SetDocumentTitleNil(b bool)`

 SetDocumentTitleNil sets the value for DocumentTitle to be an explicit nil

### UnsetDocumentTitle
`func (o *StreamSignRequest) UnsetDocumentTitle()`

UnsetDocumentTitle ensures that no value is present for DocumentTitle, not even an explicit nil
### GetDocumentType

`func (o *StreamSignRequest) GetDocumentType() string`

GetDocumentType returns the DocumentType field if non-nil, zero value otherwise.

### GetDocumentTypeOk

`func (o *StreamSignRequest) GetDocumentTypeOk() (*string, bool)`

GetDocumentTypeOk returns a tuple with the DocumentType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentType

`func (o *StreamSignRequest) SetDocumentType(v string)`

SetDocumentType sets DocumentType field to given value.

### HasDocumentType

`func (o *StreamSignRequest) HasDocumentType() bool`

HasDocumentType returns a boolean if a field has been set.

### GetRunId

`func (o *StreamSignRequest) GetRunId() string`

GetRunId returns the RunId field if non-nil, zero value otherwise.

### GetRunIdOk

`func (o *StreamSignRequest) GetRunIdOk() (*string, bool)`

GetRunIdOk returns a tuple with the RunId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRunId

`func (o *StreamSignRequest) SetRunId(v string)`

SetRunId sets RunId field to given value.

### HasRunId

`func (o *StreamSignRequest) HasRunId() bool`

HasRunId returns a boolean if a field has been set.

### SetRunIdNil

`func (o *StreamSignRequest) SetRunIdNil(b bool)`

 SetRunIdNil sets the value for RunId to be an explicit nil

### UnsetRunId
`func (o *StreamSignRequest) UnsetRunId()`

UnsetRunId ensures that no value is present for RunId, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


