# FingerprintEncodeResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | **bool** | Whether encoding succeeded | 
**DocumentId** | **string** | Document identifier | 
**FingerprintId** | **string** | Unique fingerprint identifier | 
**FingerprintedText** | **string** | Text with embedded fingerprint | 
**FingerprintKeyHash** | **string** | Hash of fingerprint key (for verification) | 
**MarkersEmbedded** | **int32** | Number of markers embedded | 
**ProcessingTimeMs** | **float32** | Processing time in milliseconds | 
**Message** | **string** | Status message | 

## Methods

### NewFingerprintEncodeResponse

`func NewFingerprintEncodeResponse(success bool, documentId string, fingerprintId string, fingerprintedText string, fingerprintKeyHash string, markersEmbedded int32, processingTimeMs float32, message string, ) *FingerprintEncodeResponse`

NewFingerprintEncodeResponse instantiates a new FingerprintEncodeResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewFingerprintEncodeResponseWithDefaults

`func NewFingerprintEncodeResponseWithDefaults() *FingerprintEncodeResponse`

NewFingerprintEncodeResponseWithDefaults instantiates a new FingerprintEncodeResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *FingerprintEncodeResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *FingerprintEncodeResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *FingerprintEncodeResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.


### GetDocumentId

`func (o *FingerprintEncodeResponse) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *FingerprintEncodeResponse) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *FingerprintEncodeResponse) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetFingerprintId

`func (o *FingerprintEncodeResponse) GetFingerprintId() string`

GetFingerprintId returns the FingerprintId field if non-nil, zero value otherwise.

### GetFingerprintIdOk

`func (o *FingerprintEncodeResponse) GetFingerprintIdOk() (*string, bool)`

GetFingerprintIdOk returns a tuple with the FingerprintId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFingerprintId

`func (o *FingerprintEncodeResponse) SetFingerprintId(v string)`

SetFingerprintId sets FingerprintId field to given value.


### GetFingerprintedText

`func (o *FingerprintEncodeResponse) GetFingerprintedText() string`

GetFingerprintedText returns the FingerprintedText field if non-nil, zero value otherwise.

### GetFingerprintedTextOk

`func (o *FingerprintEncodeResponse) GetFingerprintedTextOk() (*string, bool)`

GetFingerprintedTextOk returns a tuple with the FingerprintedText field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFingerprintedText

`func (o *FingerprintEncodeResponse) SetFingerprintedText(v string)`

SetFingerprintedText sets FingerprintedText field to given value.


### GetFingerprintKeyHash

`func (o *FingerprintEncodeResponse) GetFingerprintKeyHash() string`

GetFingerprintKeyHash returns the FingerprintKeyHash field if non-nil, zero value otherwise.

### GetFingerprintKeyHashOk

`func (o *FingerprintEncodeResponse) GetFingerprintKeyHashOk() (*string, bool)`

GetFingerprintKeyHashOk returns a tuple with the FingerprintKeyHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFingerprintKeyHash

`func (o *FingerprintEncodeResponse) SetFingerprintKeyHash(v string)`

SetFingerprintKeyHash sets FingerprintKeyHash field to given value.


### GetMarkersEmbedded

`func (o *FingerprintEncodeResponse) GetMarkersEmbedded() int32`

GetMarkersEmbedded returns the MarkersEmbedded field if non-nil, zero value otherwise.

### GetMarkersEmbeddedOk

`func (o *FingerprintEncodeResponse) GetMarkersEmbeddedOk() (*int32, bool)`

GetMarkersEmbeddedOk returns a tuple with the MarkersEmbedded field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMarkersEmbedded

`func (o *FingerprintEncodeResponse) SetMarkersEmbedded(v int32)`

SetMarkersEmbedded sets MarkersEmbedded field to given value.


### GetProcessingTimeMs

`func (o *FingerprintEncodeResponse) GetProcessingTimeMs() float32`

GetProcessingTimeMs returns the ProcessingTimeMs field if non-nil, zero value otherwise.

### GetProcessingTimeMsOk

`func (o *FingerprintEncodeResponse) GetProcessingTimeMsOk() (*float32, bool)`

GetProcessingTimeMsOk returns a tuple with the ProcessingTimeMs field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetProcessingTimeMs

`func (o *FingerprintEncodeResponse) SetProcessingTimeMs(v float32)`

SetProcessingTimeMs sets ProcessingTimeMs field to given value.


### GetMessage

`func (o *FingerprintEncodeResponse) GetMessage() string`

GetMessage returns the Message field if non-nil, zero value otherwise.

### GetMessageOk

`func (o *FingerprintEncodeResponse) GetMessageOk() (*string, bool)`

GetMessageOk returns a tuple with the Message field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMessage

`func (o *FingerprintEncodeResponse) SetMessage(v string)`

SetMessage sets Message field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


