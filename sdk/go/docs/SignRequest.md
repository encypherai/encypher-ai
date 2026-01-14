# SignRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Text** | **string** | Content to sign | 
**DocumentId** | Pointer to **NullableString** |  | [optional] 
**DocumentTitle** | Pointer to **NullableString** |  | [optional] 
**DocumentUrl** | Pointer to **NullableString** |  | [optional] 
**DocumentType** | Pointer to **string** | Document type: article | legal_brief | contract | ai_output | [optional] [default to "article"]
**ClaimGenerator** | Pointer to **NullableString** |  | [optional] 
**Actions** | Pointer to **[]map[string]interface{}** |  | [optional] 
**TemplateId** | Pointer to **NullableString** |  | [optional] 
**ValidateAssertions** | Pointer to **bool** | Whether to validate template-based assertions (Business+). | [optional] [default to true]
**Rights** | Pointer to [**NullableRightsMetadata**](RightsMetadata.md) |  | [optional] 

## Methods

### NewSignRequest

`func NewSignRequest(text string, ) *SignRequest`

NewSignRequest instantiates a new SignRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewSignRequestWithDefaults

`func NewSignRequestWithDefaults() *SignRequest`

NewSignRequestWithDefaults instantiates a new SignRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetText

`func (o *SignRequest) GetText() string`

GetText returns the Text field if non-nil, zero value otherwise.

### GetTextOk

`func (o *SignRequest) GetTextOk() (*string, bool)`

GetTextOk returns a tuple with the Text field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetText

`func (o *SignRequest) SetText(v string)`

SetText sets Text field to given value.


### GetDocumentId

