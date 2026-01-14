# VerifyVerdict

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Valid** | **bool** | Whether the signature is valid | 
**Tampered** | **bool** | Whether the payload was tampered | 
**ReasonCode** | **string** | Reason code describing the verdict | 
**SignerId** | Pointer to **NullableString** |  | [optional] 
**SignerName** | Pointer to **NullableString** |  | [optional] 
**Timestamp** | Pointer to **NullableTime** |  | [optional] 
**Details** | Pointer to **map[string]interface{}** | Structured details (manifest, benchmarking stats, etc.) | [optional] 
**EmbeddingsFound** | Pointer to **int32** | Number of embeddings found in the text | [optional] [default to 0]
**AllEmbeddings** | Pointer to [**[]EmbeddingVerdict**](EmbeddingVerdict.md) |  | [optional] 

## Methods

### NewVerifyVerdict

`func NewVerifyVerdict(valid bool, tampered bool, reasonCode string, ) *VerifyVerdict`

NewVerifyVerdict instantiates a new VerifyVerdict object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewVerifyVerdictWithDefaults

`func NewVerifyVerdictWithDefaults() *VerifyVerdict`

NewVerifyVerdictWithDefaults instantiates a new VerifyVerdict object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetValid

`func (o *VerifyVerdict) GetValid() bool`

GetValid returns the Valid field if non-nil, zero value otherwise.

### GetValidOk

`func (o *VerifyVerdict) GetValidOk() (*bool, bool)`

GetValidOk returns a tuple with the Valid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetValid

`func (o *VerifyVerdict) SetValid(v bool)`

SetValid sets Valid field to given value.


### GetTampered

`func (o *VerifyVerdict) GetTampered() bool`

GetTampered returns the Tampered field if non-nil, zero value otherwise.

### GetTamperedOk

`func (o *VerifyVerdict) GetTamperedOk() (*bool, bool)`

GetTamperedOk returns a tuple with the Tampered field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTampered

`func (o *VerifyVerdict) SetTampered(v bool)`

SetTampered sets Tampered field to given value.


### GetReasonCode

`func (o *VerifyVerdict) GetReasonCode() string`

GetReasonCode returns the ReasonCode field if non-nil, zero value otherwise.

### GetReasonCodeOk

`func (o *VerifyVerdict) GetReasonCodeOk() (*string, bool)`

GetReasonCodeOk returns a tuple with the ReasonCode field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetReasonCode

`func (o *VerifyVerdict) SetReasonCode(v string)`

SetReasonCode sets ReasonCode field to given value.


### GetSignerId

`func (o *VerifyVerdict) GetSignerId() string`

GetSignerId returns the SignerId field if non-nil, zero value otherwise.

### GetSignerIdOk

`func (o *VerifyVerdict) GetSignerIdOk() (*string, bool)`

GetSignerIdOk returns a tuple with the SignerId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignerId

`func (o *VerifyVerdict) SetSignerId(v string)`

SetSignerId sets SignerId field to given value.

### HasSignerId

`func (o *VerifyVerdict) HasSignerId() bool`

HasSignerId returns a boolean if a field has been set.

### SetSignerIdNil

`func (o *VerifyVerdict) SetSignerIdNil(b bool)`

 SetSignerIdNil sets the value for SignerId to be an explicit nil

### UnsetSignerId
`func (o *VerifyVerdict) UnsetSignerId()`

UnsetSignerId ensures that no value is present for SignerId, not even an explicit nil
### GetSignerName

`func (o *VerifyVerdict) GetSignerName() string`

GetSignerName returns the SignerName field if non-nil, zero value otherwise.

### GetSignerNameOk

`func (o *VerifyVerdict) GetSignerNameOk() (*string, bool)`

GetSignerNameOk returns a tuple with the SignerName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignerName

`func (o *VerifyVerdict) SetSignerName(v string)`

SetSignerName sets SignerName field to given value.

### HasSignerName

`func (o *VerifyVerdict) HasSignerName() bool`

