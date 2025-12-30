# CreateManifestRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Text** | **string** | Plaintext content to derive a manifest for | 
**Filename** | Pointer to **NullableString** |  | [optional] 
**DocumentTitle** | Pointer to **NullableString** |  | [optional] 
**ClaimGenerator** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewCreateManifestRequest

`func NewCreateManifestRequest(text string, ) *CreateManifestRequest`

NewCreateManifestRequest instantiates a new CreateManifestRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewCreateManifestRequestWithDefaults

`func NewCreateManifestRequestWithDefaults() *CreateManifestRequest`

NewCreateManifestRequestWithDefaults instantiates a new CreateManifestRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetText

`func (o *CreateManifestRequest) GetText() string`

GetText returns the Text field if non-nil, zero value otherwise.

### GetTextOk

`func (o *CreateManifestRequest) GetTextOk() (*string, bool)`

GetTextOk returns a tuple with the Text field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetText

`func (o *CreateManifestRequest) SetText(v string)`

SetText sets Text field to given value.


### GetFilename

`func (o *CreateManifestRequest) GetFilename() string`

GetFilename returns the Filename field if non-nil, zero value otherwise.

### GetFilenameOk

`func (o *CreateManifestRequest) GetFilenameOk() (*string, bool)`

GetFilenameOk returns a tuple with the Filename field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFilename

`func (o *CreateManifestRequest) SetFilename(v string)`

SetFilename sets Filename field to given value.

### HasFilename

`func (o *CreateManifestRequest) HasFilename() bool`

HasFilename returns a boolean if a field has been set.

### SetFilenameNil

`func (o *CreateManifestRequest) SetFilenameNil(b bool)`

 SetFilenameNil sets the value for Filename to be an explicit nil

### UnsetFilename
`func (o *CreateManifestRequest) UnsetFilename()`

UnsetFilename ensures that no value is present for Filename, not even an explicit nil
### GetDocumentTitle

`func (o *CreateManifestRequest) GetDocumentTitle() string`

GetDocumentTitle returns the DocumentTitle field if non-nil, zero value otherwise.

### GetDocumentTitleOk

`func (o *CreateManifestRequest) GetDocumentTitleOk() (*string, bool)`

GetDocumentTitleOk returns a tuple with the DocumentTitle field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentTitle

`func (o *CreateManifestRequest) SetDocumentTitle(v string)`

SetDocumentTitle sets DocumentTitle field to given value.

### HasDocumentTitle

`func (o *CreateManifestRequest) HasDocumentTitle() bool`

HasDocumentTitle returns a boolean if a field has been set.

### SetDocumentTitleNil

`func (o *CreateManifestRequest) SetDocumentTitleNil(b bool)`

 SetDocumentTitleNil sets the value for DocumentTitle to be an explicit nil

### UnsetDocumentTitle
`func (o *CreateManifestRequest) UnsetDocumentTitle()`

UnsetDocumentTitle ensures that no value is present for DocumentTitle, not even an explicit nil
### GetClaimGenerator

`func (o *CreateManifestRequest) GetClaimGenerator() string`

GetClaimGenerator returns the ClaimGenerator field if non-nil, zero value otherwise.

### GetClaimGeneratorOk

`func (o *CreateManifestRequest) GetClaimGeneratorOk() (*string, bool)`

GetClaimGeneratorOk returns a tuple with the ClaimGenerator field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetClaimGenerator

`func (o *CreateManifestRequest) SetClaimGenerator(v string)`

SetClaimGenerator sets ClaimGenerator field to given value.

### HasClaimGenerator

`func (o *CreateManifestRequest) HasClaimGenerator() bool`

HasClaimGenerator returns a boolean if a field has been set.

### SetClaimGeneratorNil

`func (o *CreateManifestRequest) SetClaimGeneratorNil(b bool)`

 SetClaimGeneratorNil sets the value for ClaimGenerator to be an explicit nil

### UnsetClaimGenerator
`func (o *CreateManifestRequest) UnsetClaimGenerator()`

UnsetClaimGenerator ensures that no value is present for ClaimGenerator, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


