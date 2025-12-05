# ChatMessage

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Role** | **string** |  | 
**Content** | **string** |  | 
**Name** | Pointer to **NullableString** |  | [optional] 

## Methods

### NewChatMessage

`func NewChatMessage(role string, content string, ) *ChatMessage`

NewChatMessage instantiates a new ChatMessage object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewChatMessageWithDefaults

`func NewChatMessageWithDefaults() *ChatMessage`

NewChatMessageWithDefaults instantiates a new ChatMessage object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetRole

`func (o *ChatMessage) GetRole() string`

GetRole returns the Role field if non-nil, zero value otherwise.

### GetRoleOk

`func (o *ChatMessage) GetRoleOk() (*string, bool)`

GetRoleOk returns a tuple with the Role field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRole

`func (o *ChatMessage) SetRole(v string)`

SetRole sets Role field to given value.


### GetContent

`func (o *ChatMessage) GetContent() string`

GetContent returns the Content field if non-nil, zero value otherwise.

### GetContentOk

`func (o *ChatMessage) GetContentOk() (*string, bool)`

GetContentOk returns a tuple with the Content field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetContent

`func (o *ChatMessage) SetContent(v string)`

SetContent sets Content field to given value.


### GetName

`func (o *ChatMessage) GetName() string`

GetName returns the Name field if non-nil, zero value otherwise.

### GetNameOk

`func (o *ChatMessage) GetNameOk() (*string, bool)`

GetNameOk returns a tuple with the Name field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetName

`func (o *ChatMessage) SetName(v string)`

SetName sets Name field to given value.

### HasName

`func (o *ChatMessage) HasName() bool`

HasName returns a boolean if a field has been set.

### SetNameNil

`func (o *ChatMessage) SetNameNil(b bool)`

 SetNameNil sets the value for Name to be an explicit nil

### UnsetName
`func (o *ChatMessage) UnsetName()`

UnsetName ensures that no value is present for Name, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


