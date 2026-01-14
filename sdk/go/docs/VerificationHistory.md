# VerificationHistory

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | **string** |  | 
**DocumentId** | **string** |  | 
**IsValid** | **bool** |  | 
**IsTampered** | **bool** |  | 
**ConfidenceScore** | **float32** |  | 
**CreatedAt** | **time.Time** |  | 

## Methods

### NewVerificationHistory

`func NewVerificationHistory(id string, documentId string, isValid bool, isTampered bool, confidenceScore float32, createdAt time.Time, ) *VerificationHistory`

NewVerificationHistory instantiates a new VerificationHistory object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewVerificationHistoryWithDefaults

`func NewVerificationHistoryWithDefaults() *VerificationHistory`

NewVerificationHistoryWithDefaults instantiates a new VerificationHistory object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *VerificationHistory) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *VerificationHistory) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *VerificationHistory) SetId(v string)`

SetId sets Id field to given value.


### GetDocumentId

`func (o *VerificationHistory) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *VerificationHistory) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *VerificationHistory) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetIsValid

`func (o *VerificationHistory) GetIsValid() bool`

GetIsValid returns the IsValid field if non-nil, zero value otherwise.

### GetIsValidOk

`func (o *VerificationHistory) GetIsValidOk() (*bool, bool)`

GetIsValidOk returns a tuple with the IsValid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIsValid

`func (o *VerificationHistory) SetIsValid(v bool)`

SetIsValid sets IsValid field to given value.


### GetIsTampered

`func (o *VerificationHistory) GetIsTampered() bool`

GetIsTampered returns the IsTampered field if non-nil, zero value otherwise.

### GetIsTamperedOk

`func (o *VerificationHistory) GetIsTamperedOk() (*bool, bool)`

GetIsTamperedOk returns a tuple with the IsTampered field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIsTampered

`func (o *VerificationHistory) SetIsTampered(v bool)`

SetIsTampered sets IsTampered field to given value.


### GetConfidenceScore

`func (o *VerificationHistory) GetConfidenceScore() float32`

GetConfidenceScore returns the ConfidenceScore field if non-nil, zero value otherwise.

### GetConfidenceScoreOk

`func (o *VerificationHistory) GetConfidenceScoreOk() (*float32, bool)`

GetConfidenceScoreOk returns a tuple with the ConfidenceScore field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetConfidenceScore

`func (o *VerificationHistory) SetConfidenceScore(v float32)`

SetConfidenceScore sets ConfidenceScore field to given value.


### GetCreatedAt

`func (o *VerificationHistory) GetCreatedAt() time.Time`

GetCreatedAt returns the CreatedAt field if non-nil, zero value otherwise.

### GetCreatedAtOk

`func (o *VerificationHistory) GetCreatedAtOk() (*time.Time, bool)`

GetCreatedAtOk returns a tuple with the CreatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreatedAt

`func (o *VerificationHistory) SetCreatedAt(v time.Time)`

SetCreatedAt sets CreatedAt field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


