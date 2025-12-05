# HeatMapData

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Positions** | **[]map[string]interface{}** |  | 
**TotalSegments** | **int32** |  | 
**MatchedSegments** | **int32** |  | 
**MatchPercentage** | **float32** |  | 

## Methods

### NewHeatMapData

`func NewHeatMapData(positions []map[string]interface{}, totalSegments int32, matchedSegments int32, matchPercentage float32, ) *HeatMapData`

NewHeatMapData instantiates a new HeatMapData object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewHeatMapDataWithDefaults

`func NewHeatMapDataWithDefaults() *HeatMapData`

NewHeatMapDataWithDefaults instantiates a new HeatMapData object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetPositions

`func (o *HeatMapData) GetPositions() []map[string]interface{}`

GetPositions returns the Positions field if non-nil, zero value otherwise.

### GetPositionsOk

`func (o *HeatMapData) GetPositionsOk() (*[]map[string]interface{}, bool)`

GetPositionsOk returns a tuple with the Positions field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPositions

`func (o *HeatMapData) SetPositions(v []map[string]interface{})`

SetPositions sets Positions field to given value.


### GetTotalSegments

`func (o *HeatMapData) GetTotalSegments() int32`

GetTotalSegments returns the TotalSegments field if non-nil, zero value otherwise.

### GetTotalSegmentsOk

`func (o *HeatMapData) GetTotalSegmentsOk() (*int32, bool)`

GetTotalSegmentsOk returns a tuple with the TotalSegments field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalSegments

`func (o *HeatMapData) SetTotalSegments(v int32)`

SetTotalSegments sets TotalSegments field to given value.


### GetMatchedSegments

`func (o *HeatMapData) GetMatchedSegments() int32`

GetMatchedSegments returns the MatchedSegments field if non-nil, zero value otherwise.

### GetMatchedSegmentsOk

`func (o *HeatMapData) GetMatchedSegmentsOk() (*int32, bool)`

GetMatchedSegmentsOk returns a tuple with the MatchedSegments field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMatchedSegments

`func (o *HeatMapData) SetMatchedSegments(v int32)`

SetMatchedSegments sets MatchedSegments field to given value.


### GetMatchPercentage

`func (o *HeatMapData) GetMatchPercentage() float32`

GetMatchPercentage returns the MatchPercentage field if non-nil, zero value otherwise.

### GetMatchPercentageOk

`func (o *HeatMapData) GetMatchPercentageOk() (*float32, bool)`

GetMatchPercentageOk returns a tuple with the MatchPercentage field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMatchPercentage

`func (o *HeatMapData) SetMatchPercentage(v float32)`

SetMatchPercentage sets MatchPercentage field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


