# CreateManifestResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Manifest** | **map[string]interface{}** |  | 
**Signing** | [**CreateManifestSigningPayload**](CreateManifestSigningPayload.md) |  | 

## Methods

### NewCreateManifestResponse

`func NewCreateManifestResponse(manifest map[string]interface{}, signing CreateManifestSigningPayload, ) *CreateManifestResponse`

NewCreateManifestResponse instantiates a new CreateManifestResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewCreateManifestResponseWithDefaults

`func NewCreateManifestResponseWithDefaults() *CreateManifestResponse`

NewCreateManifestResponseWithDefaults instantiates a new CreateManifestResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetManifest

`func (o *CreateManifestResponse) GetManifest() map[string]interface{}`

GetManifest returns the Manifest field if non-nil, zero value otherwise.

### GetManifestOk

`func (o *CreateManifestResponse) GetManifestOk() (*map[string]interface{}, bool)`

GetManifestOk returns a tuple with the Manifest field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetManifest

`func (o *CreateManifestResponse) SetManifest(v map[string]interface{})`

SetManifest sets Manifest field to given value.


### GetSigning

`func (o *CreateManifestResponse) GetSigning() CreateManifestSigningPayload`

GetSigning returns the Signing field if non-nil, zero value otherwise.

### GetSigningOk

`func (o *CreateManifestResponse) GetSigningOk() (*CreateManifestSigningPayload, bool)`

GetSigningOk returns a tuple with the Signing field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSigning

`func (o *CreateManifestResponse) SetSigning(v CreateManifestSigningPayload)`

SetSigning sets Signing field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


