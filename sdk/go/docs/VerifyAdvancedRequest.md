# VerifyAdvancedRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Text** | **string** |  | 
**IncludeAttribution** | Pointer to **bool** |  | [optional] [default to false]
**DetectPlagiarism** | Pointer to **bool** |  | [optional] [default to false]
**IncludeHeatMap** | Pointer to **bool** |  | [optional] [default to false]
**MinMatchPercentage** | Pointer to **float32** |  | [optional] [default to 0.0]
**SegmentationLevel** | Pointer to **string** |  | [optional] [default to "sentence"]
**SearchScope** | Pointer to **string** |  | [optional] [default to "organization"]
**FuzzySearch** | Pointer to [**NullableFuzzySearchConfig**](FuzzySearchConfig.md) |  | [optional] 

## Methods

### NewVerifyAdvancedRequest

`func NewVerifyAdvancedRequest(text string, ) *VerifyAdvancedRequest`

NewVerifyAdvancedRequest instantiates a new VerifyAdvancedRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewVerifyAdvancedRequestWithDefaults

`func NewVerifyAdvancedRequestWithDefaults() *VerifyAdvancedRequest`

NewVerifyAdvancedRequestWithDefaults instantiates a new VerifyAdvancedRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetText

`func (o *VerifyAdvancedRequest) GetText() string`

GetText returns the Text field if non-nil, zero value otherwise.

### GetTextOk

`func (o *VerifyAdvancedRequest) GetTextOk() (*string, bool)`

GetTextOk returns a tuple with the Text field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetText

`func (o *VerifyAdvancedRequest) SetText(v string)`

SetText sets Text field to given value.


### GetIncludeAttribution

`func (o *VerifyAdvancedRequest) GetIncludeAttribution() bool`

GetIncludeAttribution returns the IncludeAttribution field if non-nil, zero value otherwise.

### GetIncludeAttributionOk

`func (o *VerifyAdvancedRequest) GetIncludeAttributionOk() (*bool, bool)`

GetIncludeAttributionOk returns a tuple with the IncludeAttribution field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIncludeAttribution

`func (o *VerifyAdvancedRequest) SetIncludeAttribution(v bool)`

SetIncludeAttribution sets IncludeAttribution field to given value.

### HasIncludeAttribution

`func (o *VerifyAdvancedRequest) HasIncludeAttribution() bool`

HasIncludeAttribution returns a boolean if a field has been set.

### GetDetectPlagiarism

`func (o *VerifyAdvancedRequest) GetDetectPlagiarism() bool`

GetDetectPlagiarism returns the DetectPlagiarism field if non-nil, zero value otherwise.

### GetDetectPlagiarismOk

`func (o *VerifyAdvancedRequest) GetDetectPlagiarismOk() (*bool, bool)`

GetDetectPlagiarismOk returns a tuple with the DetectPlagiarism field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDetectPlagiarism

`func (o *VerifyAdvancedRequest) SetDetectPlagiarism(v bool)`

SetDetectPlagiarism sets DetectPlagiarism field to given value.

### HasDetectPlagiarism

`func (o *VerifyAdvancedRequest) HasDetectPlagiarism() bool`

HasDetectPlagiarism returns a boolean if a field has been set.

### GetIncludeHeatMap

`func (o *VerifyAdvancedRequest) GetIncludeHeatMap() bool`

GetIncludeHeatMap returns the IncludeHeatMap field if non-nil, zero value otherwise.

### GetIncludeHeatMapOk

`func (o *VerifyAdvancedRequest) GetIncludeHeatMapOk() (*bool, bool)`

GetIncludeHeatMapOk returns a tuple with the IncludeHeatMap field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIncludeHeatMap

`func (o *VerifyAdvancedRequest) SetIncludeHeatMap(v bool)`

SetIncludeHeatMap sets IncludeHeatMap field to given value.

### HasIncludeHeatMap

`func (o *VerifyAdvancedRequest) HasIncludeHeatMap() bool`

HasIncludeHeatMap returns a boolean if a field has been set.

### GetMinMatchPercentage

`func (o *VerifyAdvancedRequest) GetMinMatchPercentage() float32`

GetMinMatchPercentage returns the MinMatchPercentage field if non-nil, zero value otherwise.

### GetMinMatchPercentageOk

`func (o *VerifyAdvancedRequest) GetMinMatchPercentageOk() (*float32, bool)`

GetMinMatchPercentageOk returns a tuple with the MinMatchPercentage field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMinMatchPercentage

`func (o *VerifyAdvancedRequest) SetMinMatchPercentage(v float32)`

SetMinMatchPercentage sets MinMatchPercentage field to given value.

### HasMinMatchPercentage

`func (o *VerifyAdvancedRequest) HasMinMatchPercentage() bool`

HasMinMatchPercentage returns a boolean if a field has been set.

### GetSegmentationLevel

`func (o *VerifyAdvancedRequest) GetSegmentationLevel() string`

GetSegmentationLevel returns the SegmentationLevel field if non-nil, zero value otherwise.

### GetSegmentationLevelOk

`func (o *VerifyAdvancedRequest) GetSegmentationLevelOk() (*string, bool)`

GetSegmentationLevelOk returns a tuple with the SegmentationLevel field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSegmentationLevel

`func (o *VerifyAdvancedRequest) SetSegmentationLevel(v string)`

SetSegmentationLevel sets SegmentationLevel field to given value.

### HasSegmentationLevel

`func (o *VerifyAdvancedRequest) HasSegmentationLevel() bool`

HasSegmentationLevel returns a boolean if a field has been set.

### GetSearchScope

`func (o *VerifyAdvancedRequest) GetSearchScope() string`

GetSearchScope returns the SearchScope field if non-nil, zero value otherwise.

### GetSearchScopeOk

`func (o *VerifyAdvancedRequest) GetSearchScopeOk() (*string, bool)`

GetSearchScopeOk returns a tuple with the SearchScope field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSearchScope

`func (o *VerifyAdvancedRequest) SetSearchScope(v string)`

SetSearchScope sets SearchScope field to given value.

### HasSearchScope

`func (o *VerifyAdvancedRequest) HasSearchScope() bool`

HasSearchScope returns a boolean if a field has been set.

### GetFuzzySearch

`func (o *VerifyAdvancedRequest) GetFuzzySearch() FuzzySearchConfig`

GetFuzzySearch returns the FuzzySearch field if non-nil, zero value otherwise.

### GetFuzzySearchOk

`func (o *VerifyAdvancedRequest) GetFuzzySearchOk() (*FuzzySearchConfig, bool)`

GetFuzzySearchOk returns a tuple with the FuzzySearch field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFuzzySearch

`func (o *VerifyAdvancedRequest) SetFuzzySearch(v FuzzySearchConfig)`

SetFuzzySearch sets FuzzySearch field to given value.

### HasFuzzySearch

`func (o *VerifyAdvancedRequest) HasFuzzySearch() bool`

HasFuzzySearch returns a boolean if a field has been set.

### SetFuzzySearchNil

`func (o *VerifyAdvancedRequest) SetFuzzySearchNil(b bool)`

 SetFuzzySearchNil sets the value for FuzzySearch to be an explicit nil

### UnsetFuzzySearch
`func (o *VerifyAdvancedRequest) UnsetFuzzySearch()`

UnsetFuzzySearch ensures that no value is present for FuzzySearch, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


