# ContentAccessLogResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Id** | **string** |  | 
**AgreementId** | **string** |  | 
**ContentId** | **string** |  | 
**MemberId** | **string** |  | 
**AccessedAt** | **time.Time** |  | 
**AccessType** | **NullableString** |  | 
**AiCompanyName** | **string** |  | 

## Methods

### NewContentAccessLogResponse

`func NewContentAccessLogResponse(id string, agreementId string, contentId string, memberId string, accessedAt time.Time, accessType NullableString, aiCompanyName string, ) *ContentAccessLogResponse`

NewContentAccessLogResponse instantiates a new ContentAccessLogResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewContentAccessLogResponseWithDefaults

`func NewContentAccessLogResponseWithDefaults() *ContentAccessLogResponse`

NewContentAccessLogResponseWithDefaults instantiates a new ContentAccessLogResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetId

`func (o *ContentAccessLogResponse) GetId() string`

GetId returns the Id field if non-nil, zero value otherwise.

### GetIdOk

`func (o *ContentAccessLogResponse) GetIdOk() (*string, bool)`

GetIdOk returns a tuple with the Id field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetId

`func (o *ContentAccessLogResponse) SetId(v string)`

SetId sets Id field to given value.


### GetAgreementId

`func (o *ContentAccessLogResponse) GetAgreementId() string`

GetAgreementId returns the AgreementId field if non-nil, zero value otherwise.

### GetAgreementIdOk

`func (o *ContentAccessLogResponse) GetAgreementIdOk() (*string, bool)`

GetAgreementIdOk returns a tuple with the AgreementId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAgreementId

`func (o *ContentAccessLogResponse) SetAgreementId(v string)`

SetAgreementId sets AgreementId field to given value.


### GetContentId

`func (o *ContentAccessLogResponse) GetContentId() string`

GetContentId returns the ContentId field if non-nil, zero value otherwise.

### GetContentIdOk

`func (o *ContentAccessLogResponse) GetContentIdOk() (*string, bool)`

GetContentIdOk returns a tuple with the ContentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetContentId

`func (o *ContentAccessLogResponse) SetContentId(v string)`

SetContentId sets ContentId field to given value.


### GetMemberId

`func (o *ContentAccessLogResponse) GetMemberId() string`

GetMemberId returns the MemberId field if non-nil, zero value otherwise.

### GetMemberIdOk

`func (o *ContentAccessLogResponse) GetMemberIdOk() (*string, bool)`

GetMemberIdOk returns a tuple with the MemberId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMemberId

`func (o *ContentAccessLogResponse) SetMemberId(v string)`

SetMemberId sets MemberId field to given value.


### GetAccessedAt

`func (o *ContentAccessLogResponse) GetAccessedAt() time.Time`

GetAccessedAt returns the AccessedAt field if non-nil, zero value otherwise.

### GetAccessedAtOk

`func (o *ContentAccessLogResponse) GetAccessedAtOk() (*time.Time, bool)`

GetAccessedAtOk returns a tuple with the AccessedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAccessedAt

`func (o *ContentAccessLogResponse) SetAccessedAt(v time.Time)`

SetAccessedAt sets AccessedAt field to given value.


### GetAccessType

`func (o *ContentAccessLogResponse) GetAccessType() string`

GetAccessType returns the AccessType field if non-nil, zero value otherwise.

### GetAccessTypeOk

`func (o *ContentAccessLogResponse) GetAccessTypeOk() (*string, bool)`

GetAccessTypeOk returns a tuple with the AccessType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAccessType

`func (o *ContentAccessLogResponse) SetAccessType(v string)`

SetAccessType sets AccessType field to given value.


### SetAccessTypeNil

`func (o *ContentAccessLogResponse) SetAccessTypeNil(b bool)`

 SetAccessTypeNil sets the value for AccessType to be an explicit nil

### UnsetAccessType
`func (o *ContentAccessLogResponse) UnsetAccessType()`

UnsetAccessType ensures that no value is present for AccessType, not even an explicit nil
### GetAiCompanyName

`func (o *ContentAccessLogResponse) GetAiCompanyName() string`

GetAiCompanyName returns the AiCompanyName field if non-nil, zero value otherwise.

### GetAiCompanyNameOk

`func (o *ContentAccessLogResponse) GetAiCompanyNameOk() (*string, bool)`

GetAiCompanyNameOk returns a tuple with the AiCompanyName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAiCompanyName

`func (o *ContentAccessLogResponse) SetAiCompanyName(v string)`

SetAiCompanyName sets AiCompanyName field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


