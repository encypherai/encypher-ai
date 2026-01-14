# FingerprintDetectRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Text** | **string** | Text to scan for fingerprint | 
**FingerprintKey** | Pointer to **NullableString** |  | [optional] 
**ConfidenceThreshold** | Pointer to **float32** | Minimum confidence threshold for detection (0.0-1.0) | [optional] [default to 0.6]
**ReturnPositions** | Pointer to **bool** | Return positions of detected markers | [optional] [default to false]

## Methods

### NewFingerprintDetectRequest

`func NewFingerprintDetectRequest(text string, ) *FingerprintDetectRequest`

NewFingerprintDetectRequest instantiates a new FingerprintDetectRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewFingerprintDetectRequestWithDefaults

`func NewFingerprintDetectRequestWithDefaults() *FingerprintDetectRequest`

NewFingerprintDetectRequestWithDefaults instantiates a new FingerprintDetectRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetText

`func (o *FingerprintDetectRequest) GetText() string`

GetText returns the Text field if non-nil, zero value otherwise.

### GetTextOk

`func (o *FingerprintDetectRequest) GetTextOk() (*string, bool)`

GetTextOk returns a tuple with the Text field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetText

`func (o *FingerprintDetectRequest) SetText(v string)`

SetText sets Text field to given value.


### GetFingerprintKey

`func (o *FingerprintDetectRequest) GetFingerprintKey() string`

GetFingerprintKey returns the FingerprintKey field if non-nil, zero value otherwise.

### GetFingerprintKeyOk

`func (o *FingerprintDetectRequest) GetFingerprintKeyOk() (*string, bool)`

GetFingerprintKeyOk returns a tuple with the FingerprintKey field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFingerprintKey

`func (o *FingerprintDetectRequest) SetFingerprintKey(v string)`

SetFingerprintKey sets FingerprintKey field to given value.

### HasFingerprintKey

`func (o *FingerprintDetectRequest) HasFingerprintKey() bool`

HasFingerprintKey returns a boolean if a field has been set.

### SetFingerprintKeyNil

`func (o *FingerprintDetectRequest) SetFingerprintKeyNil(b bool)`

 SetFingerprintKeyNil sets the value for FingerprintKey to be an explicit nil

### UnsetFingerprintKey
`func (o *FingerprintDetectRequest) UnsetFingerprintKey()`

UnsetFingerprintKey ensures that no value is present for FingerprintKey, not even an explicit nil
### GetConfidenceThreshold

`func (o *FingerprintDetectRequest) GetConfidenceThreshold() float32`

GetConfidenceThreshold returns the ConfidenceThreshold field if non-nil, zero value otherwise.

### GetConfidenceThresholdOk

`func (o *FingerprintDetectRequest) GetConfidenceThresholdOk() (*float32, bool)`

GetConfidenceThresholdOk returns a tuple with the ConfidenceThreshold field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetConfidenceThreshold

`func (o *FingerprintDetectRequest) SetConfidenceThreshold(v float32)`

SetConfidenceThreshold sets ConfidenceThreshold field to given value.

### HasConfidenceThreshold

`func (o *FingerprintDetectRequest) HasConfidenceThreshold() bool`

HasConfidenceThreshold returns a boolean if a field has been set.

### GetReturnPositions

`func (o *FingerprintDetectRequest) GetReturnPositions() bool`

GetReturnPositions returns the ReturnPositions field if non-nil, zero value otherwise.

### GetReturnPositionsOk

`func (o *FingerprintDetectRequest) GetReturnPositionsOk() (*bool, bool)`

GetReturnPositionsOk returns a tuple with the ReturnPositions field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetReturnPositions

`func (o *FingerprintDetectRequest) SetReturnPositions(v bool)`

SetReturnPositions sets ReturnPositions field to given value.

### HasReturnPositions

`func (o *FingerprintDetectRequest) HasReturnPositions() bool`

HasReturnPositions returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


