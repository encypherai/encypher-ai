# MultiSourceLookupRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**TextSegment** | **string** | Text segment to search for | 
**IncludeAllSources** | Pointer to **bool** | Return all matching sources (not just first) | [optional] [default to true]
**OrderBy** | Pointer to **string** | Ordering: chronological (earliest first), authority, or confidence | [optional] [default to "chronological"]
**IncludeAuthorityScore** | Pointer to **bool** | Include authority ranking scores (Enterprise feature) | [optional] [default to false]
**MaxResults** | Pointer to **int32** | Maximum number of sources to return | [optional] [default to 10]

## Methods

### NewMultiSourceLookupRequest

`func NewMultiSourceLookupRequest(textSegment string, ) *MultiSourceLookupRequest`

NewMultiSourceLookupRequest instantiates a new MultiSourceLookupRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewMultiSourceLookupRequestWithDefaults

`func NewMultiSourceLookupRequestWithDefaults() *MultiSourceLookupRequest`

NewMultiSourceLookupRequestWithDefaults instantiates a new MultiSourceLookupRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetTextSegment

`func (o *MultiSourceLookupRequest) GetTextSegment() string`

GetTextSegment returns the TextSegment field if non-nil, zero value otherwise.

### GetTextSegmentOk

`func (o *MultiSourceLookupRequest) GetTextSegmentOk() (*string, bool)`

GetTextSegmentOk returns a tuple with the TextSegment field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTextSegment

`func (o *MultiSourceLookupRequest) SetTextSegment(v string)`

SetTextSegment sets TextSegment field to given value.


### GetIncludeAllSources

`func (o *MultiSourceLookupRequest) GetIncludeAllSources() bool`

GetIncludeAllSources returns the IncludeAllSources field if non-nil, zero value otherwise.

### GetIncludeAllSourcesOk

`func (o *MultiSourceLookupRequest) GetIncludeAllSourcesOk() (*bool, bool)`

GetIncludeAllSourcesOk returns a tuple with the IncludeAllSources field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIncludeAllSources

`func (o *MultiSourceLookupRequest) SetIncludeAllSources(v bool)`

SetIncludeAllSources sets IncludeAllSources field to given value.

### HasIncludeAllSources

`func (o *MultiSourceLookupRequest) HasIncludeAllSources() bool`

HasIncludeAllSources returns a boolean if a field has been set.

### GetOrderBy

`func (o *MultiSourceLookupRequest) GetOrderBy() string`

GetOrderBy returns the OrderBy field if non-nil, zero value otherwise.

### GetOrderByOk

`func (o *MultiSourceLookupRequest) GetOrderByOk() (*string, bool)`

GetOrderByOk returns a tuple with the OrderBy field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrderBy

`func (o *MultiSourceLookupRequest) SetOrderBy(v string)`

SetOrderBy sets OrderBy field to given value.

### HasOrderBy

`func (o *MultiSourceLookupRequest) HasOrderBy() bool`

HasOrderBy returns a boolean if a field has been set.

### GetIncludeAuthorityScore

`func (o *MultiSourceLookupRequest) GetIncludeAuthorityScore() bool`

GetIncludeAuthorityScore returns the IncludeAuthorityScore field if non-nil, zero value otherwise.

### GetIncludeAuthorityScoreOk

`func (o *MultiSourceLookupRequest) GetIncludeAuthorityScoreOk() (*bool, bool)`

GetIncludeAuthorityScoreOk returns a tuple with the IncludeAuthorityScore field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIncludeAuthorityScore

`func (o *MultiSourceLookupRequest) SetIncludeAuthorityScore(v bool)`

SetIncludeAuthorityScore sets IncludeAuthorityScore field to given value.

### HasIncludeAuthorityScore

`func (o *MultiSourceLookupRequest) HasIncludeAuthorityScore() bool`

HasIncludeAuthorityScore returns a boolean if a field has been set.

### GetMaxResults

`func (o *MultiSourceLookupRequest) GetMaxResults() int32`

GetMaxResults returns the MaxResults field if non-nil, zero value otherwise.

### GetMaxResultsOk

`func (o *MultiSourceLookupRequest) GetMaxResultsOk() (*int32, bool)`

GetMaxResultsOk returns a tuple with the MaxResults field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMaxResults

`func (o *MultiSourceLookupRequest) SetMaxResults(v int32)`

SetMaxResults sets MaxResults field to given value.

### HasMaxResults

`func (o *MultiSourceLookupRequest) HasMaxResults() bool`

HasMaxResults returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


