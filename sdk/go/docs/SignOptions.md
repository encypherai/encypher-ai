# SignOptions

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**DocumentType** | Pointer to **string** | Document type: article, legal_brief, contract, ai_output | [optional] [default to "article"]
**ClaimGenerator** | Pointer to **NullableString** |  | [optional] 
**Action** | Pointer to **string** | C2PA action type: c2pa.created (new) or c2pa.edited (modified) | [optional] [default to "c2pa.created"]
**PreviousInstanceId** | Pointer to **NullableString** |  | [optional] 
**DigitalSourceType** | Pointer to **NullableString** |  | [optional] 
**SegmentationLevel** | Pointer to **string** | Segmentation level: document (free), sentence, paragraph, section (Professional+), word (Enterprise) | [optional] [default to "document"]
**SegmentationLevels** | Pointer to **[]string** |  | [optional] 
**ManifestMode** | Pointer to **string** | Manifest mode: full (free), lightweight_uuid, minimal_uuid, hybrid, zw_embedding (Professional+) | [optional] [default to "full"]
**EmbeddingStrategy** | Pointer to **string** | Embedding strategy: single_point (free), distributed, distributed_redundant (Professional+) | [optional] [default to "single_point"]
**DistributionTarget** | Pointer to **NullableString** |  | [optional] 
**IndexForAttribution** | Pointer to **bool** | Index content for attribution/plagiarism detection (Professional+) | [optional] [default to false]
**CustomAssertions** | Pointer to **[]map[string]interface{}** |  | [optional] 
**TemplateId** | Pointer to **NullableString** |  | [optional] 
**ValidateAssertions** | Pointer to **bool** | Whether to validate custom assertions against registered schemas (Business+) | [optional] [default to true]
**Rights** | Pointer to [**NullableRightsMetadata**](RightsMetadata.md) |  | [optional] 
**License** | Pointer to [**NullableLicenseInfo**](LicenseInfo.md) |  | [optional] 
**Actions** | Pointer to **[]map[string]interface{}** |  | [optional] 
**AddDualBinding** | Pointer to **bool** | Enable additional integrity binding (Enterprise) | [optional] [default to false]
**IncludeFingerprint** | Pointer to **bool** | Include robust fingerprint that survives modifications (Enterprise) | [optional] [default to false]
**DisableC2pa** | Pointer to **bool** | Opt-out of C2PA embedding, only basic metadata (Enterprise) | [optional] [default to false]
**EmbeddingOptions** | Pointer to [**EmbeddingOptions**](EmbeddingOptions.md) | Embedding output format options | [optional] 
**ExpiresAt** | Pointer to **NullableTime** |  | [optional] 

## Methods

### NewSignOptions

`func NewSignOptions() *SignOptions`

NewSignOptions instantiates a new SignOptions object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewSignOptionsWithDefaults

`func NewSignOptionsWithDefaults() *SignOptions`

NewSignOptionsWithDefaults instantiates a new SignOptions object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetDocumentType

`func (o *SignOptions) GetDocumentType() string`

GetDocumentType returns the DocumentType field if non-nil, zero value otherwise.

### GetDocumentTypeOk

`func (o *SignOptions) GetDocumentTypeOk() (*string, bool)`

GetDocumentTypeOk returns a tuple with the DocumentType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentType

`func (o *SignOptions) SetDocumentType(v string)`

SetDocumentType sets DocumentType field to given value.

### HasDocumentType

`func (o *SignOptions) HasDocumentType() bool`

HasDocumentType returns a boolean if a field has been set.

### GetClaimGenerator

`func (o *SignOptions) GetClaimGenerator() string`

GetClaimGenerator returns the ClaimGenerator field if non-nil, zero value otherwise.

### GetClaimGeneratorOk

`func (o *SignOptions) GetClaimGeneratorOk() (*string, bool)`

GetClaimGeneratorOk returns a tuple with the ClaimGenerator field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetClaimGenerator

`func (o *SignOptions) SetClaimGenerator(v string)`

SetClaimGenerator sets ClaimGenerator field to given value.

### HasClaimGenerator

`func (o *SignOptions) HasClaimGenerator() bool`

HasClaimGenerator returns a boolean if a field has been set.

### SetClaimGeneratorNil