`func (o *SignRequest) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *SignRequest) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *SignRequest) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.

### HasDocumentId

`func (o *SignRequest) HasDocumentId() bool`

HasDocumentId returns a boolean if a field has been set.

### SetDocumentIdNil

`func (o *SignRequest) SetDocumentIdNil(b bool)`

 SetDocumentIdNil sets the value for DocumentId to be an explicit nil

### UnsetDocumentId
`func (o *SignRequest) UnsetDocumentId()`

UnsetDocumentId ensures that no value is present for DocumentId, not even an explicit nil
### GetDocumentTitle

`func (o *SignRequest) GetDocumentTitle() string`

GetDocumentTitle returns the DocumentTitle field if non-nil, zero value otherwise.

### GetDocumentTitleOk

`func (o *SignRequest) GetDocumentTitleOk() (*string, bool)`

GetDocumentTitleOk returns a tuple with the DocumentTitle field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentTitle

`func (o *SignRequest) SetDocumentTitle(v string)`

SetDocumentTitle sets DocumentTitle field to given value.

### HasDocumentTitle

`func (o *SignRequest) HasDocumentTitle() bool`

HasDocumentTitle returns a boolean if a field has been set.

### SetDocumentTitleNil

`func (o *SignRequest) SetDocumentTitleNil(b bool)`

 SetDocumentTitleNil sets the value for DocumentTitle to be an explicit nil

### UnsetDocumentTitle
`func (o *SignRequest) UnsetDocumentTitle()`

UnsetDocumentTitle ensures that no value is present for DocumentTitle, not even an explicit nil
### GetDocumentUrl

`func (o *SignRequest) GetDocumentUrl() string`

GetDocumentUrl returns the DocumentUrl field if non-nil, zero value otherwise.

### GetDocumentUrlOk

`func (o *SignRequest) GetDocumentUrlOk() (*string, bool)`

GetDocumentUrlOk returns a tuple with the DocumentUrl field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentUrl

`func (o *SignRequest) SetDocumentUrl(v string)`

SetDocumentUrl sets DocumentUrl field to given value.

### HasDocumentUrl

`func (o *SignRequest) HasDocumentUrl() bool`

HasDocumentUrl returns a boolean if a field has been set.

### SetDocumentUrlNil

`func (o *SignRequest) SetDocumentUrlNil(b bool)`

 SetDocumentUrlNil sets the value for DocumentUrl to be an explicit nil

### UnsetDocumentUrl
`func (o *SignRequest) UnsetDocumentUrl()`

UnsetDocumentUrl ensures that no value is present for DocumentUrl, not even an explicit nil
### GetDocumentType

`func (o *SignRequest) GetDocumentType() string`

GetDocumentType returns the DocumentType field if non-nil, zero value otherwise.

### GetDocumentTypeOk

`func (o *SignRequest) GetDocumentTypeOk() (*string, bool)`

GetDocumentTypeOk returns a tuple with the DocumentType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentType

`func (o *SignRequest) SetDocumentType(v string)`

SetDocumentType sets DocumentType field to given value.

### HasDocumentType

`func (o *SignRequest) HasDocumentType() bool`

HasDocumentType returns a boolean if a field has been set.

### GetClaimGenerator

`func (o *SignRequest) GetClaimGenerator() string`

GetClaimGenerator returns the ClaimGenerator field if non-nil, zero value otherwise.

### GetClaimGeneratorOk

`func (o *SignRequest) GetClaimGeneratorOk() (*string, bool)`

GetClaimGeneratorOk returns a tuple with the ClaimGenerator field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetClaimGenerator

`func (o *SignRequest) SetClaimGenerator(v string)`

SetClaimGenerator sets ClaimGenerator field to given value.

### HasClaimGenerator

`func (o *SignRequest) HasClaimGenerator() bool`

HasClaimGenerator returns a boolean if a field has been set.

### SetClaimGeneratorNil

`func (o *SignRequest) SetClaimGeneratorNil(b bool)`

 SetClaimGeneratorNil sets the value for ClaimGenerator to be an explicit nil

### UnsetClaimGenerator
`func (o *SignRequest) UnsetClaimGenerator()`

UnsetClaimGenerator ensures that no value is present for ClaimGenerator, not even an explicit nil
### GetActions

`func (o *SignRequest) GetActions() []map[string]interface{}`

GetActions returns the Actions field if non-nil, zero value otherwise.

### GetActionsOk

`func (o *SignRequest) GetActionsOk() (*[]map[string]interface{}, bool)`

GetActionsOk returns a tuple with the Actions field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetActions

`func (o *SignRequest) SetActions(v []map[string]interface{})`

SetActions sets Actions field to given value.

### HasActions

`func (o *SignRequest) HasActions() bool`

HasActions returns a boolean if a field has been set.

### SetActionsNil

`func (o *SignRequest) SetActionsNil(b bool)`

 SetActionsNil sets the value for Actions to be an explicit nil

### UnsetActions
`func (o *SignRequest) UnsetActions()`

UnsetActions ensures that no value is present for Actions, not even an explicit nil
### GetTemplateId

`func (o *SignRequest) GetTemplateId() string`

GetTemplateId returns the TemplateId field if non-nil, zero value otherwise.

### GetTemplateIdOk

`func (o *SignRequest) GetTemplateIdOk() (*string, bool)`

GetTemplateIdOk returns a tuple with the TemplateId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTemplateId

`func (o *SignRequest) SetTemplateId(v string)`

SetTemplateId sets TemplateId field to given value.

### HasTemplateId

`func (o *SignRequest) HasTemplateId() bool`

HasTemplateId returns a boolean if a field has been set.

### SetTemplateIdNil

`func (o *SignRequest) SetTemplateIdNil(b bool)`

 SetTemplateIdNil sets the value for TemplateId to be an explicit nil

### UnsetTemplateId
`func (o *SignRequest) UnsetTemplateId()`

UnsetTemplateId ensures that no value is present for TemplateId, not even an explicit nil
### GetValidateAssertions

`func (o *SignRequest) GetValidateAssertions() bool`

GetValidateAssertions returns the ValidateAssertions field if non-nil, zero value otherwise.

### GetValidateAssertionsOk

`func (o *SignRequest) GetValidateAssertionsOk() (*bool, bool)`

GetValidateAssertionsOk returns a tuple with the ValidateAssertions field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetValidateAssertions

`func (o *SignRequest) SetValidateAssertions(v bool)`

SetValidateAssertions sets ValidateAssertions field to given value.

### HasValidateAssertions

`func (o *SignRequest) HasValidateAssertions() bool`

HasValidateAssertions returns a boolean if a field has been set.

### GetRights

`func (o *SignRequest) GetRights() RightsMetadata`

GetRights returns the Rights field if non-nil, zero value otherwise.

### GetRightsOk

`func (o *SignRequest) GetRightsOk() (*RightsMetadata, bool)`

GetRightsOk returns a tuple with the Rights field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRights

`func (o *SignRequest) SetRights(v RightsMetadata)`

SetRights sets Rights field to given value.

### HasRights

`func (o *SignRequest) HasRights() bool`

HasRights returns a boolean if a field has been set.

### SetRightsNil

`func (o *SignRequest) SetRightsNil(b bool)`

 SetRightsNil sets the value for Rights to be an explicit nil

### UnsetRights
`func (o *SignRequest) UnsetRights()`

UnsetRights ensures that no value is present for Rights, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


