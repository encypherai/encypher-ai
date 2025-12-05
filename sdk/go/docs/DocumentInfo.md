# DocumentInfo

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DocumentId** | **string** | Document identifier | 
**Title** | Pointer to **NullableString** |  | [optional] 
**PublishedAt** | Pointer to **NullableTime** |  | [optional] 
**Author** | Pointer to **NullableString** |  | [optional] 
**Organization** | **string** | Organization name | 

## Methods

### NewDocumentInfo

`func NewDocumentInfo(documentId string, organization string, ) *DocumentInfo`

NewDocumentInfo instantiates a new DocumentInfo object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewDocumentInfoWithDefaults

`func NewDocumentInfoWithDefaults() *DocumentInfo`

NewDocumentInfoWithDefaults instantiates a new DocumentInfo object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDocumentId

`func (o *DocumentInfo) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *DocumentInfo) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *DocumentInfo) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetTitle

`func (o *DocumentInfo) GetTitle() string`

GetTitle returns the Title field if non-nil, zero value otherwise.

### GetTitleOk

`func (o *DocumentInfo) GetTitleOk() (*string, bool)`

GetTitleOk returns a tuple with the Title field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTitle

`func (o *DocumentInfo) SetTitle(v string)`

SetTitle sets Title field to given value.

### HasTitle

`func (o *DocumentInfo) HasTitle() bool`

HasTitle returns a boolean if a field has been set.

### SetTitleNil

`func (o *DocumentInfo) SetTitleNil(b bool)`

 SetTitleNil sets the value for Title to be an explicit nil

### UnsetTitle
`func (o *DocumentInfo) UnsetTitle()`

UnsetTitle ensures that no value is present for Title, not even an explicit nil
### GetPublishedAt

`func (o *DocumentInfo) GetPublishedAt() time.Time`

GetPublishedAt returns the PublishedAt field if non-nil, zero value otherwise.

### GetPublishedAtOk

`func (o *DocumentInfo) GetPublishedAtOk() (*time.Time, bool)`

GetPublishedAtOk returns a tuple with the PublishedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPublishedAt

`func (o *DocumentInfo) SetPublishedAt(v time.Time)`

SetPublishedAt sets PublishedAt field to given value.

### HasPublishedAt

`func (o *DocumentInfo) HasPublishedAt() bool`

HasPublishedAt returns a boolean if a field has been set.

### SetPublishedAtNil

`func (o *DocumentInfo) SetPublishedAtNil(b bool)`

 SetPublishedAtNil sets the value for PublishedAt to be an explicit nil

### UnsetPublishedAt
`func (o *DocumentInfo) UnsetPublishedAt()`

UnsetPublishedAt ensures that no value is present for PublishedAt, not even an explicit nil
### GetAuthor

`func (o *DocumentInfo) GetAuthor() string`

GetAuthor returns the Author field if non-nil, zero value otherwise.

### GetAuthorOk

`func (o *DocumentInfo) GetAuthorOk() (*string, bool)`

GetAuthorOk returns a tuple with the Author field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAuthor

`func (o *DocumentInfo) SetAuthor(v string)`

SetAuthor sets Author field to given value.

### HasAuthor

`func (o *DocumentInfo) HasAuthor() bool`

HasAuthor returns a boolean if a field has been set.

### SetAuthorNil

`func (o *DocumentInfo) SetAuthorNil(b bool)`

 SetAuthorNil sets the value for Author to be an explicit nil

### UnsetAuthor
`func (o *DocumentInfo) UnsetAuthor()`

UnsetAuthor ensures that no value is present for Author, not even an explicit nil
### GetOrganization

`func (o *DocumentInfo) GetOrganization() string`

GetOrganization returns the Organization field if non-nil, zero value otherwise.

### GetOrganizationOk

`func (o *DocumentInfo) GetOrganizationOk() (*string, bool)`

GetOrganizationOk returns a tuple with the Organization field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganization

`func (o *DocumentInfo) SetOrganization(v string)`

SetOrganization sets Organization field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


