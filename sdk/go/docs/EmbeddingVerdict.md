# EmbeddingVerdict

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Index** | **int32** | Index of this embedding (0-based) | 
**Valid** | **bool** | Whether the signature is valid | 
**Tampered** | **bool** | Whether the payload was tampered | 
**ReasonCode** | **string** | Reason code describing the verdict | 
**SignerId** | Pointer to **NullableString** |  | [optional] 
**SignerName** | Pointer to **NullableString** |  | [optional] 
**Timestamp** | Pointer to **NullableTime** |  | [optional] 
**TextSpan** | Pointer to **[]interface{}** |  | [optional] 
**CleanText** | Pointer to **NullableString** |  | [optional] 
**Manifest** | Pointer to **map[string]interface{}** |  | [optional] 

## Methods

### NewEmbeddingVerdict

`func NewEmbeddingVerdict(index int32, valid bool, tampered bool, reasonCode string, ) *EmbeddingVerdict`

NewEmbeddingVerdict instantiates a new EmbeddingVerdict object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewEmbeddingVerdictWithDefaults

`func NewEmbeddingVerdictWithDefaults() *EmbeddingVerdict`

NewEmbeddingVerdictWithDefaults instantiates a new EmbeddingVerdict object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetIndex

`func (o *EmbeddingVerdict) GetIndex() int32`

GetIndex returns the Index field if non-nil, zero value otherwise.

### GetIndexOk

`func (o *EmbeddingVerdict) GetIndexOk() (*int32, bool)`

GetIndexOk returns a tuple with the Index field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIndex

`func (o *EmbeddingVerdict) SetIndex(v int32)`

SetIndex sets Index field to given value.


### GetValid

`func (o *EmbeddingVerdict) GetValid() bool`

GetValid returns the Valid field if non-nil, zero value otherwise.

### GetValidOk

`func (o *EmbeddingVerdict) GetValidOk() (*bool, bool)`

GetValidOk returns a tuple with the Valid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetValid

`func (o *EmbeddingVerdict) SetValid(v bool)`

SetValid sets Valid field to given value.


### GetTampered

`func (o *EmbeddingVerdict) GetTampered() bool`

GetTampered returns the Tampered field if non-nil, zero value otherwise.

### GetTamperedOk

`func (o *EmbeddingVerdict) GetTamperedOk() (*bool, bool)`

GetTamperedOk returns a tuple with the Tampered field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTampered

`func (o *EmbeddingVerdict) SetTampered(v bool)`

SetTampered sets Tampered field to given value.


### GetReasonCode

`func (o *EmbeddingVerdict) GetReasonCode() string`

GetReasonCode returns the ReasonCode field if non-nil, zero value otherwise.

### GetReasonCodeOk

`func (o *EmbeddingVerdict) GetReasonCodeOk() (*string, bool)`

GetReasonCodeOk returns a tuple with the ReasonCode field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetReasonCode

`func (o *EmbeddingVerdict) SetReasonCode(v string)`

SetReasonCode sets ReasonCode field to given value.


### GetSignerId

`func (o *EmbeddingVerdict) GetSignerId() string`

GetSignerId returns the SignerId field if non-nil, zero value otherwise.

### GetSignerIdOk

`func (o *EmbeddingVerdict) GetSignerIdOk() (*string, bool)`

GetSignerIdOk returns a tuple with the SignerId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignerId

`func (o *EmbeddingVerdict) SetSignerId(v string)`

SetSignerId sets SignerId field to given value.

### HasSignerId

`func (o *EmbeddingVerdict) HasSignerId() bool`

HasSignerId returns a boolean if a field has been set.

### SetSignerIdNil

`func (o *EmbeddingVerdict) SetSignerIdNil(b bool)`

 SetSignerIdNil sets the value for SignerId to be an explicit nil

### UnsetSignerId
`func (o *EmbeddingVerdict) UnsetSignerId()`

UnsetSignerId ensures that no value is present for SignerId, not even an explicit nil
### GetSignerName

`func (o *EmbeddingVerdict) GetSignerName() string`

GetSignerName returns the SignerName field if non-nil, zero value otherwise.

### GetSignerNameOk

`func (o *EmbeddingVerdict) GetSignerNameOk() (*string, bool)`

GetSignerNameOk returns a tuple with the SignerName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignerName

`func (o *EmbeddingVerdict) SetSignerName(v string)`

