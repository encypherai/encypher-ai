# EncodeWithEmbeddingsRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DocumentId** | **string** | Unique document identifier | 
**Text** | **string** | Full document text to encode | 
**SegmentationLevel** | Pointer to **string** | Segmentation level: document (free tier, no segmentation), sentence, paragraph, section, word | [optional] [default to "sentence"]
**SegmentationLevels** | Pointer to **[]string** |  | [optional] 
**IndexForAttribution** | Pointer to **NullableBool** |  | [optional] 
**Action** | Pointer to **string** | C2PA action type: c2pa.created (new content) or c2pa.edited (modified content) | [optional] [default to "c2pa.created"]
**ManifestMode** | Pointer to **string** | Controls manifest detail level. Options: full, lightweight_uuid, hybrid. Availability depends on plan tier. | [optional] [default to "full"]
**EmbeddingStrategy** | Pointer to **string** | Controls embedding placement strategy. Options: single_point, distributed, distributed_redundant. Availability depends on plan tier. | [optional] [default to "single_point"]
**DistributionTarget** | Pointer to **NullableString** |  | [optional] 
**AddDualBinding** | Pointer to **bool** | Enable additional integrity binding. Availability depends on plan tier. | [optional] [default to false]
**DisableC2pa** | Pointer to **bool** | Opt-out of C2PA embedding. When true, only basic metadata is embedded. | [optional] [default to false]
**PreviousInstanceId** | Pointer to **NullableString** |  | [optional] 
**Metadata** | Pointer to **map[string]interface{}** |  | [optional] 
**C2paManifestUrl** | Pointer to **NullableString** |  | [optional] 
**C2paManifestHash** | Pointer to **NullableString** |  | [optional] 
**CustomAssertions** | Pointer to **[]map[string]interface{}** |  | [optional] 
**TemplateId** | Pointer to **NullableString** |  | [optional] 
**ValidateAssertions** | Pointer to **bool** | Whether to validate custom assertions against registered schemas | [optional] [default to true]
**DigitalSourceType** | Pointer to **NullableString** |  | [optional] 
**License** | Pointer to [**NullableLicenseInfo**](LicenseInfo.md) |  | [optional] 
**Rights** | Pointer to [**NullableAppSchemasEmbeddingsRightsMetadata**](AppSchemasEmbeddingsRightsMetadata.md) |  | [optional] 
**EmbeddingOptions** | Pointer to [**EmbeddingOptions**](EmbeddingOptions.md) | Embedding generation options | [optional] 
**ExpiresAt** | Pointer to **NullableTime** |  | [optional] 

## Methods

### NewEncodeWithEmbeddingsRequest

`func NewEncodeWithEmbeddingsRequest(documentId string, text string, ) *EncodeWithEmbeddingsRequest`

NewEncodeWithEmbeddingsRequest instantiates a new EncodeWithEmbeddingsRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewEncodeWithEmbeddingsRequestWithDefaults

`func NewEncodeWithEmbeddingsRequestWithDefaults() *EncodeWithEmbeddingsRequest`

NewEncodeWithEmbeddingsRequestWithDefaults instantiates a new EncodeWithEmbeddingsRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDocumentId

