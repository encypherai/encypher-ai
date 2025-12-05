# AuditLogResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**OrganizationId** | **string** |  | 
**Logs** | [**[]AuditLogEntry**](AuditLogEntry.md) |  | 
**Total** | **int32** |  | 
**Page** | **int32** |  | 
**PageSize** | **int32** |  | 
**HasMore** | **bool** |  | 

## Methods

### NewAuditLogResponse

`func NewAuditLogResponse(organizationId string, logs []AuditLogEntry, total int32, page int32, pageSize int32, hasMore bool, ) *AuditLogResponse`

NewAuditLogResponse instantiates a new AuditLogResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewAuditLogResponseWithDefaults

`func NewAuditLogResponseWithDefaults() *AuditLogResponse`

NewAuditLogResponseWithDefaults instantiates a new AuditLogResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetOrganizationId

`func (o *AuditLogResponse) GetOrganizationId() string`

GetOrganizationId returns the OrganizationId field if non-nil, zero value otherwise.

### GetOrganizationIdOk

`func (o *AuditLogResponse) GetOrganizationIdOk() (*string, bool)`

GetOrganizationIdOk returns a tuple with the OrganizationId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationId

`func (o *AuditLogResponse) SetOrganizationId(v string)`

SetOrganizationId sets OrganizationId field to given value.


### GetLogs

`func (o *AuditLogResponse) GetLogs() []AuditLogEntry`

GetLogs returns the Logs field if non-nil, zero value otherwise.

### GetLogsOk

`func (o *AuditLogResponse) GetLogsOk() (*[]AuditLogEntry, bool)`

GetLogsOk returns a tuple with the Logs field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLogs

`func (o *AuditLogResponse) SetLogs(v []AuditLogEntry)`

SetLogs sets Logs field to given value.


### GetTotal

`func (o *AuditLogResponse) GetTotal() int32`

GetTotal returns the Total field if non-nil, zero value otherwise.

### GetTotalOk

`func (o *AuditLogResponse) GetTotalOk() (*int32, bool)`

GetTotalOk returns a tuple with the Total field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTotal

`func (o *AuditLogResponse) SetTotal(v int32)`

SetTotal sets Total field to given value.


### GetPage

`func (o *AuditLogResponse) GetPage() int32`

GetPage returns the Page field if non-nil, zero value otherwise.

### GetPageOk

`func (o *AuditLogResponse) GetPageOk() (*int32, bool)`

GetPageOk returns a tuple with the Page field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPage

`func (o *AuditLogResponse) SetPage(v int32)`

SetPage sets Page field to given value.


### GetPageSize

`func (o *AuditLogResponse) GetPageSize() int32`

GetPageSize returns the PageSize field if non-nil, zero value otherwise.

### GetPageSizeOk

`func (o *AuditLogResponse) GetPageSizeOk() (*int32, bool)`

GetPageSizeOk returns a tuple with the PageSize field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPageSize

`func (o *AuditLogResponse) SetPageSize(v int32)`

SetPageSize sets PageSize field to given value.


### GetHasMore

`func (o *AuditLogResponse) GetHasMore() bool`

GetHasMore returns the HasMore field if non-nil, zero value otherwise.

### GetHasMoreOk

`func (o *AuditLogResponse) GetHasMoreOk() (*bool, bool)`

GetHasMoreOk returns a tuple with the HasMore field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetHasMore

`func (o *AuditLogResponse) SetHasMore(v bool)`

SetHasMore sets HasMore field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


