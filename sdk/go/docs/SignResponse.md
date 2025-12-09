# SignResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | **bool** | Whether the operation was successful | 
**DocumentId** | **string** | Unique document identifier | 
**SignedText** | **string** | Text with embedded C2PA manifest | 
**TotalSentences** | **int32** | Number of sentences signed | 
**VerificationUrl** | **string** | URL for public verification | 

## Methods

### NewSignResponse

`func NewSignResponse(success bool, documentId string, signedText string, totalSentences int32, verificationUrl string, ) *SignResponse`

NewSignResponse instantiates a new SignResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewSignResponseWithDefaults

`func NewSignResponseWithDefaults() *SignResponse`

NewSignResponseWithDefaults instantiates a new SignResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *SignResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *SignResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *SignResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.


### GetDocumentId

`func (o *SignResponse) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *SignResponse) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *SignResponse) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetSignedText

`func (o *SignResponse) GetSignedText() string`

GetSignedText returns the SignedText field if non-nil, zero value otherwise.

### GetSignedTextOk

`func (o *SignResponse) GetSignedTextOk() (*string, bool)`

GetSignedTextOk returns a tuple with the SignedText field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignedText

`func (o *SignResponse) SetSignedText(v string)`

SetSignedText sets SignedText field to given value.


### GetTotalSentences

`func (o *SignResponse) GetTotalSentences() int32`

GetTotalSentences returns the TotalSentences field if non-nil, zero value otherwise.

### GetTotalSentencesOk

`func (o *SignResponse) GetTotalSentencesOk() (*int32, bool)`

GetTotalSentencesOk returns a tuple with the TotalSentences field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalSentences

`func (o *SignResponse) SetTotalSentences(v int32)`

SetTotalSentences sets TotalSentences field to given value.


### GetVerificationUrl

`func (o *SignResponse) GetVerificationUrl() string`

GetVerificationUrl returns the VerificationUrl field if non-nil, zero value otherwise.

### GetVerificationUrlOk

`func (o *SignResponse) GetVerificationUrlOk() (*string, bool)`

GetVerificationUrlOk returns a tuple with the VerificationUrl field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVerificationUrl

`func (o *SignResponse) SetVerificationUrl(v string)`

SetVerificationUrl sets VerificationUrl field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