`func (o *EncodeWithEmbeddingsRequest) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *EncodeWithEmbeddingsRequest) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *EncodeWithEmbeddingsRequest) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.


### GetText

`func (o *EncodeWithEmbeddingsRequest) GetText() string`

GetText returns the Text field if non-nil, zero value otherwise.

### GetTextOk

`func (o *EncodeWithEmbeddingsRequest) GetTextOk() (*string, bool)`

GetTextOk returns a tuple with the Text field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetText

`func (o *EncodeWithEmbeddingsRequest) SetText(v string)`

SetText sets Text field to given value.


### GetSegmentationLevel

`func (o *EncodeWithEmbeddingsRequest) GetSegmentationLevel() string`

GetSegmentationLevel returns the SegmentationLevel field if non-nil, zero value otherwise.

### GetSegmentationLevelOk

`func (o *EncodeWithEmbeddingsRequest) GetSegmentationLevelOk() (*string, bool)`

GetSegmentationLevelOk returns a tuple with the SegmentationLevel field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSegmentationLevel

`func (o *EncodeWithEmbeddingsRequest) SetSegmentationLevel(v string)`

SetSegmentationLevel sets SegmentationLevel field to given value.

### HasSegmentationLevel

`func (o *EncodeWithEmbeddingsRequest) HasSegmentationLevel() bool`

HasSegmentationLevel returns a boolean if a field has been set.

### GetSegmentationLevels

`func (o *EncodeWithEmbeddingsRequest) GetSegmentationLevels() []string`

GetSegmentationLevels returns the SegmentationLevels field if non-nil, zero value otherwise.

### GetSegmentationLevelsOk

`func (o *EncodeWithEmbeddingsRequest) GetSegmentationLevelsOk() (*[]string, bool)`

GetSegmentationLevelsOk returns a tuple with the SegmentationLevels field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSegmentationLevels

`func (o *EncodeWithEmbeddingsRequest) SetSegmentationLevels(v []string)`

SetSegmentationLevels sets SegmentationLevels field to given value.

### HasSegmentationLevels

`func (o *EncodeWithEmbeddingsRequest) HasSegmentationLevels() bool`

HasSegmentationLevels returns a boolean if a field has been set.

### SetSegmentationLevelsNil

`func (o *EncodeWithEmbeddingsRequest) SetSegmentationLevelsNil(b bool)`

 SetSegmentationLevelsNil sets the value for SegmentationLevels to be an explicit nil

### UnsetSegmentationLevels
`func (o *EncodeWithEmbeddingsRequest) UnsetSegmentationLevels()`

UnsetSegmentationLevels ensures that no value is present for SegmentationLevels, not even an explicit nil
### GetIndexForAttribution

`func (o *EncodeWithEmbeddingsRequest) GetIndexForAttribution() bool`

GetIndexForAttribution returns the IndexForAttribution field if non-nil, zero value otherwise.

### GetIndexForAttributionOk

`func (o *EncodeWithEmbeddingsRequest) GetIndexForAttributionOk() (*bool, bool)`

GetIndexForAttributionOk returns a tuple with the IndexForAttribution field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIndexForAttribution

`func (o *EncodeWithEmbeddingsRequest) SetIndexForAttribution(v bool)`

SetIndexForAttribution sets IndexForAttribution field to given value.

### HasIndexForAttribution

`func (o *EncodeWithEmbeddingsRequest) HasIndexForAttribution() bool`

HasIndexForAttribution returns a boolean if a field has been set.

### SetIndexForAttributionNil

`func (o *EncodeWithEmbeddingsRequest) SetIndexForAttributionNil(b bool)`

 SetIndexForAttributionNil sets the value for IndexForAttribution to be an explicit nil

### UnsetIndexForAttribution
`func (o *EncodeWithEmbeddingsRequest) UnsetIndexForAttribution()`

UnsetIndexForAttribution ensures that no value is present for IndexForAttribution, not even an explicit nil
### GetAction

`func (o *EncodeWithEmbeddingsRequest) GetAction() string`

GetAction returns the Action field if non-nil, zero value otherwise.

### GetActionOk

`func (o *EncodeWithEmbeddingsRequest) GetActionOk() (*string, bool)`

GetActionOk returns a tuple with the Action field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAction

`func (o *EncodeWithEmbeddingsRequest) SetAction(v string)`

SetAction sets Action field to given value.

### HasAction

`func (o *EncodeWithEmbeddingsRequest) HasAction() bool`

HasAction returns a boolean if a field has been set.

### GetManifestMode

`func (o *EncodeWithEmbeddingsRequest) GetManifestMode() string`

GetManifestMode returns the ManifestMode field if non-nil, zero value otherwise.

### GetManifestModeOk

`func (o *EncodeWithEmbeddingsRequest) GetManifestModeOk() (*string, bool)`

GetManifestModeOk returns a tuple with the ManifestMode field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetManifestMode

`func (o *EncodeWithEmbeddingsRequest) SetManifestMode(v string)`

SetManifestMode sets ManifestMode field to given value.

### HasManifestMode

`func (o *EncodeWithEmbeddingsRequest) HasManifestMode() bool`

HasManifestMode returns a boolean if a field has been set.

### GetEmbeddingStrategy

`func (o *EncodeWithEmbeddingsRequest) GetEmbeddingStrategy() string`

GetEmbeddingStrategy returns the EmbeddingStrategy field if non-nil, zero value otherwise.

### GetEmbeddingStrategyOk

`func (o *EncodeWithEmbeddingsRequest) GetEmbeddingStrategyOk() (*string, bool)`

GetEmbeddingStrategyOk returns a tuple with the EmbeddingStrategy field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEmbeddingStrategy

`func (o *EncodeWithEmbeddingsRequest) SetEmbeddingStrategy(v string)`

SetEmbeddingStrategy sets EmbeddingStrategy field to given value.

### HasEmbeddingStrategy

`func (o *EncodeWithEmbeddingsRequest) HasEmbeddingStrategy() bool`

HasEmbeddingStrategy returns a boolean if a field has been set.

### GetDistributionTarget

`func (o *EncodeWithEmbeddingsRequest) GetDistributionTarget() string`

GetDistributionTarget returns the DistributionTarget field if non-nil, zero value otherwise.

### GetDistributionTargetOk

`func (o *EncodeWithEmbeddingsRequest) GetDistributionTargetOk() (*string, bool)`

GetDistributionTargetOk returns a tuple with the DistributionTarget field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDistributionTarget

`func (o *EncodeWithEmbeddingsRequest) SetDistributionTarget(v string)`

SetDistributionTarget sets DistributionTarget field to given value.

### HasDistributionTarget

`func (o *EncodeWithEmbeddingsRequest) HasDistributionTarget() bool`

HasDistributionTarget returns a boolean if a field has been set.

### SetDistributionTargetNil

`func (o *EncodeWithEmbeddingsRequest) SetDistributionTargetNil(b bool)`

 SetDistributionTargetNil sets the value for DistributionTarget to be an explicit nil

### UnsetDistributionTarget
`func (o *EncodeWithEmbeddingsRequest) UnsetDistributionTarget()`

UnsetDistributionTarget ensures that no value is present for DistributionTarget, not even an explicit nil
### GetAddDualBinding

`func (o *EncodeWithEmbeddingsRequest) GetAddDualBinding() bool`

GetAddDualBinding returns the AddDualBinding field if non-nil, zero value otherwise.

### GetAddDualBindingOk

`func (o *EncodeWithEmbeddingsRequest) GetAddDualBindingOk() (*bool, bool)`

GetAddDualBindingOk returns a tuple with the AddDualBinding field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAddDualBinding

`func (o *EncodeWithEmbeddingsRequest) SetAddDualBinding(v bool)`

SetAddDualBinding sets AddDualBinding field to given value.

### HasAddDualBinding

`func (o *EncodeWithEmbeddingsRequest) HasAddDualBinding() bool`

HasAddDualBinding returns a boolean if a field has been set.

### GetDisableC2pa

`func (o *EncodeWithEmbeddingsRequest) GetDisableC2pa() bool`

GetDisableC2pa returns the DisableC2pa field if non-nil, zero value otherwise.

### GetDisableC2paOk

`func (o *EncodeWithEmbeddingsRequest) GetDisableC2paOk() (*bool, bool)`

GetDisableC2paOk returns a tuple with the DisableC2pa field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDisableC2pa

`func (o *EncodeWithEmbeddingsRequest) SetDisableC2pa(v bool)`

SetDisableC2pa sets DisableC2pa field to given value.

### HasDisableC2pa

`func (o *EncodeWithEmbeddingsRequest) HasDisableC2pa() bool`

HasDisableC2pa returns a boolean if a field has been set.

### GetPreviousInstanceId

`func (o *EncodeWithEmbeddingsRequest) GetPreviousInstanceId() string`

GetPreviousInstanceId returns the PreviousInstanceId field if non-nil, zero value otherwise.

### GetPreviousInstanceIdOk

`func (o *EncodeWithEmbeddingsRequest) GetPreviousInstanceIdOk() (*string, bool)`

GetPreviousInstanceIdOk returns a tuple with the PreviousInstanceId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPreviousInstanceId

`func (o *EncodeWithEmbeddingsRequest) SetPreviousInstanceId(v string)`

SetPreviousInstanceId sets PreviousInstanceId field to given value.

### HasPreviousInstanceId

`func (o *EncodeWithEmbeddingsRequest) HasPreviousInstanceId() bool`

HasPreviousInstanceId returns a boolean if a field has been set.

### SetPreviousInstanceIdNil

`func (o *EncodeWithEmbeddingsRequest) SetPreviousInstanceIdNil(b bool)`

 SetPreviousInstanceIdNil sets the value for PreviousInstanceId to be an explicit nil

### UnsetPreviousInstanceId
`func (o *EncodeWithEmbeddingsRequest) UnsetPreviousInstanceId()`

UnsetPreviousInstanceId ensures that no value is present for PreviousInstanceId, not even an explicit nil
### GetMetadata

`func (o *EncodeWithEmbeddingsRequest) GetMetadata() map[string]interface{}`

GetMetadata returns the Metadata field if non-nil, zero value otherwise.

### GetMetadataOk

`func (o *EncodeWithEmbeddingsRequest) GetMetadataOk() (*map[string]interface{}, bool)`

GetMetadataOk returns a tuple with the Metadata field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMetadata

`func (o *EncodeWithEmbeddingsRequest) SetMetadata(v map[string]interface{})`

SetMetadata sets Metadata field to given value.

### HasMetadata

`func (o *EncodeWithEmbeddingsRequest) HasMetadata() bool`

HasMetadata returns a boolean if a field has been set.

### SetMetadataNil

`func (o *EncodeWithEmbeddingsRequest) SetMetadataNil(b bool)`

 SetMetadataNil sets the value for Metadata to be an explicit nil

### UnsetMetadata
`func (o *EncodeWithEmbeddingsRequest) UnsetMetadata()`

UnsetMetadata ensures that no value is present for Metadata, not even an explicit nil
### GetC2paManifestUrl

`func (o *EncodeWithEmbeddingsRequest) GetC2paManifestUrl() string`

GetC2paManifestUrl returns the C2paManifestUrl field if non-nil, zero value otherwise.

### GetC2paManifestUrlOk

`func (o *EncodeWithEmbeddingsRequest) GetC2paManifestUrlOk() (*string, bool)`

GetC2paManifestUrlOk returns a tuple with the C2paManifestUrl field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetC2paManifestUrl

`func (o *EncodeWithEmbeddingsRequest) SetC2paManifestUrl(v string)`

SetC2paManifestUrl sets C2paManifestUrl field to given value.

### HasC2paManifestUrl

`func (o *EncodeWithEmbeddingsRequest) HasC2paManifestUrl() bool`

HasC2paManifestUrl returns a boolean if a field has been set.

### SetC2paManifestUrlNil

`func (o *EncodeWithEmbeddingsRequest) SetC2paManifestUrlNil(b bool)`

 SetC2paManifestUrlNil sets the value for C2paManifestUrl to be an explicit nil

### UnsetC2paManifestUrl
`func (o *EncodeWithEmbeddingsRequest) UnsetC2paManifestUrl()`

UnsetC2paManifestUrl ensures that no value is present for C2paManifestUrl, not even an explicit nil
### GetC2paManifestHash

`func (o *EncodeWithEmbeddingsRequest) GetC2paManifestHash() string`

GetC2paManifestHash returns the C2paManifestHash field if non-nil, zero value otherwise.

### GetC2paManifestHashOk

`func (o *EncodeWithEmbeddingsRequest) GetC2paManifestHashOk() (*string, bool)`

GetC2paManifestHashOk returns a tuple with the C2paManifestHash field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetC2paManifestHash

`func (o *EncodeWithEmbeddingsRequest) SetC2paManifestHash(v string)`

SetC2paManifestHash sets C2paManifestHash field to given value.

### HasC2paManifestHash

`func (o *EncodeWithEmbeddingsRequest) HasC2paManifestHash() bool`

HasC2paManifestHash returns a boolean if a field has been set.

### SetC2paManifestHashNil

`func (o *EncodeWithEmbeddingsRequest) SetC2paManifestHashNil(b bool)`

 SetC2paManifestHashNil sets the value for C2paManifestHash to be an explicit nil

### UnsetC2paManifestHash
`func (o *EncodeWithEmbeddingsRequest) UnsetC2paManifestHash()`

UnsetC2paManifestHash ensures that no value is present for C2paManifestHash, not even an explicit nil
### GetCustomAssertions

`func (o *EncodeWithEmbeddingsRequest) GetCustomAssertions() []map[string]interface{}`

GetCustomAssertions returns the CustomAssertions field if non-nil, zero value otherwise.

### GetCustomAssertionsOk

`func (o *EncodeWithEmbeddingsRequest) GetCustomAssertionsOk() (*[]map[string]interface{}, bool)`

GetCustomAssertionsOk returns a tuple with the CustomAssertions field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCustomAssertions

`func (o *EncodeWithEmbeddingsRequest) SetCustomAssertions(v []map[string]interface{})`

SetCustomAssertions sets CustomAssertions field to given value.

### HasCustomAssertions

`func (o *EncodeWithEmbeddingsRequest) HasCustomAssertions() bool`

HasCustomAssertions returns a boolean if a field has been set.

### SetCustomAssertionsNil

`func (o *EncodeWithEmbeddingsRequest) SetCustomAssertionsNil(b bool)`

 SetCustomAssertionsNil sets the value for CustomAssertions to be an explicit nil

### UnsetCustomAssertions
`func (o *EncodeWithEmbeddingsRequest) UnsetCustomAssertions()`

UnsetCustomAssertions ensures that no value is present for CustomAssertions, not even an explicit nil
### GetTemplateId

`func (o *EncodeWithEmbeddingsRequest) GetTemplateId() string`

GetTemplateId returns the TemplateId field if non-nil, zero value otherwise.

### GetTemplateIdOk

`func (o *EncodeWithEmbeddingsRequest) GetTemplateIdOk() (*string, bool)`

GetTemplateIdOk returns a tuple with the TemplateId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTemplateId

`func (o *EncodeWithEmbeddingsRequest) SetTemplateId(v string)`

SetTemplateId sets TemplateId field to given value.

### HasTemplateId

`func (o *EncodeWithEmbeddingsRequest) HasTemplateId() bool`

HasTemplateId returns a boolean if a field has been set.

### SetTemplateIdNil

`func (o *EncodeWithEmbeddingsRequest) SetTemplateIdNil(b bool)`

 SetTemplateIdNil sets the value for TemplateId to be an explicit nil

### UnsetTemplateId
`func (o *EncodeWithEmbeddingsRequest) UnsetTemplateId()`

UnsetTemplateId ensures that no value is present for TemplateId, not even an explicit nil
### GetValidateAssertions

`func (o *EncodeWithEmbeddingsRequest) GetValidateAssertions() bool`

GetValidateAssertions returns the ValidateAssertions field if non-nil, zero value otherwise.

### GetValidateAssertionsOk

`func (o *EncodeWithEmbeddingsRequest) GetValidateAssertionsOk() (*bool, bool)`

GetValidateAssertionsOk returns a tuple with the ValidateAssertions field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetValidateAssertions

`func (o *EncodeWithEmbeddingsRequest) SetValidateAssertions(v bool)`

SetValidateAssertions sets ValidateAssertions field to given value.

### HasValidateAssertions

`func (o *EncodeWithEmbeddingsRequest) HasValidateAssertions() bool`

HasValidateAssertions returns a boolean if a field has been set.

### GetDigitalSourceType

`func (o *EncodeWithEmbeddingsRequest) GetDigitalSourceType() string`

GetDigitalSourceType returns the DigitalSourceType field if non-nil, zero value otherwise.

### GetDigitalSourceTypeOk

`func (o *EncodeWithEmbeddingsRequest) GetDigitalSourceTypeOk() (*string, bool)`

GetDigitalSourceTypeOk returns a tuple with the DigitalSourceType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDigitalSourceType

`func (o *EncodeWithEmbeddingsRequest) SetDigitalSourceType(v string)`

SetDigitalSourceType sets DigitalSourceType field to given value.

### HasDigitalSourceType

`func (o *EncodeWithEmbeddingsRequest) HasDigitalSourceType() bool`

HasDigitalSourceType returns a boolean if a field has been set.

### SetDigitalSourceTypeNil

`func (o *EncodeWithEmbeddingsRequest) SetDigitalSourceTypeNil(b bool)`

 SetDigitalSourceTypeNil sets the value for DigitalSourceType to be an explicit nil

### UnsetDigitalSourceType
`func (o *EncodeWithEmbeddingsRequest) UnsetDigitalSourceType()`

UnsetDigitalSourceType ensures that no value is present for DigitalSourceType, not even an explicit nil
### GetLicense

`func (o *EncodeWithEmbeddingsRequest) GetLicense() LicenseInfo`

GetLicense returns the License field if non-nil, zero value otherwise.

### GetLicenseOk

`func (o *EncodeWithEmbeddingsRequest) GetLicenseOk() (*LicenseInfo, bool)`

GetLicenseOk returns a tuple with the License field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLicense

`func (o *EncodeWithEmbeddingsRequest) SetLicense(v LicenseInfo)`

SetLicense sets License field to given value.

### HasLicense

`func (o *EncodeWithEmbeddingsRequest) HasLicense() bool`

HasLicense returns a boolean if a field has been set.

### SetLicenseNil

`func (o *EncodeWithEmbeddingsRequest) SetLicenseNil(b bool)`

 SetLicenseNil sets the value for License to be an explicit nil

### UnsetLicense
`func (o *EncodeWithEmbeddingsRequest) UnsetLicense()`

UnsetLicense ensures that no value is present for License, not even an explicit nil
### GetRights

`func (o *EncodeWithEmbeddingsRequest) GetRights() AppSchemasEmbeddingsRightsMetadata`

GetRights returns the Rights field if non-nil, zero value otherwise.

### GetRightsOk

`func (o *EncodeWithEmbeddingsRequest) GetRightsOk() (*AppSchemasEmbeddingsRightsMetadata, bool)`

GetRightsOk returns a tuple with the Rights field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRights

`func (o *EncodeWithEmbeddingsRequest) SetRights(v AppSchemasEmbeddingsRightsMetadata)`

SetRights sets Rights field to given value.

### HasRights

`func (o *EncodeWithEmbeddingsRequest) HasRights() bool`

HasRights returns a boolean if a field has been set.

### SetRightsNil

`func (o *EncodeWithEmbeddingsRequest) SetRightsNil(b bool)`

 SetRightsNil sets the value for Rights to be an explicit nil

### UnsetRights
`func (o *EncodeWithEmbeddingsRequest) UnsetRights()`

UnsetRights ensures that no value is present for Rights, not even an explicit nil
### GetEmbeddingOptions

`func (o *EncodeWithEmbeddingsRequest) GetEmbeddingOptions() EmbeddingOptions`

GetEmbeddingOptions returns the EmbeddingOptions field if non-nil, zero value otherwise.

### GetEmbeddingOptionsOk

`func (o *EncodeWithEmbeddingsRequest) GetEmbeddingOptionsOk() (*EmbeddingOptions, bool)`

GetEmbeddingOptionsOk returns a tuple with the EmbeddingOptions field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEmbeddingOptions

`func (o *EncodeWithEmbeddingsRequest) SetEmbeddingOptions(v EmbeddingOptions)`

SetEmbeddingOptions sets EmbeddingOptions field to given value.

### HasEmbeddingOptions

`func (o *EncodeWithEmbeddingsRequest) HasEmbeddingOptions() bool`

HasEmbeddingOptions returns a boolean if a field has been set.

### GetExpiresAt

`func (o *EncodeWithEmbeddingsRequest) GetExpiresAt() time.Time`

GetExpiresAt returns the ExpiresAt field if non-nil, zero value otherwise.

### GetExpiresAtOk

`func (o *EncodeWithEmbeddingsRequest) GetExpiresAtOk() (*time.Time, bool)`

GetExpiresAtOk returns a tuple with the ExpiresAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetExpiresAt

`func (o *EncodeWithEmbeddingsRequest) SetExpiresAt(v time.Time)`

SetExpiresAt sets ExpiresAt field to given value.

### HasExpiresAt

`func (o *EncodeWithEmbeddingsRequest) HasExpiresAt() bool`

HasExpiresAt returns a boolean if a field has been set.

### SetExpiresAtNil

`func (o *EncodeWithEmbeddingsRequest) SetExpiresAtNil(b bool)`

 SetExpiresAtNil sets the value for ExpiresAt to be an explicit nil

### UnsetExpiresAt
`func (o *EncodeWithEmbeddingsRequest) UnsetExpiresAt()`

UnsetExpiresAt ensures that no value is present for ExpiresAt, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