`func (o *SignOptions) SetClaimGeneratorNil(b bool)`

 SetClaimGeneratorNil sets the value for ClaimGenerator to be an explicit nil

### UnsetClaimGenerator
`func (o *SignOptions) UnsetClaimGenerator()`

UnsetClaimGenerator ensures that no value is present for ClaimGenerator, not even an explicit nil
### GetAction

`func (o *SignOptions) GetAction() string`

GetAction returns the Action field if non-nil, zero value otherwise.

### GetActionOk

`func (o *SignOptions) GetActionOk() (*string, bool)`

GetActionOk returns a tuple with the Action field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAction

`func (o *SignOptions) SetAction(v string)`

SetAction sets Action field to given value.

### HasAction

`func (o *SignOptions) HasAction() bool`

HasAction returns a boolean if a field has been set.

### GetPreviousInstanceId

`func (o *SignOptions) GetPreviousInstanceId() string`

GetPreviousInstanceId returns the PreviousInstanceId field if non-nil, zero value otherwise.

### GetPreviousInstanceIdOk

`func (o *SignOptions) GetPreviousInstanceIdOk() (*string, bool)`

GetPreviousInstanceIdOk returns a tuple with the PreviousInstanceId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetPreviousInstanceId

`func (o *SignOptions) SetPreviousInstanceId(v string)`

SetPreviousInstanceId sets PreviousInstanceId field to given value.

### HasPreviousInstanceId

`func (o *SignOptions) HasPreviousInstanceId() bool`

HasPreviousInstanceId returns a boolean if a field has been set.

### SetPreviousInstanceIdNil

`func (o *SignOptions) SetPreviousInstanceIdNil(b bool)`

 SetPreviousInstanceIdNil sets the value for PreviousInstanceId to be an explicit nil

### UnsetPreviousInstanceId
`func (o *SignOptions) UnsetPreviousInstanceId()`

UnsetPreviousInstanceId ensures that no value is present for PreviousInstanceId, not even an explicit nil
### GetDigitalSourceType

`func (o *SignOptions) GetDigitalSourceType() string`

GetDigitalSourceType returns the DigitalSourceType field if non-nil, zero value otherwise.

### GetDigitalSourceTypeOk

`func (o *SignOptions) GetDigitalSourceTypeOk() (*string, bool)`

GetDigitalSourceTypeOk returns a tuple with the DigitalSourceType field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDigitalSourceType

`func (o *SignOptions) SetDigitalSourceType(v string)`

SetDigitalSourceType sets DigitalSourceType field to given value.

### HasDigitalSourceType

`func (o *SignOptions) HasDigitalSourceType() bool`

HasDigitalSourceType returns a boolean if a field has been set.

### SetDigitalSourceTypeNil

`func (o *SignOptions) SetDigitalSourceTypeNil(b bool)`

 SetDigitalSourceTypeNil sets the value for DigitalSourceType to be an explicit nil

### UnsetDigitalSourceType
`func (o *SignOptions) UnsetDigitalSourceType()`

UnsetDigitalSourceType ensures that no value is present for DigitalSourceType, not even an explicit nil
### GetSegmentationLevel

`func (o *SignOptions) GetSegmentationLevel() string`

GetSegmentationLevel returns the SegmentationLevel field if non-nil, zero value otherwise.

### GetSegmentationLevelOk

`func (o *SignOptions) GetSegmentationLevelOk() (*string, bool)`

GetSegmentationLevelOk returns a tuple with the SegmentationLevel field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSegmentationLevel

`func (o *SignOptions) SetSegmentationLevel(v string)`

SetSegmentationLevel sets SegmentationLevel field to given value.

### HasSegmentationLevel

`func (o *SignOptions) HasSegmentationLevel() bool`

HasSegmentationLevel returns a boolean if a field has been set.

### GetSegmentationLevels

`func (o *SignOptions) GetSegmentationLevels() []string`

GetSegmentationLevels returns the SegmentationLevels field if non-nil, zero value otherwise.

### GetSegmentationLevelsOk

`func (o *SignOptions) GetSegmentationLevelsOk() (*[]string, bool)`

GetSegmentationLevelsOk returns a tuple with the SegmentationLevels field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSegmentationLevels

`func (o *SignOptions) SetSegmentationLevels(v []string)`

