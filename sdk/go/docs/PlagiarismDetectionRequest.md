# PlagiarismDetectionRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**TargetText** | **string** | Text to check for plagiarism | 
**TargetDocumentId** | Pointer to **NullableString** |  | [optional] 
**SegmentationLevel** | Pointer to **string** | Segmentation level to analyze | [optional] [default to "sentence"]
**IncludeHeatMap** | Pointer to **bool** | Whether to generate heat map visualization data | [optional] [default to true]
**MinMatchPercentage** | Pointer to **float32** | Minimum match percentage to include in results | [optional] [default to 0.0]

## Methods

### NewPlagiarismDetectionRequest

`func NewPlagiarismDetectionRequest(targetText string, ) *PlagiarismDetectionRequest`

NewPlagiarismDetectionRequest instantiates a new PlagiarismDetectionRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewPlagiarismDetectionRequestWithDefaults

`func NewPlagiarismDetectionRequestWithDefaults() *PlagiarismDetectionRequest`

NewPlagiarismDetectionRequestWithDefaults instantiates a new PlagiarismDetectionRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetTargetText

`func (o *PlagiarismDetectionRequest) GetTargetText() string`

GetTargetText returns the TargetText field if non-nil, zero value otherwise.

### GetTargetTextOk

`func (o *PlagiarismDetectionRequest) GetTargetTextOk() (*string, bool)`

GetTargetTextOk returns a tuple with the TargetText field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTargetText

`func (o *PlagiarismDetectionRequest) SetTargetText(v string)`

SetTargetText sets TargetText field to given value.


### GetTargetDocumentId

`func (o *PlagiarismDetectionRequest) GetTargetDocumentId() string`

GetTargetDocumentId returns the TargetDocumentId field if non-nil, zero value otherwise.

### GetTargetDocumentIdOk

`func (o *PlagiarismDetectionRequest) GetTargetDocumentIdOk() (*string, bool)`

GetTargetDocumentIdOk returns a tuple with the TargetDocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTargetDocumentId

`func (o *PlagiarismDetectionRequest) SetTargetDocumentId(v string)`

SetTargetDocumentId sets TargetDocumentId field to given value.

### HasTargetDocumentId

`func (o *PlagiarismDetectionRequest) HasTargetDocumentId() bool`

HasTargetDocumentId returns a boolean if a field has been set.

### SetTargetDocumentIdNil

`func (o *PlagiarismDetectionRequest) SetTargetDocumentIdNil(b bool)`

 SetTargetDocumentIdNil sets the value for TargetDocumentId to be an explicit nil

### UnsetTargetDocumentId
`func (o *PlagiarismDetectionRequest) UnsetTargetDocumentId()`

UnsetTargetDocumentId ensures that no value is present for TargetDocumentId, not even an explicit nil
### GetSegmentationLevel

`func (o *PlagiarismDetectionRequest) GetSegmentationLevel() string`

GetSegmentationLevel returns the SegmentationLevel field if non-nil, zero value otherwise.

### GetSegmentationLevelOk

`func (o *PlagiarismDetectionRequest) GetSegmentationLevelOk() (*string, bool)`

GetSegmentationLevelOk returns a tuple with the SegmentationLevel field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSegmentationLevel

`func (o *PlagiarismDetectionRequest) SetSegmentationLevel(v string)`

SetSegmentationLevel sets SegmentationLevel field to given value.

### HasSegmentationLevel

`func (o *PlagiarismDetectionRequest) HasSegmentationLevel() bool`

HasSegmentationLevel returns a boolean if a field has been set.

### GetIncludeHeatMap

`func (o *PlagiarismDetectionRequest) GetIncludeHeatMap() bool`

GetIncludeHeatMap returns the IncludeHeatMap field if non-nil, zero value otherwise.

### GetIncludeHeatMapOk

`func (o *PlagiarismDetectionRequest) GetIncludeHeatMapOk() (*bool, bool)`

GetIncludeHeatMapOk returns a tuple with the IncludeHeatMap field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIncludeHeatMap

`func (o *PlagiarismDetectionRequest) SetIncludeHeatMap(v bool)`

SetIncludeHeatMap sets IncludeHeatMap field to given value.

### HasIncludeHeatMap

`func (o *PlagiarismDetectionRequest) HasIncludeHeatMap() bool`

HasIncludeHeatMap returns a boolean if a field has been set.

### GetMinMatchPercentage

`func (o *PlagiarismDetectionRequest) GetMinMatchPercentage() float32`

GetMinMatchPercentage returns the MinMatchPercentage field if non-nil, zero value otherwise.

### GetMinMatchPercentageOk

`func (o *PlagiarismDetectionRequest) GetMinMatchPercentageOk() (*float32, bool)`

GetMinMatchPercentageOk returns a tuple with the MinMatchPercentage field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMinMatchPercentage

`func (o *PlagiarismDetectionRequest) SetMinMatchPercentage(v float32)`

SetMinMatchPercentage sets MinMatchPercentage field to given value.

### HasMinMatchPercentage

`func (o *PlagiarismDetectionRequest) HasMinMatchPercentage() bool`

HasMinMatchPercentage returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


