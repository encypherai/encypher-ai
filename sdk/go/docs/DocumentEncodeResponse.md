# DocumentEncodeResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | **bool** | Whether encoding was successful | 
**Message** | **string** | Success or error message | 
**DocumentId** | **string** | Document identifier | 
**OrganizationId** | **string** | Organization identifier | 
**Roots** | [**map[string]MerkleRootResponse**](MerkleRootResponse.md) | Dictionary mapping segmentation level to Merkle root | 
**TotalSegments** | **map[string]int32** | Number of segments at each level | 
**ProcessingTimeMs** | **float32** | Processing time in milliseconds | 

## Methods

### NewDocumentEncodeResponse

`func NewDocumentEncodeResponse(success bool, message string, documentId string, organizationId string, roots map[string]MerkleRootResponse, totalSegments map[string]int32, processingTimeMs float32, ) *DocumentEncodeResponse`

NewDocumentEncodeResponse instantiates a new DocumentEncodeResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewDocumentEncodeResponseWithDefaults

`func NewDocumentEncodeResponseWithDefaults() *DocumentEncodeResponse`

NewDocumentEncodeResponseWithDefaults instantiates a new DocumentEncodeResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *DocumentEncodeResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *DocumentEncodeResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *DocumentEncodeResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.


### GetMessage

`func (o *DocumentEncodeResponse) GetMessage() string`

GetMessage returns the Message field if non-nil, zero value otherwise.

### GetMessageOk

`func (o *DocumentEncodeResponse) GetMessageOk() (*string, bool)`

GetMessageOk returns a tuple with the Message field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMessage

`func (o *DocumentEncodeResponse) SetMessage(v string)`

SetMessage sets Message field to given value.


### GetDocumentId

`func (o *DocumentEncodeResponse) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *DocumentEncodeResponse) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *DocumentEncodeResponse) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetOrganizationId

`func (o *DocumentEncodeResponse) GetOrganizationId() string`

GetOrganizationId returns the OrganizationId field if non-nil, zero value otherwise.

### GetOrganizationIdOk

`func (o *DocumentEncodeResponse) GetOrganizationIdOk() (*string, bool)`

GetOrganizationIdOk returns a tuple with the OrganizationId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationId

`func (o *DocumentEncodeResponse) SetOrganizationId(v string)`

SetOrganizationId sets OrganizationId field to given value.


### GetRoots

`func (o *DocumentEncodeResponse) GetRoots() map[string]MerkleRootResponse`

GetRoots returns the Roots field if non-nil, zero value otherwise.

### GetRootsOk

`func (o *DocumentEncodeResponse) GetRootsOk() (*map[string]MerkleRootResponse, bool)`

GetRootsOk returns a tuple with the Roots field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRoots

`func (o *DocumentEncodeResponse) SetRoots(v map[string]MerkleRootResponse)`

SetRoots sets Roots field to given value.


### GetTotalSegments

`func (o *DocumentEncodeResponse) GetTotalSegments() map[string]int32`

GetTotalSegments returns the TotalSegments field if non-nil, zero value otherwise.

### GetTotalSegmentsOk

`func (o *DocumentEncodeResponse) GetTotalSegmentsOk() (*map[string]int32, bool)`

GetTotalSegmentsOk returns a tuple with the TotalSegments field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotalSegments

`func (o *DocumentEncodeResponse) SetTotalSegments(v map[string]int32)`

SetTotalSegments sets TotalSegments field to given value.


### GetProcessingTimeMs

`func (o *DocumentEncodeResponse) GetProcessingTimeMs() float32`

GetProcessingTimeMs returns the ProcessingTimeMs field if non-nil, zero value otherwise.

### GetProcessingTimeMsOk

`func (o *DocumentEncodeResponse) GetProcessingTimeMsOk() (*float32, bool)`

GetProcessingTimeMsOk returns a tuple with the ProcessingTimeMs field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetProcessingTimeMs

`func (o *DocumentEncodeResponse) SetProcessingTimeMs(v float32)`

SetProcessingTimeMs sets ProcessingTimeMs field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