SetSegmentationLevels sets SegmentationLevels field to given value.

### HasSegmentationLevels

`func (o *SignOptions) HasSegmentationLevels() bool`

HasSegmentationLevels returns a boolean if a field has been set.

### SetSegmentationLevelsNil

`func (o *SignOptions) SetSegmentationLevelsNil(b bool)`

 SetSegmentationLevelsNil sets the value for SegmentationLevels to be an explicit nil

### UnsetSegmentationLevels
`func (o *SignOptions) UnsetSegmentationLevels()`

UnsetSegmentationLevels ensures that no value is present for SegmentationLevels, not even an explicit nil
### GetManifestMode

`func (o *SignOptions) GetManifestMode() string`

GetManifestMode returns the ManifestMode field if non-nil, zero value otherwise.

### GetManifestModeOk

`func (o *SignOptions) GetManifestModeOk() (*string, bool)`

GetManifestModeOk returns a tuple with the ManifestMode field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetManifestMode

`func (o *SignOptions) SetManifestMode(v string)`

SetManifestMode sets ManifestMode field to given value.

### HasManifestMode

`func (o *SignOptions) HasManifestMode() bool`

HasManifestMode returns a boolean if a field has been set.

### GetEmbeddingStrategy

`func (o *SignOptions) GetEmbeddingStrategy() string`

GetEmbeddingStrategy returns the EmbeddingStrategy field if non-nil, zero value otherwise.

### GetEmbeddingStrategyOk

`func (o *SignOptions) GetEmbeddingStrategyOk() (*string, bool)`

GetEmbeddingStrategyOk returns a tuple with the EmbeddingStrategy field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEmbeddingStrategy

`func (o *SignOptions) SetEmbeddingStrategy(v string)`

SetEmbeddingStrategy sets EmbeddingStrategy field to given value.

### HasEmbeddingStrategy

`func (o *SignOptions) HasEmbeddingStrategy() bool`

HasEmbeddingStrategy returns a boolean if a field has been set.

### GetDistributionTarget

`func (o *SignOptions) GetDistributionTarget() string`

GetDistributionTarget returns the DistributionTarget field if non-nil, zero value otherwise.

### GetDistributionTargetOk

`func (o *SignOptions) GetDistributionTargetOk() (*string, bool)`

GetDistributionTargetOk returns a tuple with the DistributionTarget field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDistributionTarget

`func (o *SignOptions) SetDistributionTarget(v string)`

SetDistributionTarget sets DistributionTarget field to given value.

### HasDistributionTarget

`func (o *SignOptions) HasDistributionTarget() bool`

HasDistributionTarget returns a boolean if a field has been set.

### SetDistributionTargetNil

`func (o *SignOptions) SetDistributionTargetNil(b bool)`

 SetDistributionTargetNil sets the value for DistributionTarget to be an explicit nil

### UnsetDistributionTarget
`func (o *SignOptions) UnsetDistributionTarget()`

UnsetDistributionTarget ensures that no value is present for DistributionTarget, not even an explicit nil
### GetIndexForAttribution

`func (o *SignOptions) GetIndexForAttribution() bool`

GetIndexForAttribution returns the IndexForAttribution field if non-nil, zero value otherwise.

### GetIndexForAttributionOk

`func (o *SignOptions) GetIndexForAttributionOk() (*bool, bool)`

GetIndexForAttributionOk returns a tuple with the IndexForAttribution field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIndexForAttribution

`func (o *SignOptions) SetIndexForAttribution(v bool)`

SetIndexForAttribution sets IndexForAttribution field to given value.

### HasIndexForAttribution

`func (o *SignOptions) HasIndexForAttribution() bool`

HasIndexForAttribution returns a boolean if a field has been set.

### GetCustomAssertions

`func (o *SignOptions) GetCustomAssertions() []map[string]interface{}`

GetCustomAssertions returns the CustomAssertions field if non-nil, zero value otherwise.

### GetCustomAssertionsOk

`func (o *SignOptions) GetCustomAssertionsOk() (*[]map[string]interface{}, bool)`

GetCustomAssertionsOk returns a tuple with the CustomAssertions field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetCustomAssertions

`func (o *SignOptions) SetCustomAssertions(v []map[string]interface{})`

SetCustomAssertions sets CustomAssertions field to given value.

