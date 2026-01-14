# VerificationResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**IsValid** | **bool** |  | 
**IsTampered** | **bool** |  | 
**SignatureValid** | **bool** |  | 
**HashValid** | **bool** |  | 
**ConfidenceScore** | **float32** |  | 
**SimilarityScore** | **NullableFloat32** |  | 
**SignerId** | **NullableString** |  | 
**Warnings** | **[]string** |  | 
**VerificationTimeMs** | **int32** |  | 
**CreatedAt** | **time.Time** |  | 

## Methods

### NewVerificationResponse

`func NewVerificationResponse(isValid bool, isTampered bool, signatureValid bool, hashValid bool, confidenceScore float32, similarityScore NullableFloat32, signerId NullableString, warnings []string, verificationTimeMs int32, createdAt time.Time, ) *VerificationResponse`

NewVerificationResponse instantiates a new VerificationResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewVerificationResponseWithDefaults

`func NewVerificationResponseWithDefaults() *VerificationResponse`

NewVerificationResponseWithDefaults instantiates a new VerificationResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetIsValid

`func (o *VerificationResponse) GetIsValid() bool`

GetIsValid returns the IsValid field if non-nil, zero value otherwise.

### GetIsValidOk

`func (o *VerificationResponse) GetIsValidOk() (*bool, bool)`

GetIsValidOk returns a tuple with the IsValid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIsValid

`func (o *VerificationResponse) SetIsValid(v bool)`

SetIsValid sets IsValid field to given value.


### GetIsTampered

`func (o *VerificationResponse) GetIsTampered() bool`

GetIsTampered returns the IsTampered field if non-nil, zero value otherwise.

### GetIsTamperedOk

`func (o *VerificationResponse) GetIsTamperedOk() (*bool, bool)`

GetIsTamperedOk returns a tuple with the IsTampered field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIsTampered

`func (o *VerificationResponse) SetIsTampered(v bool)`

SetIsTampered sets IsTampered field to given value.


### GetSignatureValid

`func (o *VerificationResponse) GetSignatureValid() bool`

GetSignatureValid returns the SignatureValid field if non-nil, zero value otherwise.

### GetSignatureValidOk

`func (o *VerificationResponse) GetSignatureValidOk() (*bool, bool)`

GetSignatureValidOk returns a tuple with the SignatureValid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignatureValid

`func (o *VerificationResponse) SetSignatureValid(v bool)`

SetSignatureValid sets SignatureValid field to given value.


### GetHashValid

`func (o *VerificationResponse) GetHashValid() bool`

GetHashValid returns the HashValid field if non-nil, zero value otherwise.

### GetHashValidOk

`func (o *VerificationResponse) GetHashValidOk() (*bool, bool)`

GetHashValidOk returns a tuple with the HashValid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetHashValid

`func (o *VerificationResponse) SetHashValid(v bool)`

SetHashValid sets HashValid field to given value.


### GetConfidenceScore

`func (o *VerificationResponse) GetConfidenceScore() float32`

GetConfidenceScore returns the ConfidenceScore field if non-nil, zero value otherwise.

### GetConfidenceScoreOk

`func (o *VerificationResponse) GetConfidenceScoreOk() (*float32, bool)`

GetConfidenceScoreOk returns a tuple with the ConfidenceScore field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetConfidenceScore

`func (o *VerificationResponse) SetConfidenceScore(v float32)`

SetConfidenceScore sets ConfidenceScore field to given value.


### GetSimilarityScore

`func (o *VerificationResponse) GetSimilarityScore() float32`

GetSimilarityScore returns the SimilarityScore field if non-nil, zero value otherwise.

### GetSimilarityScoreOk

`func (o *VerificationResponse) GetSimilarityScoreOk() (*float32, bool)`

GetSimilarityScoreOk returns a tuple with the SimilarityScore field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSimilarityScore

`func (o *VerificationResponse) SetSimilarityScore(v float32)`

SetSimilarityScore sets SimilarityScore field to given value.


### SetSimilarityScoreNil

`func (o *VerificationResponse) SetSimilarityScoreNil(b bool)`

 SetSimilarityScoreNil sets the value for SimilarityScore to be an explicit nil

### UnsetSimilarityScore
`func (o *VerificationResponse) UnsetSimilarityScore()`

UnsetSimilarityScore ensures that no value is present for SimilarityScore, not even an explicit nil
### GetSignerId

`func (o *VerificationResponse) GetSignerId() string`

GetSignerId returns the SignerId field if non-nil, zero value otherwise.

### GetSignerIdOk

`func (o *VerificationResponse) GetSignerIdOk() (*string, bool)`

GetSignerIdOk returns a tuple with the SignerId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignerId

`func (o *VerificationResponse) SetSignerId(v string)`

SetSignerId sets SignerId field to given value.


### SetSignerIdNil

`func (o *VerificationResponse) SetSignerIdNil(b bool)`

 SetSignerIdNil sets the value for SignerId to be an explicit nil

### UnsetSignerId
`func (o *VerificationResponse) UnsetSignerId()`

UnsetSignerId ensures that no value is present for SignerId, not even an explicit nil
### GetWarnings

`func (o *VerificationResponse) GetWarnings() []string`

GetWarnings returns the Warnings field if non-nil, zero value otherwise.

### GetWarningsOk

`func (o *VerificationResponse) GetWarningsOk() (*[]string, bool)`

GetWarningsOk returns a tuple with the Warnings field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetWarnings

`func (o *VerificationResponse) SetWarnings(v []string)`

SetWarnings sets Warnings field to given value.


### SetWarningsNil

`func (o *VerificationResponse) SetWarningsNil(b bool)`

 SetWarningsNil sets the value for Warnings to be an explicit nil

### UnsetWarnings
`func (o *VerificationResponse) UnsetWarnings()`

UnsetWarnings ensures that no value is present for Warnings, not even an explicit nil
### GetVerificationTimeMs

`func (o *VerificationResponse) GetVerificationTimeMs() int32`

GetVerificationTimeMs returns the VerificationTimeMs field if non-nil, zero value otherwise.

### GetVerificationTimeMsOk

`func (o *VerificationResponse) GetVerificationTimeMsOk() (*int32, bool)`

GetVerificationTimeMsOk returns a tuple with the VerificationTimeMs field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVerificationTimeMs

`func (o *VerificationResponse) SetVerificationTimeMs(v int32)`

SetVerificationTimeMs sets VerificationTimeMs field to given value.


### GetCreatedAt

`func (o *VerificationResponse) GetCreatedAt() time.Time`

GetCreatedAt returns the CreatedAt field if non-nil, zero value otherwise.

### GetCreatedAtOk

`func (o *VerificationResponse) GetCreatedAtOk() (*time.Time, bool)`

GetCreatedAtOk returns a tuple with the CreatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreatedAt

`func (o *VerificationResponse) SetCreatedAt(v time.Time)`

SetCreatedAt sets CreatedAt field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


