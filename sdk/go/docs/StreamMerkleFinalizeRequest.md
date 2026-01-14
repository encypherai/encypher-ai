# StreamMerkleFinalizeRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**SessionId** | **string** | Session ID to finalize | 
**EmbedManifest** | Pointer to **bool** | Whether to embed C2PA manifest into the final document | [optional] [default to true]
**ManifestMode** | Pointer to **string** | Manifest mode: full, lightweight_uuid, hybrid | [optional] [default to "full"]
**Action** | Pointer to **string** | C2PA action type: c2pa.created or c2pa.edited | [optional] [default to "c2pa.created"]

## Methods

### NewStreamMerkleFinalizeRequest

`func NewStreamMerkleFinalizeRequest(sessionId string, ) *StreamMerkleFinalizeRequest`

NewStreamMerkleFinalizeRequest instantiates a new StreamMerkleFinalizeRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewStreamMerkleFinalizeRequestWithDefaults

`func NewStreamMerkleFinalizeRequestWithDefaults() *StreamMerkleFinalizeRequest`

NewStreamMerkleFinalizeRequestWithDefaults instantiates a new StreamMerkleFinalizeRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetSessionId

`func (o *StreamMerkleFinalizeRequest) GetSessionId() string`

GetSessionId returns the SessionId field if non-nil, zero value otherwise.

### GetSessionIdOk

`func (o *StreamMerkleFinalizeRequest) GetSessionIdOk() (*string, bool)`

GetSessionIdOk returns a tuple with the SessionId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSessionId

`func (o *StreamMerkleFinalizeRequest) SetSessionId(v string)`

SetSessionId sets SessionId field to given value.


### GetEmbedManifest

`func (o *StreamMerkleFinalizeRequest) GetEmbedManifest() bool`

GetEmbedManifest returns the EmbedManifest field if non-nil, zero value otherwise.

### GetEmbedManifestOk

`func (o *StreamMerkleFinalizeRequest) GetEmbedManifestOk() (*bool, bool)`

GetEmbedManifestOk returns a tuple with the EmbedManifest field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEmbedManifest

`func (o *StreamMerkleFinalizeRequest) SetEmbedManifest(v bool)`

SetEmbedManifest sets EmbedManifest field to given value.

### HasEmbedManifest

`func (o *StreamMerkleFinalizeRequest) HasEmbedManifest() bool`

HasEmbedManifest returns a boolean if a field has been set.

### GetManifestMode

`func (o *StreamMerkleFinalizeRequest) GetManifestMode() string`

GetManifestMode returns the ManifestMode field if non-nil, zero value otherwise.

### GetManifestModeOk

`func (o *StreamMerkleFinalizeRequest) GetManifestModeOk() (*string, bool)`

GetManifestModeOk returns a tuple with the ManifestMode field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetManifestMode

`func (o *StreamMerkleFinalizeRequest) SetManifestMode(v string)`

SetManifestMode sets ManifestMode field to given value.

### HasManifestMode

`func (o *StreamMerkleFinalizeRequest) HasManifestMode() bool`

HasManifestMode returns a boolean if a field has been set.

### GetAction

`func (o *StreamMerkleFinalizeRequest) GetAction() string`

GetAction returns the Action field if non-nil, zero value otherwise.

### GetActionOk

`func (o *StreamMerkleFinalizeRequest) GetActionOk() (*string, bool)`

GetActionOk returns a tuple with the Action field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAction

`func (o *StreamMerkleFinalizeRequest) SetAction(v string)`

SetAction sets Action field to given value.

### HasAction

`func (o *StreamMerkleFinalizeRequest) HasAction() bool`

HasAction returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