### HasCustomAssertions

`func (o *SignOptions) HasCustomAssertions() bool`

HasCustomAssertions returns a boolean if a field has been set.

### SetCustomAssertionsNil

`func (o *SignOptions) SetCustomAssertionsNil(b bool)`

 SetCustomAssertionsNil sets the value for CustomAssertions to be an explicit nil

### UnsetCustomAssertions
`func (o *SignOptions) UnsetCustomAssertions()`

UnsetCustomAssertions ensures that no value is present for CustomAssertions, not even an explicit nil
### GetTemplateId

`func (o *SignOptions) GetTemplateId() string`

GetTemplateId returns the TemplateId field if non-nil, zero value otherwise.

### GetTemplateIdOk

`func (o *SignOptions) GetTemplateIdOk() (*string, bool)`

GetTemplateIdOk returns a tuple with the TemplateId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTemplateId

`func (o *SignOptions) SetTemplateId(v string)`

SetTemplateId sets TemplateId field to given value.

### HasTemplateId

`func (o *SignOptions) HasTemplateId() bool`

HasTemplateId returns a boolean if a field has been set.

### SetTemplateIdNil

`func (o *SignOptions) SetTemplateIdNil(b bool)`

 SetTemplateIdNil sets the value for TemplateId to be an explicit nil

### UnsetTemplateId
`func (o *SignOptions) UnsetTemplateId()`

UnsetTemplateId ensures that no value is present for TemplateId, not even an explicit nil
### GetValidateAssertions

`func (o *SignOptions) GetValidateAssertions() bool`

GetValidateAssertions returns the ValidateAssertions field if non-nil, zero value otherwise.

### GetValidateAssertionsOk

`func (o *SignOptions) GetValidateAssertionsOk() (*bool, bool)`

GetValidateAssertionsOk returns a tuple with the ValidateAssertions field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetValidateAssertions

`func (o *SignOptions) SetValidateAssertions(v bool)`

SetValidateAssertions sets ValidateAssertions field to given value.

### HasValidateAssertions

`func (o *SignOptions) HasValidateAssertions() bool`

HasValidateAssertions returns a boolean if a field has been set.

### GetRights

`func (o *SignOptions) GetRights() RightsMetadata`

GetRights returns the Rights field if non-nil, zero value otherwise.

### GetRightsOk

`func (o *SignOptions) GetRightsOk() (*RightsMetadata, bool)`

GetRightsOk returns a tuple with the Rights field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetRights

`func (o *SignOptions) SetRights(v RightsMetadata)`

SetRights sets Rights field to given value.

### HasRights

`func (o *SignOptions) HasRights() bool`

HasRights returns a boolean if a field has been set.

### SetRightsNil

`func (o *SignOptions) SetRightsNil(b bool)`

 SetRightsNil sets the value for Rights to be an explicit nil

### UnsetRights
`func (o *SignOptions) UnsetRights()`

UnsetRights ensures that no value is present for Rights, not even an explicit nil
### GetLicense

`func (o *SignOptions) GetLicense() LicenseInfo`

GetLicense returns the License field if non-nil, zero value otherwise.

### GetLicenseOk

`func (o *SignOptions) GetLicenseOk() (*LicenseInfo, bool)`

GetLicenseOk returns a tuple with the License field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLicense

`func (o *SignOptions) SetLicense(v LicenseInfo)`

SetLicense sets License field to given value.

### HasLicense

`func (o *SignOptions) HasLicense() bool`

HasLicense returns a boolean if a field has been set.

### SetLicenseNil

`func (o *SignOptions) SetLicenseNil(b bool)`

 SetLicenseNil sets the value for License to be an explicit nil

### UnsetLicense
`func (o *SignOptions) UnsetLicense()`

UnsetLicense ensures that no value is present for License, not even an explicit nil
### GetActions

`func (o *SignOptions) GetActions() []map[string]interface{}`

GetActions returns the Actions field if non-nil, zero value otherwise.

### GetActionsOk

`func (o *SignOptions) GetActionsOk() (*[]map[string]interface{}, bool)`

GetActionsOk returns a tuple with the Actions field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetActions

`func (o *SignOptions) SetActions(v []map[string]interface{})`

SetActions sets Actions field to given value.

### HasActions

