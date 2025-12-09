# ContentMetadata

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | **int32** |  | 
**ContentType** | **string** |  | 
**WordCount** | **NullableInt32** |  | 
**SignedAt** | **time.Time** |  | 
**ContentHash** | **string** |  | 
**VerificationUrl** | **string** |  | 

## Methods

### NewContentMetadata

`func NewContentMetadata(id int32, contentType string, wordCount NullableInt32, signedAt time.Time, contentHash string, verificationUrl string, ) *ContentMetadata`

NewContentMetadata instantiates a new ContentMetadata object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewContentMetadataWithDefaults

`func NewContentMetadataWithDefaults() *ContentMetadata`

NewContentMetadataWithDefaults instantiates a new ContentMetadata object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *ContentMetadata) GetId() int32`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *ContentMetadata) GetIdOk() (*int32, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *ContentMetadata) SetId(v int32)`

SetId sets Id field to given value.


### GetContentType

`func (o *ContentMetadata) GetContentType() string`

GetContentType returns the ContentType field if non-nil, zero value otherwise.

### GetContentTypeOk

`func (o *ContentMetadata) GetContentTypeOk() (*string, bool)`

GetContentTypeOk returns a tuple with the ContentType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetContentType

`func (o *ContentMetadata) SetContentType(v string)`

SetContentType sets ContentType field to given value.


### GetWordCount

`func (o *ContentMetadata) GetWordCount() int32`

GetWordCount returns the WordCount field if non-nil, zero value otherwise.

### GetWordCountOk

`func (o *ContentMetadata) GetWordCountOk() (*int32, bool)`

GetWordCountOk returns a tuple with the WordCount field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetWordCount

`func (o *ContentMetadata) SetWordCount(v int32)`

SetWordCount sets WordCount field to given value.


### SetWordCountNil

`func (o *ContentMetadata) SetWordCountNil(b bool)`

 SetWordCountNil sets the value for WordCount to be an explicit nil

### UnsetWordCount
`func (o *ContentMetadata) UnsetWordCount()`

UnsetWordCount ensures that no value is present for WordCount, not even an explicit nil
### GetSignedAt

`func (o *ContentMetadata) GetSignedAt() time.Time`

GetSignedAt returns the SignedAt field if non-nil, zero value otherwise.

### GetSignedAtOk

`func (o *ContentMetadata) GetSignedAtOk() (*time.Time, bool)`

GetSignedAtOk returns a tuple with the SignedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignedAt

`func (o *ContentMetadata) SetSignedAt(v time.Time)`

SetSignedAt sets SignedAt field to given value.


### GetContentHash

`func (o *ContentMetadata) GetContentHash() string`

GetContentHash returns the ContentHash field if non-nil, zero value otherwise.

### GetContentHashOk

`func (o *ContentMetadata) GetContentHashOk() (*string, bool)`

GetContentHashOk returns a tuple with the ContentHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetContentHash

`func (o *ContentMetadata) SetContentHash(v string)`

SetContentHash sets ContentHash field to given value.


### GetVerificationUrl

`func (o *ContentMetadata) GetVerificationUrl() string`

GetVerificationUrl returns the VerificationUrl field if non-nil, zero value otherwise.

### GetVerificationUrlOk

`func (o *ContentMetadata) GetVerificationUrlOk() (*string, bool)`

GetVerificationUrlOk returns a tuple with the VerificationUrl field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetVerificationUrl

`func (o *ContentMetadata) SetVerificationUrl(v string)`

SetVerificationUrl sets VerificationUrl field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


