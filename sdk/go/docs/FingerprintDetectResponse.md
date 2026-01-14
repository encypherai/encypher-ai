# FingerprintDetectResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | **bool** | Whether detection succeeded | 
**FingerprintDetected** | **bool** | Whether a fingerprint was detected | 
**Matches** | Pointer to [**[]FingerprintMatch**](FingerprintMatch.md) | List of fingerprint matches | [optional] 
**BestMatch** | Pointer to [**NullableFingerprintMatch**](FingerprintMatch.md) |  | [optional] 
**ProcessingTimeMs** | **float32** | Processing time in milliseconds | 
**Message** | **string** | Status message | 

## Methods

### NewFingerprintDetectResponse

`func NewFingerprintDetectResponse(success bool, fingerprintDetected bool, processingTimeMs float32, message string, ) *FingerprintDetectResponse`

NewFingerprintDetectResponse instantiates a new FingerprintDetectResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewFingerprintDetectResponseWithDefaults

`func NewFingerprintDetectResponseWithDefaults() *FingerprintDetectResponse`

NewFingerprintDetectResponseWithDefaults instantiates a new FingerprintDetectResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *FingerprintDetectResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *FingerprintDetectResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *FingerprintDetectResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.


### GetFingerprintDetected

`func (o *FingerprintDetectResponse) GetFingerprintDetected() bool`

GetFingerprintDetected returns the FingerprintDetected field if non-nil, zero value otherwise.

### GetFingerprintDetectedOk

`func (o *FingerprintDetectResponse) GetFingerprintDetectedOk() (*bool, bool)`

GetFingerprintDetectedOk returns a tuple with the FingerprintDetected field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFingerprintDetected

`func (o *FingerprintDetectResponse) SetFingerprintDetected(v bool)`

SetFingerprintDetected sets FingerprintDetected field to given value.


### GetMatches

`func (o *FingerprintDetectResponse) GetMatches() []FingerprintMatch`

GetMatches returns the Matches field if non-nil, zero value otherwise.

### GetMatchesOk

`func (o *FingerprintDetectResponse) GetMatchesOk() (*[]FingerprintMatch, bool)`

GetMatchesOk returns a tuple with the Matches field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMatches

`func (o *FingerprintDetectResponse) SetMatches(v []FingerprintMatch)`

SetMatches sets Matches field to given value.

### HasMatches

`func (o *FingerprintDetectResponse) HasMatches() bool`

HasMatches returns a boolean if a field has been set.

### GetBestMatch

`func (o *FingerprintDetectResponse) GetBestMatch() FingerprintMatch`

GetBestMatch returns the BestMatch field if non-nil, zero value otherwise.

### GetBestMatchOk

`func (o *FingerprintDetectResponse) GetBestMatchOk() (*FingerprintMatch, bool)`

GetBestMatchOk returns a tuple with the BestMatch field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetBestMatch

`func (o *FingerprintDetectResponse) SetBestMatch(v FingerprintMatch)`

SetBestMatch sets BestMatch field to given value.

### HasBestMatch

`func (o *FingerprintDetectResponse) HasBestMatch() bool`

HasBestMatch returns a boolean if a field has been set.

### SetBestMatchNil

`func (o *FingerprintDetectResponse) SetBestMatchNil(b bool)`

 SetBestMatchNil sets the value for BestMatch to be an explicit nil

### UnsetBestMatch
`func (o *FingerprintDetectResponse) UnsetBestMatch()`

UnsetBestMatch ensures that no value is present for BestMatch, not even an explicit nil
### GetProcessingTimeMs

`func (o *FingerprintDetectResponse) GetProcessingTimeMs() float32`

GetProcessingTimeMs returns the ProcessingTimeMs field if non-nil, zero value otherwise.

### GetProcessingTimeMsOk

`func (o *FingerprintDetectResponse) GetProcessingTimeMsOk() (*float32, bool)`

GetProcessingTimeMsOk returns a tuple with the ProcessingTimeMs field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetProcessingTimeMs

`func (o *FingerprintDetectResponse) SetProcessingTimeMs(v float32)`

SetProcessingTimeMs sets ProcessingTimeMs field to given value.


### GetMessage

`func (o *FingerprintDetectResponse) GetMessage() string`

GetMessage returns the Message field if non-nil, zero value otherwise.

### GetMessageOk

`func (o *FingerprintDetectResponse) GetMessageOk() (*string, bool)`

GetMessageOk returns a tuple with the Message field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMessage

`func (o *FingerprintDetectResponse) SetMessage(v string)`

SetMessage sets Message field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


