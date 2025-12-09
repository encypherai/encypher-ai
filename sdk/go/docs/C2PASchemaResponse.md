# C2PASchemaResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | **string** |  | 
**Name** | **string** |  | 
**Label** | **string** |  | 
**Version** | **string** |  | 
**JsonSchema** | **map[string]interface{}** |  | 
**Description** | **NullableString** |  | 
**OrganizationId** | **string** |  | 
**IsActive** | **bool** |  | 
**IsPublic** | **bool** |  | 
**CreatedAt** | **NullableString** |  | 
**UpdatedAt** | **NullableString** |  | 

## Methods

### NewC2PASchemaResponse

`func NewC2PASchemaResponse(id string, name string, label string, version string, jsonSchema map[string]interface{}, description NullableString, organizationId string, isActive bool, isPublic bool, createdAt NullableString, updatedAt NullableString, ) *C2PASchemaResponse`

NewC2PASchemaResponse instantiates a new C2PASchemaResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewC2PASchemaResponseWithDefaults

`func NewC2PASchemaResponseWithDefaults() *C2PASchemaResponse`

NewC2PASchemaResponseWithDefaults instantiates a new C2PASchemaResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *C2PASchemaResponse) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *C2PASchemaResponse) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *C2PASchemaResponse) SetId(v string)`

SetId sets Id field to given value.


### GetName

`func (o *C2PASchemaResponse) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *C2PASchemaResponse) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *C2PASchemaResponse) SetName(v string)`

SetName sets Name field to given value.


### GetLabel

`func (o *C2PASchemaResponse) GetLabel() string`

GetLabel returns the Label field if non-nil, zero value otherwise.

### GetLabelOk

`func (o *C2PASchemaResponse) GetLabelOk() (*string, bool)`

GetLabelOk returns a tuple with the Label field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLabel

`func (o *C2PASchemaResponse) SetLabel(v string)`

SetLabel sets Label field to given value.


### GetVersion

`func (o *C2PASchemaResponse) GetVersion() string`

GetVersion returns the Version field if non-nil, zero value otherwise.

### GetVersionOk

`func (o *C2PASchemaResponse) GetVersionOk() (*string, bool)`

GetVersionOk returns a tuple with the Version field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVersion

`func (o *C2PASchemaResponse) SetVersion(v string)`

SetVersion sets Version field to given value.


### GetJsonSchema

`func (o *C2PASchemaResponse) GetJsonSchema() map[string]interface{}`

GetJsonSchema returns the JsonSchema field if non-nil, zero value otherwise.

### GetJsonSchemaOk

`func (o *C2PASchemaResponse) GetJsonSchemaOk() (*map[string]interface{}, bool)`

GetJsonSchemaOk returns a tuple with the JsonSchema field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetJsonSchema

`func (o *C2PASchemaResponse) SetJsonSchema(v map[string]interface{})`

SetJsonSchema sets JsonSchema field to given value.


### GetDescription

`func (o *C2PASchemaResponse) GetDescription() string`

GetDescription returns the Description field if non-nil, zero value otherwise.

### GetDescriptionOk

`func (o *C2PASchemaResponse) GetDescriptionOk() (*string, bool)`

GetDescriptionOk returns a tuple with the Description field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDescription

`func (o *C2PASchemaResponse) SetDescription(v string)`

SetDescription sets Description field to given value.


### SetDescriptionNil

`func (o *C2PASchemaResponse) SetDescriptionNil(b bool)`

 SetDescriptionNil sets the value for Description to be an explicit nil

### UnsetDescription
`func (o *C2PASchemaResponse) UnsetDescription()`

UnsetDescription ensures that no value is present for Description, not even an explicit nil
### GetOrganizationId

`func (o *C2PASchemaResponse) GetOrganizationId() string`

GetOrganizationId returns the OrganizationId field if non-nil, zero value otherwise.

### GetOrganizationIdOk

`func (o *C2PASchemaResponse) GetOrganizationIdOk() (*string, bool)`

GetOrganizationIdOk returns a tuple with the OrganizationId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationId

`func (o *C2PASchemaResponse) SetOrganizationId(v string)`

SetOrganizationId sets OrganizationId field to given value.


### GetIsActive

`func (o *C2PASchemaResponse) GetIsActive() bool`

GetIsActive returns the IsActive field if non-nil, zero value otherwise.

### GetIsActiveOk

`func (o *C2PASchemaResponse) GetIsActiveOk() (*bool, bool)`

GetIsActiveOk returns a tuple with the IsActive field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIsActive

`func (o *C2PASchemaResponse) SetIsActive(v bool)`

SetIsActive sets IsActive field to given value.


### GetIsPublic

`func (o *C2PASchemaResponse) GetIsPublic() bool`

GetIsPublic returns the IsPublic field if non-nil, zero value otherwise.

### GetIsPublicOk

`func (o *C2PASchemaResponse) GetIsPublicOk() (*bool, bool)`

GetIsPublicOk returns a tuple with the IsPublic field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIsPublic

`func (o *C2PASchemaResponse) SetIsPublic(v bool)`

SetIsPublic sets IsPublic field to given value.


### GetCreatedAt

`func (o *C2PASchemaResponse) GetCreatedAt() string`

GetCreatedAt returns the CreatedAt field if non-nil, zero value otherwise.

### GetCreatedAtOk

`func (o *C2PASchemaResponse) GetCreatedAtOk() (*string, bool)`

GetCreatedAtOk returns a tuple with the CreatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreatedAt

`func (o *C2PASchemaResponse) SetCreatedAt(v string)`

SetCreatedAt sets CreatedAt field to given value.


### SetCreatedAtNil

`func (o *C2PASchemaResponse) SetCreatedAtNil(b bool)`

 SetCreatedAtNil sets the value for CreatedAt to be an explicit nil

### UnsetCreatedAt
`func (o *C2PASchemaResponse) UnsetCreatedAt()`

UnsetCreatedAt ensures that no value is present for CreatedAt, not even an explicit nil
### GetUpdatedAt

`func (o *C2PASchemaResponse) GetUpdatedAt() string`

GetUpdatedAt returns the UpdatedAt field if non-nil, zero value otherwise.

### GetUpdatedAtOk

`func (o *C2PASchemaResponse) GetUpdatedAtOk() (*string, bool)`

GetUpdatedAtOk returns a tuple with the UpdatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUpdatedAt

`func (o *C2PASchemaResponse) SetUpdatedAt(v string)`

SetUpdatedAt sets UpdatedAt field to given value.


### SetUpdatedAtNil

`func (o *C2PASchemaResponse) SetUpdatedAtNil(b bool)`

 SetUpdatedAtNil sets the value for UpdatedAt to be an explicit nil

### UnsetUpdatedAt
`func (o *C2PASchemaResponse) UnsetUpdatedAt()`

UnsetUpdatedAt ensures that no value is present for UpdatedAt, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


