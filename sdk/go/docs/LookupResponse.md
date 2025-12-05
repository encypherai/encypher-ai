# LookupResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | **bool** | Whether the operation was successful | 
**Found** | **bool** | Whether the sentence was found | 
**DocumentTitle** | Pointer to **NullableString** |  | [optional] 
**OrganizationName** | Pointer to **NullableString** |  | [optional] 
**PublicationDate** | Pointer to **NullableTime** |  | [optional] 
**SentenceIndex** | Pointer to **NullableInt32** |  | [optional] 
**DocumentUrl** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewLookupResponse

`func NewLookupResponse(success bool, found bool, ) *LookupResponse`

NewLookupResponse instantiates a new LookupResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewLookupResponseWithDefaults

`func NewLookupResponseWithDefaults() *LookupResponse`

NewLookupResponseWithDefaults instantiates a new LookupResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *LookupResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *LookupResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *LookupResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.


### GetFound

`func (o *LookupResponse) GetFound() bool`

GetFound returns the Found field if non-nil, zero value otherwise.

### GetFoundOk

`func (o *LookupResponse) GetFoundOk() (*bool, bool)`

GetFoundOk returns a tuple with the Found field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFound

`func (o *LookupResponse) SetFound(v bool)`

SetFound sets Found field to given value.


### GetDocumentTitle

`func (o *LookupResponse) GetDocumentTitle() string`

GetDocumentTitle returns the DocumentTitle field if non-nil, zero value otherwise.

### GetDocumentTitleOk

`func (o *LookupResponse) GetDocumentTitleOk() (*string, bool)`

GetDocumentTitleOk returns a tuple with the DocumentTitle field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentTitle

`func (o *LookupResponse) SetDocumentTitle(v string)`

SetDocumentTitle sets DocumentTitle field to given value.

### HasDocumentTitle

`func (o *LookupResponse) HasDocumentTitle() bool`

HasDocumentTitle returns a boolean if a field has been set.

### SetDocumentTitleNil

`func (o *LookupResponse) SetDocumentTitleNil(b bool)`

 SetDocumentTitleNil sets the value for DocumentTitle to be an explicit nil

### UnsetDocumentTitle
`func (o *LookupResponse) UnsetDocumentTitle()`

UnsetDocumentTitle ensures that no value is present for DocumentTitle, not even an explicit nil
### GetOrganizationName

`func (o *LookupResponse) GetOrganizationName() string`

GetOrganizationName returns the OrganizationName field if non-nil, zero value otherwise.

### GetOrganizationNameOk

`func (o *LookupResponse) GetOrganizationNameOk() (*string, bool)`

GetOrganizationNameOk returns a tuple with the OrganizationName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationName

`func (o *LookupResponse) SetOrganizationName(v string)`

SetOrganizationName sets OrganizationName field to given value.

### HasOrganizationName

`func (o *LookupResponse) HasOrganizationName() bool`

HasOrganizationName returns a boolean if a field has been set.

### SetOrganizationNameNil

`func (o *LookupResponse) SetOrganizationNameNil(b bool)`

 SetOrganizationNameNil sets the value for OrganizationName to be an explicit nil

### UnsetOrganizationName
`func (o *LookupResponse) UnsetOrganizationName()`

UnsetOrganizationName ensures that no value is present for OrganizationName, not even an explicit nil
### GetPublicationDate

`func (o *LookupResponse) GetPublicationDate() time.Time`

GetPublicationDate returns the PublicationDate field if non-nil, zero value otherwise.

### GetPublicationDateOk

`func (o *LookupResponse) GetPublicationDateOk() (*time.Time, bool)`

GetPublicationDateOk returns a tuple with the PublicationDate field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPublicationDate

`func (o *LookupResponse) SetPublicationDate(v time.Time)`

SetPublicationDate sets PublicationDate field to given value.

### HasPublicationDate

`func (o *LookupResponse) HasPublicationDate() bool`

HasPublicationDate returns a boolean if a field has been set.

### SetPublicationDateNil

`func (o *LookupResponse) SetPublicationDateNil(b bool)`

 SetPublicationDateNil sets the value for PublicationDate to be an explicit nil

### UnsetPublicationDate
`func (o *LookupResponse) UnsetPublicationDate()`

UnsetPublicationDate ensures that no value is present for PublicationDate, not even an explicit nil
### GetSentenceIndex

`func (o *LookupResponse) GetSentenceIndex() int32`

GetSentenceIndex returns the SentenceIndex field if non-nil, zero value otherwise.

### GetSentenceIndexOk

`func (o *LookupResponse) GetSentenceIndexOk() (*int32, bool)`

GetSentenceIndexOk returns a tuple with the SentenceIndex field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSentenceIndex

`func (o *LookupResponse) SetSentenceIndex(v int32)`

SetSentenceIndex sets SentenceIndex field to given value.

### HasSentenceIndex

`func (o *LookupResponse) HasSentenceIndex() bool`

HasSentenceIndex returns a boolean if a field has been set.

### SetSentenceIndexNil

`func (o *LookupResponse) SetSentenceIndexNil(b bool)`

 SetSentenceIndexNil sets the value for SentenceIndex to be an explicit nil

### UnsetSentenceIndex
`func (o *LookupResponse) UnsetSentenceIndex()`

UnsetSentenceIndex ensures that no value is present for SentenceIndex, not even an explicit nil
### GetDocumentUrl

`func (o *LookupResponse) GetDocumentUrl() string`

GetDocumentUrl returns the DocumentUrl field if non-nil, zero value otherwise.

### GetDocumentUrlOk

`func (o *LookupResponse) GetDocumentUrlOk() (*string, bool)`

GetDocumentUrlOk returns a tuple with the DocumentUrl field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentUrl

`func (o *LookupResponse) SetDocumentUrl(v string)`

SetDocumentUrl sets DocumentUrl field to given value.

### HasDocumentUrl

`func (o *LookupResponse) HasDocumentUrl() bool`

HasDocumentUrl returns a boolean if a field has been set.

### SetDocumentUrlNil

`func (o *LookupResponse) SetDocumentUrlNil(b bool)`

 SetDocumentUrlNil sets the value for DocumentUrl to be an explicit nil

### UnsetDocumentUrl
`func (o *LookupResponse) UnsetDocumentUrl()`

UnsetDocumentUrl ensures that no value is present for DocumentUrl, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


