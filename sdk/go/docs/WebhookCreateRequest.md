# WebhookCreateRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Url** | **string** | Webhook URL (must be HTTPS) | 
**Events** | **[]string** | Events to subscribe to | 
**Secret** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewWebhookCreateRequest

`func NewWebhookCreateRequest(url string, events []string, ) *WebhookCreateRequest`

NewWebhookCreateRequest instantiates a new WebhookCreateRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewWebhookCreateRequestWithDefaults

`func NewWebhookCreateRequestWithDefaults() *WebhookCreateRequest`

NewWebhookCreateRequestWithDefaults instantiates a new WebhookCreateRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetUrl

`func (o *WebhookCreateRequest) GetUrl() string`

GetUrl returns the Url field if non-nil, zero value otherwise.

### GetUrlOk

`func (o *WebhookCreateRequest) GetUrlOk() (*string, bool)`

GetUrlOk returns a tuple with the Url field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetUrl

`func (o *WebhookCreateRequest) SetUrl(v string)`

SetUrl sets Url field to given value.


### GetEvents

`func (o *WebhookCreateRequest) GetEvents() []string`

GetEvents returns the Events field if non-nil, zero value otherwise.

### GetEventsOk

`func (o *WebhookCreateRequest) GetEventsOk() (*[]string, bool)`

GetEventsOk returns a tuple with the Events field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEvents

`func (o *WebhookCreateRequest) SetEvents(v []string)`

SetEvents sets Events field to given value.


### GetSecret

`func (o *WebhookCreateRequest) GetSecret() string`

GetSecret returns the Secret field if non-nil, zero value otherwise.

### GetSecretOk

`func (o *WebhookCreateRequest) GetSecretOk() (*string, bool)`

GetSecretOk returns a tuple with the Secret field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSecret

`func (o *WebhookCreateRequest) SetSecret(v string)`

SetSecret sets Secret field to given value.

### HasSecret

`func (o *WebhookCreateRequest) HasSecret() bool`

HasSecret returns a boolean if a field has been set.

### SetSecretNil

`func (o *WebhookCreateRequest) SetSecretNil(b bool)`

 SetSecretNil sets the value for Secret to be an explicit nil

### UnsetSecret
`func (o *WebhookCreateRequest) UnsetSecret()`

UnsetSecret ensures that no value is present for Secret, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


