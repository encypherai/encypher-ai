# EvidenceGenerateResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | **bool** | Whether evidence generation succeeded | 
**Evidence** | Pointer to [**NullableEvidencePackage**](EvidencePackage.md) |  | [optional] 
**ProcessingTimeMs** | **float32** | Processing time in milliseconds | 
**Message** | **string** | Status message | 

## Methods

### NewEvidenceGenerateResponse

`func NewEvidenceGenerateResponse(success bool, processingTimeMs float32, message string, ) *EvidenceGenerateResponse`

NewEvidenceGenerateResponse instantiates a new EvidenceGenerateResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewEvidenceGenerateResponseWithDefaults

`func NewEvidenceGenerateResponseWithDefaults() *EvidenceGenerateResponse`

NewEvidenceGenerateResponseWithDefaults instantiates a new EvidenceGenerateResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *EvidenceGenerateResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *EvidenceGenerateResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *EvidenceGenerateResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.


### GetEvidence

`func (o *EvidenceGenerateResponse) GetEvidence() EvidencePackage`

GetEvidence returns the Evidence field if non-nil, zero value otherwise.

### GetEvidenceOk

`func (o *EvidenceGenerateResponse) GetEvidenceOk() (*EvidencePackage, bool)`

GetEvidenceOk returns a tuple with the Evidence field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEvidence

`func (o *EvidenceGenerateResponse) SetEvidence(v EvidencePackage)`

SetEvidence sets Evidence field to given value.

### HasEvidence

`func (o *EvidenceGenerateResponse) HasEvidence() bool`

HasEvidence returns a boolean if a field has been set.

### SetEvidenceNil

`func (o *EvidenceGenerateResponse) SetEvidenceNil(b bool)`

 SetEvidenceNil sets the value for Evidence to be an explicit nil

### UnsetEvidence
`func (o *EvidenceGenerateResponse) UnsetEvidence()`

UnsetEvidence ensures that no value is present for Evidence, not even an explicit nil
### GetProcessingTimeMs

`func (o *EvidenceGenerateResponse) GetProcessingTimeMs() float32`

GetProcessingTimeMs returns the ProcessingTimeMs field if non-nil, zero value otherwise.

### GetProcessingTimeMsOk

`func (o *EvidenceGenerateResponse) GetProcessingTimeMsOk() (*float32, bool)`

GetProcessingTimeMsOk returns a tuple with the ProcessingTimeMs field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetProcessingTimeMs

`func (o *EvidenceGenerateResponse) SetProcessingTimeMs(v float32)`

SetProcessingTimeMs sets ProcessingTimeMs field to given value.


### GetMessage

`func (o *EvidenceGenerateResponse) GetMessage() string`

GetMessage returns the Message field if non-nil, zero value otherwise.

### GetMessageOk

`func (o *EvidenceGenerateResponse) GetMessageOk() (*string, bool)`

GetMessageOk returns a tuple with the Message field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMessage

`func (o *EvidenceGenerateResponse) SetMessage(v string)`

SetMessage sets Message field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


