# PlagiarismDetectionResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | **bool** |  | 
**ReportId** | **string** |  | 
**TargetDocumentId** | **NullableString** |  | 
**TotalSegments** | **int32** |  | 
**MatchedSegments** | **int32** |  | 
**OverallMatchPercentage** | **float32** |  | 
**SourceDocuments** | [**[]SourceDocumentMatch**](SourceDocumentMatch.md) |  | 
**HeatMapData** | [**NullableHeatMapData**](HeatMapData.md) |  | 
**ProcessingTimeMs** | **float32** |  | 
**ScanTimestamp** | **time.Time** |  | 

## Methods

### NewPlagiarismDetectionResponse

`func NewPlagiarismDetectionResponse(success bool, reportId string, targetDocumentId NullableString, totalSegments int32, matchedSegments int32, overallMatchPercentage float32, sourceDocuments []SourceDocumentMatch, heatMapData NullableHeatMapData, processingTimeMs float32, scanTimestamp time.Time, ) *PlagiarismDetectionResponse`

NewPlagiarismDetectionResponse instantiates a new PlagiarismDetectionResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewPlagiarismDetectionResponseWithDefaults

`func NewPlagiarismDetectionResponseWithDefaults() *PlagiarismDetectionResponse`

NewPlagiarismDetectionResponseWithDefaults instantiates a new PlagiarismDetectionResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *PlagiarismDetectionResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *PlagiarismDetectionResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *PlagiarismDetectionResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.


### GetReportId

`func (o *PlagiarismDetectionResponse) GetReportId() string`

GetReportId returns the ReportId field if non-nil, zero value otherwise.

### GetReportIdOk

`func (o *PlagiarismDetectionResponse) GetReportIdOk() (*string, bool)`

GetReportIdOk returns a tuple with the ReportId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetReportId

`func (o *PlagiarismDetectionResponse) SetReportId(v string)`

SetReportId sets ReportId field to given value.


### GetTargetDocumentId

`func (o *PlagiarismDetectionResponse) GetTargetDocumentId() string`

GetTargetDocumentId returns the TargetDocumentId field if non-nil, zero value otherwise.

### GetTargetDocumentIdOk

`func (o *PlagiarismDetectionResponse) GetTargetDocumentIdOk() (*string, bool)`

GetTargetDocumentIdOk returns a tuple with the TargetDocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTargetDocumentId

`func (o *PlagiarismDetectionResponse) SetTargetDocumentId(v string)`

SetTargetDocumentId sets TargetDocumentId field to given value.


### SetTargetDocumentIdNil

`func (o *PlagiarismDetectionResponse) SetTargetDocumentIdNil(b bool)`

 SetTargetDocumentIdNil sets the value for TargetDocumentId to be an explicit nil

### UnsetTargetDocumentId
`func (o *PlagiarismDetectionResponse) UnsetTargetDocumentId()`

UnsetTargetDocumentId ensures that no value is present for TargetDocumentId, not even an explicit nil
### GetTotalSegments

`func (o *PlagiarismDetectionResponse) GetTotalSegments() int32`

GetTotalSegments returns the TotalSegments field if non-nil, zero value otherwise.

### GetTotalSegmentsOk

`func (o *PlagiarismDetectionResponse) GetTotalSegmentsOk() (*int32, bool)`

GetTotalSegmentsOk returns a tuple with the TotalSegments field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalSegments

`func (o *PlagiarismDetectionResponse) SetTotalSegments(v int32)`

SetTotalSegments sets TotalSegments field to given value.


### GetMatchedSegments

`func (o *PlagiarismDetectionResponse) GetMatchedSegments() int32`

GetMatchedSegments returns the MatchedSegments field if non-nil, zero value otherwise.

### GetMatchedSegmentsOk

`func (o *PlagiarismDetectionResponse) GetMatchedSegmentsOk() (*int32, bool)`

GetMatchedSegmentsOk returns a tuple with the MatchedSegments field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMatchedSegments

`func (o *PlagiarismDetectionResponse) SetMatchedSegments(v int32)`

SetMatchedSegments sets MatchedSegments field to given value.


### GetOverallMatchPercentage

`func (o *PlagiarismDetectionResponse) GetOverallMatchPercentage() float32`

GetOverallMatchPercentage returns the OverallMatchPercentage field if non-nil, zero value otherwise.

### GetOverallMatchPercentageOk

`func (o *PlagiarismDetectionResponse) GetOverallMatchPercentageOk() (*float32, bool)`

GetOverallMatchPercentageOk returns a tuple with the OverallMatchPercentage field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOverallMatchPercentage

`func (o *PlagiarismDetectionResponse) SetOverallMatchPercentage(v float32)`

SetOverallMatchPercentage sets OverallMatchPercentage field to given value.


### GetSourceDocuments

`func (o *PlagiarismDetectionResponse) GetSourceDocuments() []SourceDocumentMatch`

GetSourceDocuments returns the SourceDocuments field if non-nil, zero value otherwise.

### GetSourceDocumentsOk

`func (o *PlagiarismDetectionResponse) GetSourceDocumentsOk() (*[]SourceDocumentMatch, bool)`

GetSourceDocumentsOk returns a tuple with the SourceDocuments field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSourceDocuments

`func (o *PlagiarismDetectionResponse) SetSourceDocuments(v []SourceDocumentMatch)`

SetSourceDocuments sets SourceDocuments field to given value.


### GetHeatMapData

`func (o *PlagiarismDetectionResponse) GetHeatMapData() HeatMapData`

GetHeatMapData returns the HeatMapData field if non-nil, zero value otherwise.

### GetHeatMapDataOk

`func (o *PlagiarismDetectionResponse) GetHeatMapDataOk() (*HeatMapData, bool)`

GetHeatMapDataOk returns a tuple with the HeatMapData field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetHeatMapData

`func (o *PlagiarismDetectionResponse) SetHeatMapData(v HeatMapData)`

SetHeatMapData sets HeatMapData field to given value.


### SetHeatMapDataNil

`func (o *PlagiarismDetectionResponse) SetHeatMapDataNil(b bool)`

 SetHeatMapDataNil sets the value for HeatMapData to be an explicit nil

### UnsetHeatMapData
`func (o *PlagiarismDetectionResponse) UnsetHeatMapData()`

UnsetHeatMapData ensures that no value is present for HeatMapData, not even an explicit nil
### GetProcessingTimeMs

`func (o *PlagiarismDetectionResponse) GetProcessingTimeMs() float32`

GetProcessingTimeMs returns the ProcessingTimeMs field if non-nil, zero value otherwise.

### GetProcessingTimeMsOk

`func (o *PlagiarismDetectionResponse) GetProcessingTimeMsOk() (*float32, bool)`

GetProcessingTimeMsOk returns a tuple with the ProcessingTimeMs field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetProcessingTimeMs

`func (o *PlagiarismDetectionResponse) SetProcessingTimeMs(v float32)`

SetProcessingTimeMs sets ProcessingTimeMs field to given value.


### GetScanTimestamp

`func (o *PlagiarismDetectionResponse) GetScanTimestamp() time.Time`

GetScanTimestamp returns the ScanTimestamp field if non-nil, zero value otherwise.

### GetScanTimestampOk

`func (o *PlagiarismDetectionResponse) GetScanTimestampOk() (*time.Time, bool)`

GetScanTimestampOk returns a tuple with the ScanTimestamp field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetScanTimestamp

`func (o *PlagiarismDetectionResponse) SetScanTimestamp(v time.Time)`

SetScanTimestamp sets ScanTimestamp field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


