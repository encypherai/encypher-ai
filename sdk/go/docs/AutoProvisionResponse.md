# AutoProvisionResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Success** | **bool** | Whether provisioning was successful | 
**Message** | **string** | Success or error message | 
**OrganizationId** | **string** | Created organization ID | 
**OrganizationName** | **string** | Organization name | 
**UserId** | Pointer to **NullableString** |  | [optional] 
**ApiKey** | [**APIKeyResponse**](APIKeyResponse.md) | Generated API key | 
**Tier** | **string** | Organization tier | 
**FeaturesEnabled** | **map[string]bool** | Enabled features | 
**QuotaLimits** | **map[string]int32** | Quota limits | 
**NextSteps** | **map[string]string** | Next steps and documentation links | 

## Methods

### NewAutoProvisionResponse

`func NewAutoProvisionResponse(success bool, message string, organizationId string, organizationName string, apiKey APIKeyResponse, tier string, featuresEnabled map[string]bool, quotaLimits map[string]int32, nextSteps map[string]string, ) *AutoProvisionResponse`

NewAutoProvisionResponse instantiates a new AutoProvisionResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewAutoProvisionResponseWithDefaults

`func NewAutoProvisionResponseWithDefaults() *AutoProvisionResponse`

NewAutoProvisionResponseWithDefaults instantiates a new AutoProvisionResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSuccess

`func (o *AutoProvisionResponse) GetSuccess() bool`

GetSuccess returns the Success field if non-nil, zero value otherwise.

### GetSuccessOk

`func (o *AutoProvisionResponse) GetSuccessOk() (*bool, bool)`

GetSuccessOk returns a tuple with the Success field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSuccess

`func (o *AutoProvisionResponse) SetSuccess(v bool)`

SetSuccess sets Success field to given value.


### GetMessage

`func (o *AutoProvisionResponse) GetMessage() string`

GetMessage returns the Message field if non-nil, zero value otherwise.

### GetMessageOk

`func (o *AutoProvisionResponse) GetMessageOk() (*string, bool)`

GetMessageOk returns a tuple with the Message field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMessage

`func (o *AutoProvisionResponse) SetMessage(v string)`

SetMessage sets Message field to given value.


### GetOrganizationId

`func (o *AutoProvisionResponse) GetOrganizationId() string`

GetOrganizationId returns the OrganizationId field if non-nil, zero value otherwise.

### GetOrganizationIdOk

`func (o *AutoProvisionResponse) GetOrganizationIdOk() (*string, bool)`

GetOrganizationIdOk returns a tuple with the OrganizationId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationId

`func (o *AutoProvisionResponse) SetOrganizationId(v string)`

SetOrganizationId sets OrganizationId field to given value.


### GetOrganizationName

`func (o *AutoProvisionResponse) GetOrganizationName() string`

GetOrganizationName returns the OrganizationName field if non-nil, zero value otherwise.

### GetOrganizationNameOk

`func (o *AutoProvisionResponse) GetOrganizationNameOk() (*string, bool)`

GetOrganizationNameOk returns a tuple with the OrganizationName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationName

`func (o *AutoProvisionResponse) SetOrganizationName(v string)`

SetOrganizationName sets OrganizationName field to given value.


### GetUserId

`func (o *AutoProvisionResponse) GetUserId() string`

GetUserId returns the UserId field if non-nil, zero value otherwise.

### GetUserIdOk

`func (o *AutoProvisionResponse) GetUserIdOk() (*string, bool)`

GetUserIdOk returns a tuple with the UserId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUserId

`func (o *AutoProvisionResponse) SetUserId(v string)`

SetUserId sets UserId field to given value.

### HasUserId

`func (o *AutoProvisionResponse) HasUserId() bool`

HasUserId returns a boolean if a field has been set.

### SetUserIdNil

`func (o *AutoProvisionResponse) SetUserIdNil(b bool)`

 SetUserIdNil sets the value for UserId to be an explicit nil

### UnsetUserId
`func (o *AutoProvisionResponse) UnsetUserId()`

UnsetUserId ensures that no value is present for UserId, not even an explicit nil
### GetApiKey

`func (o *AutoProvisionResponse) GetApiKey() APIKeyResponse`

GetApiKey returns the ApiKey field if non-nil, zero value otherwise.

### GetApiKeyOk

`func (o *AutoProvisionResponse) GetApiKeyOk() (*APIKeyResponse, bool)`

GetApiKeyOk returns a tuple with the ApiKey field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetApiKey

`func (o *AutoProvisionResponse) SetApiKey(v APIKeyResponse)`

SetApiKey sets ApiKey field to given value.


### GetTier

`func (o *AutoProvisionResponse) GetTier() string`

GetTier returns the Tier field if non-nil, zero value otherwise.

### GetTierOk

`func (o *AutoProvisionResponse) GetTierOk() (*string, bool)`

GetTierOk returns a tuple with the Tier field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTier

`func (o *AutoProvisionResponse) SetTier(v string)`

SetTier sets Tier field to given value.


### GetFeaturesEnabled

`func (o *AutoProvisionResponse) GetFeaturesEnabled() map[string]bool`

GetFeaturesEnabled returns the FeaturesEnabled field if non-nil, zero value otherwise.

### GetFeaturesEnabledOk

`func (o *AutoProvisionResponse) GetFeaturesEnabledOk() (*map[string]bool, bool)`

GetFeaturesEnabledOk returns a tuple with the FeaturesEnabled field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetFeaturesEnabled

`func (o *AutoProvisionResponse) SetFeaturesEnabled(v map[string]bool)`

SetFeaturesEnabled sets FeaturesEnabled field to given value.


### GetQuotaLimits

`func (o *AutoProvisionResponse) GetQuotaLimits() map[string]int32`

GetQuotaLimits returns the QuotaLimits field if non-nil, zero value otherwise.

### GetQuotaLimitsOk

`func (o *AutoProvisionResponse) GetQuotaLimitsOk() (*map[string]int32, bool)`

GetQuotaLimitsOk returns a tuple with the QuotaLimits field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetQuotaLimits

`func (o *AutoProvisionResponse) SetQuotaLimits(v map[string]int32)`

SetQuotaLimits sets QuotaLimits field to given value.


### GetNextSteps

`func (o *AutoProvisionResponse) GetNextSteps() map[string]string`

GetNextSteps returns the NextSteps field if non-nil, zero value otherwise.

### GetNextStepsOk

`func (o *AutoProvisionResponse) GetNextStepsOk() (*map[string]string, bool)`

GetNextStepsOk returns a tuple with the NextSteps field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetNextSteps

`func (o *AutoProvisionResponse) SetNextSteps(v map[string]string)`

SetNextSteps sets NextSteps field to given value.



[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


