# ValidateManifestRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Manifest** | **map[string]interface{}** | Manifest JSON object | 
**Schemas** | Pointer to **map[string]map[string]interface{}** |  | [optional] 

## Methods

### NewValidateManifestRequest

`func NewValidateManifestRequest(manifest map[string]interface{}, ) *ValidateManifestRequest`

NewValidateManifestRequest instantiates a new ValidateManifestRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewValidateManifestRequestWithDefaults

`func NewValidateManifestRequestWithDefaults() *ValidateManifestRequest`

NewValidateManifestRequestWithDefaults instantiates a new ValidateManifestRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetManifest

`func (o *ValidateManifestRequest) GetManifest() map[string]interface{}`

GetManifest returns the Manifest field if non-nil, zero value otherwise.

### GetManifestOk

`func (o *ValidateManifestRequest) GetManifestOk() (*map[string]interface{}, bool)`

GetManifestOk returns a tuple with the Manifest field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetManifest

`func (o *ValidateManifestRequest) SetManifest(v map[string]interface{})`

SetManifest sets Manifest field to given value.


### GetSchemas

`func (o *ValidateManifestRequest) GetSchemas() map[string]map[string]interface{}`

GetSchemas returns the Schemas field if non-nil, zero value otherwise.

### GetSchemasOk

`func (o *ValidateManifestRequest) GetSchemasOk() (*map[string]map[string]interface{}, bool)`

GetSchemasOk returns a tuple with the Schemas field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSchemas

`func (o *ValidateManifestRequest) SetSchemas(v map[string]map[string]interface{})`

SetSchemas sets Schemas field to given value.

### HasSchemas

`func (o *ValidateManifestRequest) HasSchemas() bool`

HasSchemas returns a boolean if a field has been set.

### SetSchemasNil

`func (o *ValidateManifestRequest) SetSchemasNil(b bool)`

 SetSchemasNil sets the value for Schemas to be an explicit nil

### UnsetSchemas
`func (o *ValidateManifestRequest) UnsetSchemas()`

UnsetSchemas ensures that no value is present for Schemas, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


