# C2PATemplateCreate

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | **string** | Template name | 
**SchemaId** | **string** | ID of the schema this template uses | 
**TemplateData** | **map[string]interface{}** | Template data/configuration | 
**Description** | Pointer to **NullableString** |  | [optional] 
**Category** | Pointer to **NullableString** |  | [optional] 
**IsPublic** | Pointer to **bool** | Whether template is publicly accessible | [optional] [default to false]

## Methods

### NewC2PATemplateCreate

`func NewC2PATemplateCreate(name string, schemaId string, templateData map[string]interface{}, ) *C2PATemplateCreate`

NewC2PATemplateCreate instantiates a new C2PATemplateCreate object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewC2PATemplateCreateWithDefaults

`func NewC2PATemplateCreateWithDefaults() *C2PATemplateCreate`

NewC2PATemplateCreateWithDefaults instantiates a new C2PATemplateCreate object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *C2PATemplateCreate) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *C2PATemplateCreate) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *C2PATemplateCreate) SetName(v string)`

SetName sets Name field to given value.


### GetSchemaId

`func (o *C2PATemplateCreate) GetSchemaId() string`

GetSchemaId returns the SchemaId field if non-nil, zero value otherwise.

### GetSchemaIdOk

`func (o *C2PATemplateCreate) GetSchemaIdOk() (*string, bool)`

GetSchemaIdOk returns a tuple with the SchemaId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSchemaId

`func (o *C2PATemplateCreate) SetSchemaId(v string)`

SetSchemaId sets SchemaId field to given value.


### GetTemplateData

`func (o *C2PATemplateCreate) GetTemplateData() map[string]interface{}`

GetTemplateData returns the TemplateData field if non-nil, zero value otherwise.

### GetTemplateDataOk

`func (o *C2PATemplateCreate) GetTemplateDataOk() (*map[string]interface{}, bool)`

GetTemplateDataOk returns a tuple with the TemplateData field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTemplateData

`func (o *C2PATemplateCreate) SetTemplateData(v map[string]interface{})`

SetTemplateData sets TemplateData field to given value.


### GetDescription

`func (o *C2PATemplateCreate) GetDescription() string`

GetDescription returns the Description field if non-nil, zero value otherwise.

### GetDescriptionOk

`func (o *C2PATemplateCreate) GetDescriptionOk() (*string, bool)`

GetDescriptionOk returns a tuple with the Description field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDescription

`func (o *C2PATemplateCreate) SetDescription(v string)`

SetDescription sets Description field to given value.

### HasDescription

`func (o *C2PATemplateCreate) HasDescription() bool`

HasDescription returns a boolean if a field has been set.

### SetDescriptionNil

`func (o *C2PATemplateCreate) SetDescriptionNil(b bool)`

 SetDescriptionNil sets the value for Description to be an explicit nil

### UnsetDescription
`func (o *C2PATemplateCreate) UnsetDescription()`

UnsetDescription ensures that no value is present for Description, not even an explicit nil
### GetCategory

`func (o *C2PATemplateCreate) GetCategory() string`

GetCategory returns the Category field if non-nil, zero value otherwise.

### GetCategoryOk

`func (o *C2PATemplateCreate) GetCategoryOk() (*string, bool)`

GetCategoryOk returns a tuple with the Category field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCategory

`func (o *C2PATemplateCreate) SetCategory(v string)`

SetCategory sets Category field to given value.

### HasCategory

`func (o *C2PATemplateCreate) HasCategory() bool`

HasCategory returns a boolean if a field has been set.

### SetCategoryNil

`func (o *C2PATemplateCreate) SetCategoryNil(b bool)`

 SetCategoryNil sets the value for Category to be an explicit nil

### UnsetCategory
`func (o *C2PATemplateCreate) UnsetCategory()`

UnsetCategory ensures that no value is present for Category, not even an explicit nil
### GetIsPublic

`func (o *C2PATemplateCreate) GetIsPublic() bool`

GetIsPublic returns the IsPublic field if non-nil, zero value otherwise.

### GetIsPublicOk

`func (o *C2PATemplateCreate) GetIsPublicOk() (*bool, bool)`

GetIsPublicOk returns a tuple with the IsPublic field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIsPublic

`func (o *C2PATemplateCreate) SetIsPublic(v bool)`

SetIsPublic sets IsPublic field to given value.

### HasIsPublic

`func (o *C2PATemplateCreate) HasIsPublic() bool`

HasIsPublic returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


