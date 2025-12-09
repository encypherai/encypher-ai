# C2PASchemaCreate

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Name** | **string** | Human-readable name for the schema | 
**Label** | **string** | Full assertion label (e.g., &#39;com.acme.legal.v1&#39;) | 
**Version** | Pointer to **string** | Schema version (e.g., &#39;v1&#39;, &#39;1.0.0&#39;) | [optional] [default to "1.0"]
**JsonSchema** | **map[string]interface{}** | JSON Schema for validation | 
**Description** | Pointer to **NullableString** |  | [optional] 
**IsPublic** | Pointer to **bool** | Whether schema is publicly accessible | [optional] [default to false]

## Methods

### NewC2PASchemaCreate

`func NewC2PASchemaCreate(name string, label string, jsonSchema map[string]interface{}, ) *C2PASchemaCreate`

NewC2PASchemaCreate instantiates a new C2PASchemaCreate object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewC2PASchemaCreateWithDefaults

`func NewC2PASchemaCreateWithDefaults() *C2PASchemaCreate`

NewC2PASchemaCreateWithDefaults instantiates a new C2PASchemaCreate object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetName

`func (o *C2PASchemaCreate) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *C2PASchemaCreate) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *C2PASchemaCreate) SetName(v string)`

SetName sets Name field to given value.


### GetLabel

`func (o *C2PASchemaCreate) GetLabel() string`

GetLabel returns the Label field if non-nil, zero value otherwise.

### GetLabelOk

`func (o *C2PASchemaCreate) GetLabelOk() (*string, bool)`

GetLabelOk returns a tuple with the Label field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLabel

`func (o *C2PASchemaCreate) SetLabel(v string)`

SetLabel sets Label field to given value.


### GetVersion

`func (o *C2PASchemaCreate) GetVersion() string`

GetVersion returns the Version field if non-nil, zero value otherwise.

### GetVersionOk

`func (o *C2PASchemaCreate) GetVersionOk() (*string, bool)`

GetVersionOk returns a tuple with the Version field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVersion

`func (o *C2PASchemaCreate) SetVersion(v string)`

SetVersion sets Version field to given value.

### HasVersion

`func (o *C2PASchemaCreate) HasVersion() bool`

HasVersion returns a boolean if a field has been set.

### GetJsonSchema

`func (o *C2PASchemaCreate) GetJsonSchema() map[string]interface{}`

GetJsonSchema returns the JsonSchema field if non-nil, zero value otherwise.

### GetJsonSchemaOk

`func (o *C2PASchemaCreate) GetJsonSchemaOk() (*map[string]interface{}, bool)`

GetJsonSchemaOk returns a tuple with the JsonSchema field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetJsonSchema

`func (o *C2PASchemaCreate) SetJsonSchema(v map[string]interface{})`

SetJsonSchema sets JsonSchema field to given value.


### GetDescription

`func (o *C2PASchemaCreate) GetDescription() string`

GetDescription returns the Description field if non-nil, zero value otherwise.

### GetDescriptionOk

`func (o *C2PASchemaCreate) GetDescriptionOk() (*string, bool)`

GetDescriptionOk returns a tuple with the Description field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDescription

`func (o *C2PASchemaCreate) SetDescription(v string)`

SetDescription sets Description field to given value.

### HasDescription

`func (o *C2PASchemaCreate) HasDescription() bool`

HasDescription returns a boolean if a field has been set.

### SetDescriptionNil

`func (o *C2PASchemaCreate) SetDescriptionNil(b bool)`

 SetDescriptionNil sets the value for Description to be an explicit nil

### UnsetDescription
`func (o *C2PASchemaCreate) UnsetDescription()`

UnsetDescription ensures that no value is present for Description, not even an explicit nil
### GetIsPublic

`func (o *C2PASchemaCreate) GetIsPublic() bool`

GetIsPublic returns the IsPublic field if non-nil, zero value otherwise.

### GetIsPublicOk

`func (o *C2PASchemaCreate) GetIsPublicOk() (*bool, bool)`

GetIsPublicOk returns a tuple with the IsPublic field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIsPublic

`func (o *C2PASchemaCreate) SetIsPublic(v bool)`

SetIsPublic sets IsPublic field to given value.

### HasIsPublic

`func (o *C2PASchemaCreate) HasIsPublic() bool`

HasIsPublic returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