HasSignerName returns a boolean if a field has been set.

### SetSignerNameNil

`func (o *VerifyVerdict) SetSignerNameNil(b bool)`

 SetSignerNameNil sets the value for SignerName to be an explicit nil

### UnsetSignerName
`func (o *VerifyVerdict) UnsetSignerName()`

UnsetSignerName ensures that no value is present for SignerName, not even an explicit nil
### GetTimestamp

`func (o *VerifyVerdict) GetTimestamp() time.Time`

GetTimestamp returns the Timestamp field if non-nil, zero value otherwise.

### GetTimestampOk

`func (o *VerifyVerdict) GetTimestampOk() (*time.Time, bool)`

GetTimestampOk returns a tuple with the Timestamp field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTimestamp

`func (o *VerifyVerdict) SetTimestamp(v time.Time)`

SetTimestamp sets Timestamp field to given value.

### HasTimestamp

`func (o *VerifyVerdict) HasTimestamp() bool`

HasTimestamp returns a boolean if a field has been set.

### SetTimestampNil

`func (o *VerifyVerdict) SetTimestampNil(b bool)`

 SetTimestampNil sets the value for Timestamp to be an explicit nil

### UnsetTimestamp
`func (o *VerifyVerdict) UnsetTimestamp()`

UnsetTimestamp ensures that no value is present for Timestamp, not even an explicit nil
### GetDetails

`func (o *VerifyVerdict) GetDetails() map[string]interface{}`

GetDetails returns the Details field if non-nil, zero value otherwise.

### GetDetailsOk

`func (o *VerifyVerdict) GetDetailsOk() (*map[string]interface{}, bool)`

GetDetailsOk returns a tuple with the Details field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDetails

`func (o *VerifyVerdict) SetDetails(v map[string]interface{})`

SetDetails sets Details field to given value.

### HasDetails

`func (o *VerifyVerdict) HasDetails() bool`

HasDetails returns a boolean if a field has been set.

### GetEmbeddingsFound

`func (o *VerifyVerdict) GetEmbeddingsFound() int32`

GetEmbeddingsFound returns the EmbeddingsFound field if non-nil, zero value otherwise.

### GetEmbeddingsFoundOk

`func (o *VerifyVerdict) GetEmbeddingsFoundOk() (*int32, bool)`

GetEmbeddingsFoundOk returns a tuple with the EmbeddingsFound field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEmbeddingsFound

`func (o *VerifyVerdict) SetEmbeddingsFound(v int32)`

SetEmbeddingsFound sets EmbeddingsFound field to given value.

### HasEmbeddingsFound

`func (o *VerifyVerdict) HasEmbeddingsFound() bool`

HasEmbeddingsFound returns a boolean if a field has been set.

### GetAllEmbeddings

`func (o *VerifyVerdict) GetAllEmbeddings() []EmbeddingVerdict`

GetAllEmbeddings returns the AllEmbeddings field if non-nil, zero value otherwise.

### GetAllEmbeddingsOk

`func (o *VerifyVerdict) GetAllEmbeddingsOk() (*[]EmbeddingVerdict, bool)`

GetAllEmbeddingsOk returns a tuple with the AllEmbeddings field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAllEmbeddings

`func (o *VerifyVerdict) SetAllEmbeddings(v []EmbeddingVerdict)`

SetAllEmbeddings sets AllEmbeddings field to given value.

### HasAllEmbeddings

`func (o *VerifyVerdict) HasAllEmbeddings() bool`

HasAllEmbeddings returns a boolean if a field has been set.

### SetAllEmbeddingsNil

`func (o *VerifyVerdict) SetAllEmbeddingsNil(b bool)`

 SetAllEmbeddingsNil sets the value for AllEmbeddings to be an explicit nil

### UnsetAllEmbeddings
`func (o *VerifyVerdict) UnsetAllEmbeddings()`

UnsetAllEmbeddings ensures that no value is present for AllEmbeddings, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


