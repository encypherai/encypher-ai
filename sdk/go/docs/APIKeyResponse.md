# APIKeyResponse

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ApiKey** | **string** | Generated API key | 
**KeyId** | **string** | API key identifier | 
**OrganizationId** | **string** | Organization identifier | 
**Tier** | **string** | Organization tier | 
**CreatedAt** | **time.Time** | Creation timestamp | 
**ExpiresAt** | Pointer to **NullableTime** |  | [optional] 

## Methods

### NewAPIKeyResponse

`func NewAPIKeyResponse(apiKey string, keyId string, organizationId string, tier string, createdAt time.Time, ) *APIKeyResponse`

NewAPIKeyResponse instantiates a new APIKeyResponse object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewAPIKeyResponseWithDefaults

`func NewAPIKeyResponseWithDefaults() *APIKeyResponse`

NewAPIKeyResponseWithDefaults instantiates a new APIKeyResponse object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetApiKey

`func (o *APIKeyResponse) GetApiKey() string`

GetApiKey returns the ApiKey field if non-nil, zero value otherwise.

### GetApiKeyOk

`func (o *APIKeyResponse) GetApiKeyOk() (*string, bool)`

GetApiKeyOk returns a tuple with the ApiKey field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetApiKey

`func (o *APIKeyResponse) SetApiKey(v string)`

SetApiKey sets ApiKey field to given value.


### GetKeyId

`func (o *APIKeyResponse) GetKeyId() string`

GetKeyId returns the KeyId field if non-nil, zero value otherwise.

### GetKeyIdOk

`func (o *APIKeyResponse) GetKeyIdOk() (*string, bool)`

GetKeyIdOk returns a tuple with the KeyId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetKeyId

`func (o *APIKeyResponse) SetKeyId(v string)`

SetKeyId sets KeyId field to given value.


### GetOrganizationId

`func (o *APIKeyResponse) GetOrganizationId() string`

GetOrganizationId returns the OrganizationId field if non-nil, zero value otherwise.

### GetOrganizationIdOk

`func (o *APIKeyResponse) GetOrganizationIdOk() (*string, bool)`

GetOrganizationIdOk returns a tuple with the OrganizationId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationId

`func (o *APIKeyResponse) SetOrganizationId(v string)`

SetOrganizationId sets OrganizationId field to given value.


### GetTier

`func (o *APIKeyResponse) GetTier() string`

GetTier returns the Tier field if non-nil, zero value otherwise.

### GetTierOk

`func (o *APIKeyResponse) GetTierOk() (*string, bool)`

GetTierOk returns a tuple with the Tier field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTier

`func (o *APIKeyResponse) SetTier(v string)`

SetTier sets Tier field to given value.


### GetCreatedAt

`func (o *APIKeyResponse) GetCreatedAt() time.Time`

GetCreatedAt returns the CreatedAt field if non-nil, zero value otherwise.

### GetCreatedAtOk

`func (o *APIKeyResponse) GetCreatedAtOk() (*time.Time, bool)`

GetCreatedAtOk returns a tuple with the CreatedAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCreatedAt

`func (o *APIKeyResponse) SetCreatedAt(v time.Time)`

SetCreatedAt sets CreatedAt field to given value.


### GetExpiresAt

`func (o *APIKeyResponse) GetExpiresAt() time.Time`

GetExpiresAt returns the ExpiresAt field if non-nil, zero value otherwise.

### GetExpiresAtOk

`func (o *APIKeyResponse) GetExpiresAtOk() (*time.Time, bool)`

GetExpiresAtOk returns a tuple with the ExpiresAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetExpiresAt

`func (o *APIKeyResponse) SetExpiresAt(v time.Time)`

SetExpiresAt sets ExpiresAt field to given value.

### HasExpiresAt

`func (o *APIKeyResponse) HasExpiresAt() bool`

HasExpiresAt returns a boolean if a field has been set.

### SetExpiresAtNil

`func (o *APIKeyResponse) SetExpiresAtNil(b bool)`

 SetExpiresAtNil sets the value for ExpiresAt to be an explicit nil

### UnsetExpiresAt
`func (o *APIKeyResponse) UnsetExpiresAt()`

UnsetExpiresAt ensures that no value is present for ExpiresAt, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


