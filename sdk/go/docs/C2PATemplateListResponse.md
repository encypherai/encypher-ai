# C2PATemplateListResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Templates** | [**[]C2PATemplateResponse**](C2PATemplateResponse.md) |  | 
**Total** | **int32** |  | 
**Page** | **int32** |  | 
**PageSize** | **int32** |  | 

## Methods

### NewC2PATemplateListResponse

`func NewC2PATemplateListResponse(templates []C2PATemplateResponse, total int32, page int32, pageSize int32, ) *C2PATemplateListResponse`

NewC2PATemplateListResponse instantiates a new C2PATemplateListResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewC2PATemplateListResponseWithDefaults

`func NewC2PATemplateListResponseWithDefaults() *C2PATemplateListResponse`

NewC2PATemplateListResponseWithDefaults instantiates a new C2PATemplateListResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetTemplates

`func (o *C2PATemplateListResponse) GetTemplates() []C2PATemplateResponse`

GetTemplates returns the Templates field if non-nil, zero value otherwise.

### GetTemplatesOk

`func (o *C2PATemplateListResponse) GetTemplatesOk() (*[]C2PATemplateResponse, bool)`

GetTemplatesOk returns a tuple with the Templates field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTemplates

`func (o *C2PATemplateListResponse) SetTemplates(v []C2PATemplateResponse)`

SetTemplates sets Templates field to given value.


### GetTotal

`func (o *C2PATemplateListResponse) GetTotal() int32`

GetTotal returns the Total field if non-nil, zero value otherwise.

### GetTotalOk

`func (o *C2PATemplateListResponse) GetTotalOk() (*int32, bool)`

GetTotalOk returns a tuple with the Total field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotal

`func (o *C2PATemplateListResponse) SetTotal(v int32)`

SetTotal sets Total field to given value.


### GetPage

`func (o *C2PATemplateListResponse) GetPage() int32`

GetPage returns the Page field if non-nil, zero value otherwise.

### GetPageOk

`func (o *C2PATemplateListResponse) GetPageOk() (*int32, bool)`

GetPageOk returns a tuple with the Page field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPage

`func (o *C2PATemplateListResponse) SetPage(v int32)`

SetPage sets Page field to given value.


### GetPageSize

`func (o *C2PATemplateListResponse) GetPageSize() int32`

GetPageSize returns the PageSize field if non-nil, zero value otherwise.

### GetPageSizeOk

`func (o *C2PATemplateListResponse) GetPageSizeOk() (*int32, bool)`

GetPageSizeOk returns a tuple with the PageSize field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPageSize

`func (o *C2PATemplateListResponse) SetPageSize(v int32)`

SetPageSize sets PageSize field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


