# C2PATemplateResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | **string** |  | 
**Name** | **string** |  | 
**Description** | **NullableString** |  | 
**SchemaId** | **string** |  | 
**TemplateData** | **map[string]interface{}** |  | 
**Category** | **NullableString** |  | 
**OrganizationId** | **string** |  | 
**IsDefault** | **bool** |  | 
**IsActive** | **bool** |  | 
**IsPublic** | **bool** |  | 
**CreatedAt** | **NullableString** |  | 
**UpdatedAt** | **NullableString** |  | 

## Methods

### NewC2PATemplateResponse

`func NewC2PATemplateResponse(id string, name string, description NullableString, schemaId string, templateData map[string]interface{}, category NullableString, organizationId string, isDefault bool, isActive bool, isPublic bool, createdAt NullableString, updatedAt NullableString, ) *C2PATemplateResponse`

NewC2PATemplateResponse instantiates a new C2PATemplateResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewC2PATemplateResponseWithDefaults

`func NewC2PATemplateResponseWithDefaults() *C2PATemplateResponse`

NewC2PATemplateResponseWithDefaults instantiates a new C2PATemplateResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *C2PATemplateResponse) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *C2PATemplateResponse) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *C2PATemplateResponse) SetId(v string)`

SetId sets Id field to given value.


### GetName

`func (o *C2PATemplateResponse) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *C2PATemplateResponse) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *C2PATemplateResponse) SetName(v string)`

SetName sets Name field to given value.


### GetDescription

`func (o *C2PATemplateResponse) GetDescription() string`

GetDescription returns the Description field if non-nil, zero value otherwise.

### GetDescriptionOk

`func (o *C2PATemplateResponse) GetDescriptionOk() (*string, bool)`

GetDescriptionOk returns a tuple with the Description field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDescription

`func (o *C2PATemplateResponse) SetDescription(v string)`

SetDescription sets Description field to given value.


### SetDescriptionNil

`func (o *C2PATemplateResponse) SetDescriptionNil(b bool)`

 SetDescriptionNil sets the value for Description to be an explicit nil

### UnsetDescription
`func (o *C2PATemplateResponse) UnsetDescription()`

UnsetDescription ensures that no value is present for Description, not even an explicit nil
### GetSchemaId

`func (o *C2PATemplateResponse) GetSchemaId() string`

GetSchemaId returns the SchemaId field if non-nil, zero value otherwise.

### GetSchemaIdOk

`func (o *C2PATemplateResponse) GetSchemaIdOk() (*string, bool)`

GetSchemaIdOk returns a tuple with the SchemaId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSchemaId

`func (o *C2PATemplateResponse) SetSchemaId(v string)`

SetSchemaId sets SchemaId field to given value.


### GetTemplateData

`func (o *C2PATemplateResponse) GetTemplateData() map[string]interface{}`

GetTemplateData returns the TemplateData field if non-nil, zero value otherwise.

### GetTemplateDataOk

`func (o *C2PATemplateResponse) GetTemplateDataOk() (*map[string]interface{}, bool)`

GetTemplateDataOk returns a tuple with the TemplateData field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTemplateData

`func (o *C2PATemplateResponse) SetTemplateData(v map[string]interface{})`

SetTemplateData sets TemplateData field to given value.


### GetCategory

`func (o *C2PATemplateResponse) GetCategory() string`

GetCategory returns the Category field if non-nil, zero value otherwise.

### GetCategoryOk

`func (o *C2PATemplateResponse) GetCategoryOk() (*string, bool)`

GetCategoryOk returns a tuple with the Category field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCategory

`func (o *C2PATemplateResponse) SetCategory(v string)`

SetCategory sets Category field to given value.


### SetCategoryNil

`func (o *C2PATemplateResponse) SetCategoryNil(b bool)`

 SetCategoryNil sets the value for Category to be an explicit nil

### UnsetCategory
`func (o *C2PATemplateResponse) UnsetCategory()`

UnsetCategory ensures that no value is present for Category, not even an explicit nil
### GetOrganizationId

`func (o *C2PATemplateResponse) GetOrganizationId() string`

GetOrganizationId returns the OrganizationId field if non-nil, zero value otherwise.

### GetOrganizationIdOk

`func (o *C2PATemplateResponse) GetOrganizationIdOk() (*string, bool)`

GetOrganizationIdOk returns a tuple with the OrganizationId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationId

`func (o *C2PATemplateResponse) SetOrganizationId(v string)`

SetOrganizationId sets OrganizationId field to given value.


### GetIsDefault

`func (o *C2PATemplateResponse) GetIsDefault() bool`

GetIsDefault returns the IsDefault field if non-nil, zero value otherwise.

### GetIsDefaultOk

`func (o *C2PATemplateResponse) GetIsDefaultOk() (*bool, bool)`

GetIsDefaultOk returns a tuple with the IsDefault field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIsDefault

`func (o *C2PATemplateResponse) SetIsDefault(v bool)`

SetIsDefault sets IsDefault field to given value.


### GetIsActive

`func (o *C2PATemplateResponse) GetIsActive() bool`

GetIsActive returns the IsActive field if non-nil, zero value otherwise.

### GetIsActiveOk

`func (o *C2PATemplateResponse) GetIsActiveOk() (*bool, bool)`

GetIsActiveOk returns a tuple with the IsActive field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIsActive

`func (o *C2PATemplateResponse) SetIsActive(v bool)`

SetIsActive sets IsActive field to given value.


### GetIsPublic

`func (o *C2PATemplateResponse) GetIsPublic() bool`

GetIsPublic returns the IsPublic field if non-nil, zero value otherwise.

### GetIsPublicOk

`func (o *C2PATemplateResponse) GetIsPublicOk() (*bool, bool)`

GetIsPublicOk returns a tuple with the IsPublic field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIsPublic

`func (o *C2PATemplateResponse) SetIsPublic(v bool)`

SetIsPublic sets IsPublic field to given value.


### GetCreatedAt

`func (o *C2PATemplateResponse) GetCreatedAt() string`

GetCreatedAt returns the CreatedAt field if non-nil, zero value otherwise.

### GetCreatedAtOk

`func (o *C2PATemplateResponse) GetCreatedAtOk() (*string, bool)`

GetCreatedAtOk returns a tuple with the CreatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreatedAt

`func (o *C2PATemplateResponse) SetCreatedAt(v string)`

SetCreatedAt sets CreatedAt field to given value.


### SetCreatedAtNil

`func (o *C2PATemplateResponse) SetCreatedAtNil(b bool)`

 SetCreatedAtNil sets the value for CreatedAt to be an explicit nil

### UnsetCreatedAt
`func (o *C2PATemplateResponse) UnsetCreatedAt()`

UnsetCreatedAt ensures that no value is present for CreatedAt, not even an explicit nil
### GetUpdatedAt

`func (o *C2PATemplateResponse) GetUpdatedAt() string`

GetUpdatedAt returns the UpdatedAt field if non-nil, zero value otherwise.

### GetUpdatedAtOk

`func (o *C2PATemplateResponse) GetUpdatedAtOk() (*string, bool)`

GetUpdatedAtOk returns a tuple with the UpdatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUpdatedAt

`func (o *C2PATemplateResponse) SetUpdatedAt(v string)`

SetUpdatedAt sets UpdatedAt field to given value.


### SetUpdatedAtNil

`func (o *C2PATemplateResponse) SetUpdatedAtNil(b bool)`

 SetUpdatedAtNil sets the value for UpdatedAt to be an explicit nil

### UnsetUpdatedAt
`func (o *C2PATemplateResponse) UnsetUpdatedAt()`

UnsetUpdatedAt ensures that no value is present for UpdatedAt, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


