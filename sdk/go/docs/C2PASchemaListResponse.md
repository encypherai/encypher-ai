# C2PASchemaListResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Schemas** | [**[]C2PASchemaResponse**](C2PASchemaResponse.md) |  | 
**Total** | **int32** |  | 
**Page** | **int32** |  | 
**PageSize** | **int32** |  | 

## Methods

### NewC2PASchemaListResponse

`func NewC2PASchemaListResponse(schemas []C2PASchemaResponse, total int32, page int32, pageSize int32, ) *C2PASchemaListResponse`

NewC2PASchemaListResponse instantiates a new C2PASchemaListResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewC2PASchemaListResponseWithDefaults

`func NewC2PASchemaListResponseWithDefaults() *C2PASchemaListResponse`

NewC2PASchemaListResponseWithDefaults instantiates a new C2PASchemaListResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSchemas

`func (o *C2PASchemaListResponse) GetSchemas() []C2PASchemaResponse`

GetSchemas returns the Schemas field if non-nil, zero value otherwise.

### GetSchemasOk

`func (o *C2PASchemaListResponse) GetSchemasOk() (*[]C2PASchemaResponse, bool)`

GetSchemasOk returns a tuple with the Schemas field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSchemas

`func (o *C2PASchemaListResponse) SetSchemas(v []C2PASchemaResponse)`

SetSchemas sets Schemas field to given value.


### GetTotal

`func (o *C2PASchemaListResponse) GetTotal() int32`

GetTotal returns the Total field if non-nil, zero value otherwise.

### GetTotalOk

`func (o *C2PASchemaListResponse) GetTotalOk() (*int32, bool)`

GetTotalOk returns a tuple with the Total field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotal

`func (o *C2PASchemaListResponse) SetTotal(v int32)`

SetTotal sets Total field to given value.


### GetPage

`func (o *C2PASchemaListResponse) GetPage() int32`

GetPage returns the Page field if non-nil, zero value otherwise.

### GetPageOk

`func (o *C2PASchemaListResponse) GetPageOk() (*int32, bool)`

GetPageOk returns a tuple with the Page field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPage

`func (o *C2PASchemaListResponse) SetPage(v int32)`

SetPage sets Page field to given value.


### GetPageSize

`func (o *C2PASchemaListResponse) GetPageSize() int32`

GetPageSize returns the PageSize field if non-nil, zero value otherwise.

### GetPageSizeOk

`func (o *C2PASchemaListResponse) GetPageSizeOk() (*int32, bool)`

GetPageSizeOk returns a tuple with the PageSize field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPageSize

`func (o *C2PASchemaListResponse) SetPageSize(v int32)`

SetPageSize sets PageSize field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