SetSignerName sets SignerName field to given value.

### HasSignerName

`func (o *EmbeddingVerdict) HasSignerName() bool`

HasSignerName returns a boolean if a field has been set.

### SetSignerNameNil

`func (o *EmbeddingVerdict) SetSignerNameNil(b bool)`

 SetSignerNameNil sets the value for SignerName to be an explicit nil

### UnsetSignerName
`func (o *EmbeddingVerdict) UnsetSignerName()`

UnsetSignerName ensures that no value is present for SignerName, not even an explicit nil
### GetTimestamp

`func (o *EmbeddingVerdict) GetTimestamp() time.Time`

GetTimestamp returns the Timestamp field if non-nil, zero value otherwise.

### GetTimestampOk

`func (o *EmbeddingVerdict) GetTimestampOk() (*time.Time, bool)`

GetTimestampOk returns a tuple with the Timestamp field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTimestamp

`func (o *EmbeddingVerdict) SetTimestamp(v time.Time)`

SetTimestamp sets Timestamp field to given value.

### HasTimestamp

`func (o *EmbeddingVerdict) HasTimestamp() bool`

HasTimestamp returns a boolean if a field has been set.

### SetTimestampNil

`func (o *EmbeddingVerdict) SetTimestampNil(b bool)`

 SetTimestampNil sets the value for Timestamp to be an explicit nil

### UnsetTimestamp
`func (o *EmbeddingVerdict) UnsetTimestamp()`

UnsetTimestamp ensures that no value is present for Timestamp, not even an explicit nil
### GetTextSpan

`func (o *EmbeddingVerdict) GetTextSpan() []interface{}`

GetTextSpan returns the TextSpan field if non-nil, zero value otherwise.

### GetTextSpanOk

`func (o *EmbeddingVerdict) GetTextSpanOk() (*[]interface{}, bool)`

GetTextSpanOk returns a tuple with the TextSpan field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTextSpan

`func (o *EmbeddingVerdict) SetTextSpan(v []interface{})`

SetTextSpan sets TextSpan field to given value.

### HasTextSpan

`func (o *EmbeddingVerdict) HasTextSpan() bool`

HasTextSpan returns a boolean if a field has been set.

### SetTextSpanNil

`func (o *EmbeddingVerdict) SetTextSpanNil(b bool)`

 SetTextSpanNil sets the value for TextSpan to be an explicit nil

### UnsetTextSpan
`func (o *EmbeddingVerdict) UnsetTextSpan()`

UnsetTextSpan ensures that no value is present for TextSpan, not even an explicit nil
### GetCleanText

`func (o *EmbeddingVerdict) GetCleanText() string`

GetCleanText returns the CleanText field if non-nil, zero value otherwise.

### GetCleanTextOk

`func (o *EmbeddingVerdict) GetCleanTextOk() (*string, bool)`

GetCleanTextOk returns a tuple with the CleanText field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCleanText

`func (o *EmbeddingVerdict) SetCleanText(v string)`

SetCleanText sets CleanText field to given value.

### HasCleanText

`func (o *EmbeddingVerdict) HasCleanText() bool`

HasCleanText returns a boolean if a field has been set.

### SetCleanTextNil

`func (o *EmbeddingVerdict) SetCleanTextNil(b bool)`

 SetCleanTextNil sets the value for CleanText to be an explicit nil

### UnsetCleanText
`func (o *EmbeddingVerdict) UnsetCleanText()`

UnsetCleanText ensures that no value is present for CleanText, not even an explicit nil
### GetManifest

`func (o *EmbeddingVerdict) GetManifest() map[string]interface{}`

GetManifest returns the Manifest field if non-nil, zero value otherwise.

### GetManifestOk

`func (o *EmbeddingVerdict) GetManifestOk() (*map[string]interface{}, bool)`

GetManifestOk returns a tuple with the Manifest field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetManifest

`func (o *EmbeddingVerdict) SetManifest(v map[string]interface{})`

SetManifest sets Manifest field to given value.

### HasManifest

`func (o *EmbeddingVerdict) HasManifest() bool`

HasManifest returns a boolean if a field has been set.

### SetManifestNil

`func (o *EmbeddingVerdict) SetManifestNil(b bool)`

 SetManifestNil sets the value for Manifest to be an explicit nil

### UnsetManifest
`func (o *EmbeddingVerdict) UnsetManifest()`

UnsetManifest ensures that no value is present for Manifest, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


