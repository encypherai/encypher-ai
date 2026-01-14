# FingerprintMatch

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**FingerprintId** | **string** | Matched fingerprint ID | 
**DocumentId** | **string** | Source document ID | 
**OrganizationId** | **string** | Source organization ID | 
**Confidence** | **float32** | Detection confidence (0-1) | 
**MarkersFound** | **int32** | Number of markers detected | 
**MarkersExpected** | **int32** | Number of markers expected | 
**MarkerPositions** | Pointer to **[]int32** |  | [optional] 
**CreatedAt** | **time.Time** | When fingerprint was created | 

## Methods

### NewFingerprintMatch

`func NewFingerprintMatch(fingerprintId string, documentId string, organizationId string, confidence float32, markersFound int32, markersExpected int32, createdAt time.Time, ) *FingerprintMatch`

NewFingerprintMatch instantiates a new FingerprintMatch object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewFingerprintMatchWithDefaults

`func NewFingerprintMatchWithDefaults() *FingerprintMatch`

NewFingerprintMatchWithDefaults instantiates a new FingerprintMatch object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetFingerprintId

`func (o *FingerprintMatch) GetFingerprintId() string`

GetFingerprintId returns the FingerprintId field if non-nil, zero value otherwise.

### GetFingerprintIdOk

`func (o *FingerprintMatch) GetFingerprintIdOk() (*string, bool)`

GetFingerprintIdOk returns a tuple with the FingerprintId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFingerprintId

`func (o *FingerprintMatch) SetFingerprintId(v string)`

SetFingerprintId sets FingerprintId field to given value.


### GetDocumentId

`func (o *FingerprintMatch) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *FingerprintMatch) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *FingerprintMatch) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetOrganizationId

`func (o *FingerprintMatch) GetOrganizationId() string`

GetOrganizationId returns the OrganizationId field if non-nil, zero value otherwise.

### GetOrganizationIdOk

`func (o *FingerprintMatch) GetOrganizationIdOk() (*string, bool)`

GetOrganizationIdOk returns a tuple with the OrganizationId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationId

`func (o *FingerprintMatch) SetOrganizationId(v string)`

SetOrganizationId sets OrganizationId field to given value.


### GetConfidence

`func (o *FingerprintMatch) GetConfidence() float32`

GetConfidence returns the Confidence field if non-nil, zero value otherwise.

### GetConfidenceOk

`func (o *FingerprintMatch) GetConfidenceOk() (*float32, bool)`

GetConfidenceOk returns a tuple with the Confidence field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetConfidence

`func (o *FingerprintMatch) SetConfidence(v float32)`

SetConfidence sets Confidence field to given value.


### GetMarkersFound

`func (o *FingerprintMatch) GetMarkersFound() int32`

GetMarkersFound returns the MarkersFound field if non-nil, zero value otherwise.

### GetMarkersFoundOk

`func (o *FingerprintMatch) GetMarkersFoundOk() (*int32, bool)`

GetMarkersFoundOk returns a tuple with the MarkersFound field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMarkersFound

`func (o *FingerprintMatch) SetMarkersFound(v int32)`

SetMarkersFound sets MarkersFound field to given value.


### GetMarkersExpected

`func (o *FingerprintMatch) GetMarkersExpected() int32`

GetMarkersExpected returns the MarkersExpected field if non-nil, zero value otherwise.

### GetMarkersExpectedOk

`func (o *FingerprintMatch) GetMarkersExpectedOk() (*int32, bool)`

GetMarkersExpectedOk returns a tuple with the MarkersExpected field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMarkersExpected

`func (o *FingerprintMatch) SetMarkersExpected(v int32)`

SetMarkersExpected sets MarkersExpected field to given value.


### GetMarkerPositions

`func (o *FingerprintMatch) GetMarkerPositions() []int32`

GetMarkerPositions returns the MarkerPositions field if non-nil, zero value otherwise.

### GetMarkerPositionsOk

`func (o *FingerprintMatch) GetMarkerPositionsOk() (*[]int32, bool)`

GetMarkerPositionsOk returns a tuple with the MarkerPositions field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMarkerPositions

`func (o *FingerprintMatch) SetMarkerPositions(v []int32)`

SetMarkerPositions sets MarkerPositions field to given value.

### HasMarkerPositions

`func (o *FingerprintMatch) HasMarkerPositions() bool`

HasMarkerPositions returns a boolean if a field has been set.

### SetMarkerPositionsNil

`func (o *FingerprintMatch) SetMarkerPositionsNil(b bool)`

 SetMarkerPositionsNil sets the value for MarkerPositions to be an explicit nil

### UnsetMarkerPositions
`func (o *FingerprintMatch) UnsetMarkerPositions()`

UnsetMarkerPositions ensures that no value is present for MarkerPositions, not even an explicit nil
### GetCreatedAt

`func (o *FingerprintMatch) GetCreatedAt() time.Time`

GetCreatedAt returns the CreatedAt field if non-nil, zero value otherwise.

### GetCreatedAtOk

`func (o *FingerprintMatch) GetCreatedAtOk() (*time.Time, bool)`

GetCreatedAtOk returns a tuple with the CreatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreatedAt

`func (o *FingerprintMatch) SetCreatedAt(v time.Time)`

SetCreatedAt sets CreatedAt field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


