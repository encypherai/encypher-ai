# ContentStats

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**PeriodStart** | **string** |  | 
**PeriodEnd** | **string** |  | 
**DocumentsCount** | **int32** |  | 
**SentencesCount** | **int32** |  | 
**TotalCharacters** | **int32** |  | 
**UniqueContentHashCount** | **int32** |  | 
**ContentCategories** | Pointer to **map[string]interface{}** |  | [optional] 

## Methods

### NewContentStats

`func NewContentStats(periodStart string, periodEnd string, documentsCount int32, sentencesCount int32, totalCharacters int32, uniqueContentHashCount int32, ) *ContentStats`

NewContentStats instantiates a new ContentStats object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewContentStatsWithDefaults

`func NewContentStatsWithDefaults() *ContentStats`

NewContentStatsWithDefaults instantiates a new ContentStats object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetPeriodStart

`func (o *ContentStats) GetPeriodStart() string`

GetPeriodStart returns the PeriodStart field if non-nil, zero value otherwise.

### GetPeriodStartOk

`func (o *ContentStats) GetPeriodStartOk() (*string, bool)`

GetPeriodStartOk returns a tuple with the PeriodStart field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPeriodStart

`func (o *ContentStats) SetPeriodStart(v string)`

SetPeriodStart sets PeriodStart field to given value.


### GetPeriodEnd

`func (o *ContentStats) GetPeriodEnd() string`

GetPeriodEnd returns the PeriodEnd field if non-nil, zero value otherwise.

### GetPeriodEndOk

`func (o *ContentStats) GetPeriodEndOk() (*string, bool)`

GetPeriodEndOk returns a tuple with the PeriodEnd field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPeriodEnd

`func (o *ContentStats) SetPeriodEnd(v string)`

SetPeriodEnd sets PeriodEnd field to given value.


### GetDocumentsCount

`func (o *ContentStats) GetDocumentsCount() int32`

GetDocumentsCount returns the DocumentsCount field if non-nil, zero value otherwise.

### GetDocumentsCountOk

`func (o *ContentStats) GetDocumentsCountOk() (*int32, bool)`

GetDocumentsCountOk returns a tuple with the DocumentsCount field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentsCount

`func (o *ContentStats) SetDocumentsCount(v int32)`

SetDocumentsCount sets DocumentsCount field to given value.


### GetSentencesCount

`func (o *ContentStats) GetSentencesCount() int32`

GetSentencesCount returns the SentencesCount field if non-nil, zero value otherwise.

### GetSentencesCountOk

`func (o *ContentStats) GetSentencesCountOk() (*int32, bool)`

GetSentencesCountOk returns a tuple with the SentencesCount field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSentencesCount

`func (o *ContentStats) SetSentencesCount(v int32)`

SetSentencesCount sets SentencesCount field to given value.


### GetTotalCharacters

`func (o *ContentStats) GetTotalCharacters() int32`

GetTotalCharacters returns the TotalCharacters field if non-nil, zero value otherwise.

### GetTotalCharactersOk

`func (o *ContentStats) GetTotalCharactersOk() (*int32, bool)`

GetTotalCharactersOk returns a tuple with the TotalCharacters field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalCharacters

`func (o *ContentStats) SetTotalCharacters(v int32)`

SetTotalCharacters sets TotalCharacters field to given value.


### GetUniqueContentHashCount

`func (o *ContentStats) GetUniqueContentHashCount() int32`

GetUniqueContentHashCount returns the UniqueContentHashCount field if non-nil, zero value otherwise.

### GetUniqueContentHashCountOk

`func (o *ContentStats) GetUniqueContentHashCountOk() (*int32, bool)`

GetUniqueContentHashCountOk returns a tuple with the UniqueContentHashCount field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUniqueContentHashCount

`func (o *ContentStats) SetUniqueContentHashCount(v int32)`

SetUniqueContentHashCount sets UniqueContentHashCount field to given value.


### GetContentCategories

`func (o *ContentStats) GetContentCategories() map[string]interface{}`

GetContentCategories returns the ContentCategories field if non-nil, zero value otherwise.

### GetContentCategoriesOk

`func (o *ContentStats) GetContentCategoriesOk() (*map[string]interface{}, bool)`

GetContentCategoriesOk returns a tuple with the ContentCategories field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetContentCategories

`func (o *ContentStats) SetContentCategories(v map[string]interface{})`

SetContentCategories sets ContentCategories field to given value.

### HasContentCategories

`func (o *ContentStats) HasContentCategories() bool`

HasContentCategories returns a boolean if a field has been set.

### SetContentCategoriesNil

`func (o *ContentStats) SetContentCategoriesNil(b bool)`

 SetContentCategoriesNil sets the value for ContentCategories to be an explicit nil

### UnsetContentCategories
`func (o *ContentStats) UnsetContentCategories()`

UnsetContentCategories ensures that no value is present for ContentCategories, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


