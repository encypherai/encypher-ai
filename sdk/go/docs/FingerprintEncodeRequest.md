# FingerprintEncodeRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DocumentId** | **string** | Unique document identifier | 
**Text** | **string** | Text to fingerprint | 
**FingerprintDensity** | Pointer to **float32** | Density of fingerprint markers (0.01-0.5) | [optional] [default to 0.1]
**FingerprintKey** | Pointer to **NullableString** |  | [optional] 
**Metadata** | Pointer to **map[string]interface{}** |  | [optional] 

## Methods

### NewFingerprintEncodeRequest

`func NewFingerprintEncodeRequest(documentId string, text string, ) *FingerprintEncodeRequest`

NewFingerprintEncodeRequest instantiates a new FingerprintEncodeRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewFingerprintEncodeRequestWithDefaults

`func NewFingerprintEncodeRequestWithDefaults() *FingerprintEncodeRequest`

NewFingerprintEncodeRequestWithDefaults instantiates a new FingerprintEncodeRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDocumentId

`func (o *FingerprintEncodeRequest) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *FingerprintEncodeRequest) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *FingerprintEncodeRequest) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetText

`func (o *FingerprintEncodeRequest) GetText() string`

GetText returns the Text field if non-nil, zero value otherwise.

### GetTextOk

`func (o *FingerprintEncodeRequest) GetTextOk() (*string, bool)`

GetTextOk returns a tuple with the Text field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetText

`func (o *FingerprintEncodeRequest) SetText(v string)`

SetText sets Text field to given value.


### GetFingerprintDensity

`func (o *FingerprintEncodeRequest) GetFingerprintDensity() float32`

GetFingerprintDensity returns the FingerprintDensity field if non-nil, zero value otherwise.

### GetFingerprintDensityOk

`func (o *FingerprintEncodeRequest) GetFingerprintDensityOk() (*float32, bool)`

GetFingerprintDensityOk returns a tuple with the FingerprintDensity field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFingerprintDensity

`func (o *FingerprintEncodeRequest) SetFingerprintDensity(v float32)`

SetFingerprintDensity sets FingerprintDensity field to given value.

### HasFingerprintDensity

`func (o *FingerprintEncodeRequest) HasFingerprintDensity() bool`

HasFingerprintDensity returns a boolean if a field has been set.

### GetFingerprintKey

`func (o *FingerprintEncodeRequest) GetFingerprintKey() string`

GetFingerprintKey returns the FingerprintKey field if non-nil, zero value otherwise.

### GetFingerprintKeyOk

`func (o *FingerprintEncodeRequest) GetFingerprintKeyOk() (*string, bool)`

GetFingerprintKeyOk returns a tuple with the FingerprintKey field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFingerprintKey

`func (o *FingerprintEncodeRequest) SetFingerprintKey(v string)`

SetFingerprintKey sets FingerprintKey field to given value.

### HasFingerprintKey

`func (o *FingerprintEncodeRequest) HasFingerprintKey() bool`

HasFingerprintKey returns a boolean if a field has been set.

### SetFingerprintKeyNil

`func (o *FingerprintEncodeRequest) SetFingerprintKeyNil(b bool)`

 SetFingerprintKeyNil sets the value for FingerprintKey to be an explicit nil

### UnsetFingerprintKey
`func (o *FingerprintEncodeRequest) UnsetFingerprintKey()`

UnsetFingerprintKey ensures that no value is present for FingerprintKey, not even an explicit nil
### GetMetadata

`func (o *FingerprintEncodeRequest) GetMetadata() map[string]interface{}`

GetMetadata returns the Metadata field if non-nil, zero value otherwise.

### GetMetadataOk

`func (o *FingerprintEncodeRequest) GetMetadataOk() (*map[string]interface{}, bool)`

GetMetadataOk returns a tuple with the Metadata field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMetadata

`func (o *FingerprintEncodeRequest) SetMetadata(v map[string]interface{})`

SetMetadata sets Metadata field to given value.

### HasMetadata

`func (o *FingerprintEncodeRequest) HasMetadata() bool`

HasMetadata returns a boolean if a field has been set.

### SetMetadataNil

`func (o *FingerprintEncodeRequest) SetMetadataNil(b bool)`

 SetMetadataNil sets the value for Metadata to be an explicit nil

### UnsetMetadata
`func (o *FingerprintEncodeRequest) UnsetMetadata()`

UnsetMetadata ensures that no value is present for Metadata, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