`func (o *SignOptions) HasActions() bool`

HasActions returns a boolean if a field has been set.

### SetActionsNil

`func (o *SignOptions) SetActionsNil(b bool)`

 SetActionsNil sets the value for Actions to be an explicit nil

### UnsetActions
`func (o *SignOptions) UnsetActions()`

UnsetActions ensures that no value is present for Actions, not even an explicit nil
### GetAddDualBinding

`func (o *SignOptions) GetAddDualBinding() bool`

GetAddDualBinding returns the AddDualBinding field if non-nil, zero value otherwise.

### GetAddDualBindingOk

`func (o *SignOptions) GetAddDualBindingOk() (*bool, bool)`

GetAddDualBindingOk returns a tuple with the AddDualBinding field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetAddDualBinding

`func (o *SignOptions) SetAddDualBinding(v bool)`

SetAddDualBinding sets AddDualBinding field to given value.

### HasAddDualBinding

`func (o *SignOptions) HasAddDualBinding() bool`

HasAddDualBinding returns a boolean if a field has been set.

### GetIncludeFingerprint

`func (o *SignOptions) GetIncludeFingerprint() bool`

GetIncludeFingerprint returns the IncludeFingerprint field if non-nil, zero value otherwise.

### GetIncludeFingerprintOk

`func (o *SignOptions) GetIncludeFingerprintOk() (*bool, bool)`

GetIncludeFingerprintOk returns a tuple with the IncludeFingerprint field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIncludeFingerprint

`func (o *SignOptions) SetIncludeFingerprint(v bool)`

SetIncludeFingerprint sets IncludeFingerprint field to given value.

### HasIncludeFingerprint

`func (o *SignOptions) HasIncludeFingerprint() bool`

HasIncludeFingerprint returns a boolean if a field has been set.

### GetDisableC2pa

`func (o *SignOptions) GetDisableC2pa() bool`

GetDisableC2pa returns the DisableC2pa field if non-nil, zero value otherwise.

### GetDisableC2paOk

`func (o *SignOptions) GetDisableC2paOk() (*bool, bool)`

GetDisableC2paOk returns a tuple with the DisableC2pa field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDisableC2pa

`func (o *SignOptions) SetDisableC2pa(v bool)`

SetDisableC2pa sets DisableC2pa field to given value.

### HasDisableC2pa

`func (o *SignOptions) HasDisableC2pa() bool`

HasDisableC2pa returns a boolean if a field has been set.

### GetEmbeddingOptions

`func (o *SignOptions) GetEmbeddingOptions() EmbeddingOptions`

GetEmbeddingOptions returns the EmbeddingOptions field if non-nil, zero value otherwise.

### GetEmbeddingOptionsOk

`func (o *SignOptions) GetEmbeddingOptionsOk() (*EmbeddingOptions, bool)`

GetEmbeddingOptionsOk returns a tuple with the EmbeddingOptions field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetEmbeddingOptions

`func (o *SignOptions) SetEmbeddingOptions(v EmbeddingOptions)`

SetEmbeddingOptions sets EmbeddingOptions field to given value.

### HasEmbeddingOptions

`func (o *SignOptions) HasEmbeddingOptions() bool`

HasEmbeddingOptions returns a boolean if a field has been set.

### GetExpiresAt

`func (o *SignOptions) GetExpiresAt() time.Time`

GetExpiresAt returns the ExpiresAt field if non-nil, zero value otherwise.

### GetExpiresAtOk

`func (o *SignOptions) GetExpiresAtOk() (*time.Time, bool)`

GetExpiresAtOk returns a tuple with the ExpiresAt field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetExpiresAt

`func (o *SignOptions) SetExpiresAt(v time.Time)`

SetExpiresAt sets ExpiresAt field to given value.

### HasExpiresAt

`func (o *SignOptions) HasExpiresAt() bool`

HasExpiresAt returns a boolean if a field has been set.

### SetExpiresAtNil

`func (o *SignOptions) SetExpiresAtNil(b bool)`

 SetExpiresAtNil sets the value for ExpiresAt to be an explicit nil

### UnsetExpiresAt
`func (o *SignOptions) UnsetExpiresAt()`

UnsetExpiresAt ensures that no value is present for ExpiresAt, not even an explicit nil

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


