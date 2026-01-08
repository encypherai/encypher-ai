# CreateManifestSigningPayload

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ClaimGenerator** | **string** |  | 
**Actions** | Pointer to **[]map[string]interface{}** |  | [optional] 

## Methods

### NewCreateManifestSigningPayload

`func NewCreateManifestSigningPayload(claimGenerator string, ) *CreateManifestSigningPayload`

NewCreateManifestSigningPayload instantiates a new CreateManifestSigningPayload object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewCreateManifestSigningPayloadWithDefaults

`func NewCreateManifestSigningPayloadWithDefaults() *CreateManifestSigningPayload`

NewCreateManifestSigningPayloadWithDefaults instantiates a new CreateManifestSigningPayload object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetClaimGenerator

`func (o *CreateManifestSigningPayload) GetClaimGenerator() string`

GetClaimGenerator returns the ClaimGenerator field if non-nil, zero value otherwise.

### GetClaimGeneratorOk

`func (o *CreateManifestSigningPayload) GetClaimGeneratorOk() (*string, bool)`

GetClaimGeneratorOk returns a tuple with the ClaimGenerator field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetClaimGenerator

`func (o *CreateManifestSigningPayload) SetClaimGenerator(v string)`

SetClaimGenerator sets ClaimGenerator field to given value.


### GetActions

`func (o *CreateManifestSigningPayload) GetActions() []map[string]interface{}`

GetActions returns the Actions field if non-nil, zero value otherwise.

### GetActionsOk

`func (o *CreateManifestSigningPayload) GetActionsOk() (*[]map[string]interface{}, bool)`

GetActionsOk returns a tuple with the Actions field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetActions

`func (o *CreateManifestSigningPayload) SetActions(v []map[string]interface{})`

SetActions sets Actions field to given value.

### HasActions

`func (o *CreateManifestSigningPayload) HasActions() bool`

HasActions returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


