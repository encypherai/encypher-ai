# VerificationStats

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**TotalVerifications** | **int32** |  | 
**ValidVerifications** | **int32** |  | 
**InvalidVerifications** | **int32** |  | 
**TamperedDocuments** | **int32** |  | 
**AverageConfidenceScore** | **float32** |  | 
**AverageVerificationTimeMs** | **float32** |  | 

## Methods

### NewVerificationStats

`func NewVerificationStats(totalVerifications int32, validVerifications int32, invalidVerifications int32, tamperedDocuments int32, averageConfidenceScore float32, averageVerificationTimeMs float32, ) *VerificationStats`

NewVerificationStats instantiates a new VerificationStats object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewVerificationStatsWithDefaults

`func NewVerificationStatsWithDefaults() *VerificationStats`

NewVerificationStatsWithDefaults instantiates a new VerificationStats object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetTotalVerifications

`func (o *VerificationStats) GetTotalVerifications() int32`

GetTotalVerifications returns the TotalVerifications field if non-nil, zero value otherwise.

### GetTotalVerificationsOk

`func (o *VerificationStats) GetTotalVerificationsOk() (*int32, bool)`

GetTotalVerificationsOk returns a tuple with the TotalVerifications field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalVerifications

`func (o *VerificationStats) SetTotalVerifications(v int32)`

SetTotalVerifications sets TotalVerifications field to given value.


### GetValidVerifications

`func (o *VerificationStats) GetValidVerifications() int32`

GetValidVerifications returns the ValidVerifications field if non-nil, zero value otherwise.

### GetValidVerificationsOk

`func (o *VerificationStats) GetValidVerificationsOk() (*int32, bool)`

GetValidVerificationsOk returns a tuple with the ValidVerifications field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetValidVerifications

`func (o *VerificationStats) SetValidVerifications(v int32)`

SetValidVerifications sets ValidVerifications field to given value.


### GetInvalidVerifications

`func (o *VerificationStats) GetInvalidVerifications() int32`

GetInvalidVerifications returns the InvalidVerifications field if non-nil, zero value otherwise.

### GetInvalidVerificationsOk

`func (o *VerificationStats) GetInvalidVerificationsOk() (*int32, bool)`

GetInvalidVerificationsOk returns a tuple with the InvalidVerifications field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetInvalidVerifications

`func (o *VerificationStats) SetInvalidVerifications(v int32)`

SetInvalidVerifications sets InvalidVerifications field to given value.


### GetTamperedDocuments

`func (o *VerificationStats) GetTamperedDocuments() int32`

GetTamperedDocuments returns the TamperedDocuments field if non-nil, zero value otherwise.

### GetTamperedDocumentsOk

`func (o *VerificationStats) GetTamperedDocumentsOk() (*int32, bool)`

GetTamperedDocumentsOk returns a tuple with the TamperedDocuments field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTamperedDocuments

`func (o *VerificationStats) SetTamperedDocuments(v int32)`

SetTamperedDocuments sets TamperedDocuments field to given value.


### GetAverageConfidenceScore

`func (o *VerificationStats) GetAverageConfidenceScore() float32`

GetAverageConfidenceScore returns the AverageConfidenceScore field if non-nil, zero value otherwise.

### GetAverageConfidenceScoreOk

`func (o *VerificationStats) GetAverageConfidenceScoreOk() (*float32, bool)`

GetAverageConfidenceScoreOk returns a tuple with the AverageConfidenceScore field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAverageConfidenceScore

`func (o *VerificationStats) SetAverageConfidenceScore(v float32)`

SetAverageConfidenceScore sets AverageConfidenceScore field to given value.


### GetAverageVerificationTimeMs

`func (o *VerificationStats) GetAverageVerificationTimeMs() float32`

GetAverageVerificationTimeMs returns the AverageVerificationTimeMs field if non-nil, zero value otherwise.

### GetAverageVerificationTimeMsOk

`func (o *VerificationStats) GetAverageVerificationTimeMsOk() (*float32, bool)`

GetAverageVerificationTimeMsOk returns a tuple with the AverageVerificationTimeMs field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAverageVerificationTimeMs

`func (o *VerificationStats) SetAverageVerificationTimeMs(v float32)`

SetAverageVerificationTimeMs sets AverageVerificationTimeMs field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


