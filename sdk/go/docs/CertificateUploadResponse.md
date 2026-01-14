# CertificateUploadResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | Pointer to **bool** |  | [optional] [default to true]
**Data** | Pointer to **map[string]interface{}** |  | [optional] 
**Error** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewCertificateUploadResponse

`func NewCertificateUploadResponse() *CertificateUploadResponse`

NewCertificateUploadResponse instantiates a new CertificateUploadResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewCertificateUploadResponseWithDefaults

`func NewCertificateUploadResponseWithDefaults() *CertificateUploadResponse`

NewCertificateUploadResponseWithDefaults instantiates a new CertificateUploadResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *CertificateUploadResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *CertificateUploadResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *CertificateUploadResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.

### HasSuccess

`func (o *CertificateUploadResponse) HasSuccess() bool`

HasSuccess returns a boolean if a field has been set.

### GetData

`func (o *CertificateUploadResponse) GetData() map[string]interface{}`

GetData returns the Data field if non-nil, zero value otherwise.

### GetDataOk

`func (o *CertificateUploadResponse) GetDataOk() (*map[string]interface{}, bool)`

GetDataOk returns a tuple with the Data field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetData

`func (o *CertificateUploadResponse) SetData(v map[string]interface{})`

SetData sets Data field to given value.

### HasData

`func (o *CertificateUploadResponse) HasData() bool`

HasData returns a boolean if a field has been set.

### SetDataNil

`func (o *CertificateUploadResponse) SetDataNil(b bool)`

 SetDataNil sets the value for Data to be an explicit nil

### UnsetData
`func (o *CertificateUploadResponse) UnsetData()`

UnsetData ensures that no value is present for Data, not even an explicit nil
### GetError

`func (o *CertificateUploadResponse) GetError() string`

GetError returns the Error field if non-nil, zero value otherwise.

### GetErrorOk

`func (o *CertificateUploadResponse) GetErrorOk() (*string, bool)`

GetErrorOk returns a tuple with the Error field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetError

`func (o *CertificateUploadResponse) SetError(v string)`

SetError sets Error field to given value.

### HasError

`func (o *CertificateUploadResponse) HasError() bool`

HasError returns a boolean if a field has been set.

### SetErrorNil

`func (o *CertificateUploadResponse) SetErrorNil(b bool)`

 SetErrorNil sets the value for Error to be an explicit nil

### UnsetError
`func (o *CertificateUploadResponse) UnsetError()`

UnsetError ensures that no value is present for Error, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


