# VerificationServiceVerifyVerdict

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**Valid** | **bool** |  | 
**Tampered** | **bool** |  | 
**ReasonCode** | **string** |  | 
**SignerId** | Pointer to **NullableString** |  | [optional] 
**SignerName** | Pointer to **NullableString** |  | [optional] 
**OrganizationId** | Pointer to **NullableString** |  | [optional] 
**OrganizationName** | Pointer to **NullableString** |  | [optional] 
**Timestamp** | Pointer to **NullableTime** |  | [optional] 
**Document** | Pointer to [**NullableDocumentInfo**](DocumentInfo.md) |  | [optional] 
**C2pa** | Pointer to [**NullableC2PAInfo**](C2PAInfo.md) |  | [optional] 
**Licensing** | Pointer to [**NullableLicensingInfo**](LicensingInfo.md) |  | [optional] 
**MerkleProof** | Pointer to [**NullableMerkleProofInfo**](MerkleProofInfo.md) |  | [optional] 
**Details** | Pointer to **map[string]interface{}** |  | [optional] 

## Methods

### NewVerificationServiceVerifyVerdict

`func NewVerificationServiceVerifyVerdict(valid bool, tampered bool, reasonCode string, ) *VerificationServiceVerifyVerdict`

NewVerificationServiceVerifyVerdict instantiates a new VerificationServiceVerifyVerdict object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewVerificationServiceVerifyVerdictWithDefaults

`func NewVerificationServiceVerifyVerdictWithDefaults() *VerificationServiceVerifyVerdict`

NewVerificationServiceVerifyVerdictWithDefaults instantiates a new VerificationServiceVerifyVerdict object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetValid

`func (o *VerificationServiceVerifyVerdict) GetValid() bool`

GetValid returns the Valid field if non-nil, zero value otherwise.

### GetValidOk

`func (o *VerificationServiceVerifyVerdict) GetValidOk() (*bool, bool)`

GetValidOk returns a tuple with the Valid field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetValid

`func (o *VerificationServiceVerifyVerdict) SetValid(v bool)`

SetValid sets Valid field to given value.


### GetTampered

`func (o *VerificationServiceVerifyVerdict) GetTampered() bool`

GetTampered returns the Tampered field if non-nil, zero value otherwise.

### GetTamperedOk

`func (o *VerificationServiceVerifyVerdict) GetTamperedOk() (*bool, bool)`

GetTamperedOk returns a tuple with the Tampered field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTampered

`func (o *VerificationServiceVerifyVerdict) SetTampered(v bool)`

SetTampered sets Tampered field to given value.


### GetReasonCode

`func (o *VerificationServiceVerifyVerdict) GetReasonCode() string`

GetReasonCode returns the ReasonCode field if non-nil, zero value otherwise.

### GetReasonCodeOk

`func (o *VerificationServiceVerifyVerdict) GetReasonCodeOk() (*string, bool)`

GetReasonCodeOk returns a tuple with the ReasonCode field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetReasonCode

`func (o *VerificationServiceVerifyVerdict) SetReasonCode(v string)`

SetReasonCode sets ReasonCode field to given value.


### GetSignerId

`func (o *VerificationServiceVerifyVerdict) GetSignerId() string`

GetSignerId returns the SignerId field if non-nil, zero value otherwise.

### GetSignerIdOk

`func (o *VerificationServiceVerifyVerdict) GetSignerIdOk() (*string, bool)`

GetSignerIdOk returns a tuple with the SignerId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignerId

`func (o *VerificationServiceVerifyVerdict) SetSignerId(v string)`

SetSignerId sets SignerId field to given value.

### HasSignerId

`func (o *VerificationServiceVerifyVerdict) HasSignerId() bool`

HasSignerId returns a boolean if a field has been set.

### SetSignerIdNil

`func (o *VerificationServiceVerifyVerdict) SetSignerIdNil(b bool)`

 SetSignerIdNil sets the value for SignerId to be an explicit nil

### UnsetSignerId
`func (o *VerificationServiceVerifyVerdict) UnsetSignerId()`

UnsetSignerId ensures that no value is present for SignerId, not even an explicit nil
### GetSignerName

`func (o *VerificationServiceVerifyVerdict) GetSignerName() string`

GetSignerName returns the SignerName field if non-nil, zero value otherwise.

### GetSignerNameOk

`func (o *VerificationServiceVerifyVerdict) GetSignerNameOk() (*string, bool)`

GetSignerNameOk returns a tuple with the SignerName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetSignerName

`func (o *VerificationServiceVerifyVerdict) SetSignerName(v string)`

SetSignerName sets SignerName field to given value.

### HasSignerName

`func (o *VerificationServiceVerifyVerdict) HasSignerName() bool`

HasSignerName returns a boolean if a field has been set.

### SetSignerNameNil

`func (o *VerificationServiceVerifyVerdict) SetSignerNameNil(b bool)`

 SetSignerNameNil sets the value for SignerName to be an explicit nil

### UnsetSignerName
`func (o *VerificationServiceVerifyVerdict) UnsetSignerName()`

UnsetSignerName ensures that no value is present for SignerName, not even an explicit nil
### GetOrganizationId

`func (o *VerificationServiceVerifyVerdict) GetOrganizationId() string`

GetOrganizationId returns the OrganizationId field if non-nil, zero value otherwise.

### GetOrganizationIdOk

`func (o *VerificationServiceVerifyVerdict) GetOrganizationIdOk() (*string, bool)`

GetOrganizationIdOk returns a tuple with the OrganizationId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationId

`func (o *VerificationServiceVerifyVerdict) SetOrganizationId(v string)`

SetOrganizationId sets OrganizationId field to given value.

### HasOrganizationId

`func (o *VerificationServiceVerifyVerdict) HasOrganizationId() bool`

HasOrganizationId returns a boolean if a field has been set.

### SetOrganizationIdNil

`func (o *VerificationServiceVerifyVerdict) SetOrganizationIdNil(b bool)`

 SetOrganizationIdNil sets the value for OrganizationId to be an explicit nil

### UnsetOrganizationId
`func (o *VerificationServiceVerifyVerdict) UnsetOrganizationId()`

UnsetOrganizationId ensures that no value is present for OrganizationId, not even an explicit nil
### GetOrganizationName

`func (o *VerificationServiceVerifyVerdict) GetOrganizationName() string`

GetOrganizationName returns the OrganizationName field if non-nil, zero value otherwise.

### GetOrganizationNameOk

`func (o *VerificationServiceVerifyVerdict) GetOrganizationNameOk() (*string, bool)`

GetOrganizationNameOk returns a tuple with the OrganizationName field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetOrganizationName

`func (o *VerificationServiceVerifyVerdict) SetOrganizationName(v string)`

SetOrganizationName sets OrganizationName field to given value.

### HasOrganizationName

`func (o *VerificationServiceVerifyVerdict) HasOrganizationName() bool`

HasOrganizationName returns a boolean if a field has been set.

### SetOrganizationNameNil

`func (o *VerificationServiceVerifyVerdict) SetOrganizationNameNil(b bool)`

 SetOrganizationNameNil sets the value for OrganizationName to be an explicit nil

### UnsetOrganizationName
`func (o *VerificationServiceVerifyVerdict) UnsetOrganizationName()`

UnsetOrganizationName ensures that no value is present for OrganizationName, not even an explicit nil
### GetTimestamp

`func (o *VerificationServiceVerifyVerdict) GetTimestamp() time.Time`

GetTimestamp returns the Timestamp field if non-nil, zero value otherwise.

### GetTimestampOk

`func (o *VerificationServiceVerifyVerdict) GetTimestampOk() (*time.Time, bool)`

GetTimestampOk returns a tuple with the Timestamp field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTimestamp

`func (o *VerificationServiceVerifyVerdict) SetTimestamp(v time.Time)`

SetTimestamp sets Timestamp field to given value.

### HasTimestamp

`func (o *VerificationServiceVerifyVerdict) HasTimestamp() bool`

HasTimestamp returns a boolean if a field has been set.

### SetTimestampNil

`func (o *VerificationServiceVerifyVerdict) SetTimestampNil(b bool)`

 SetTimestampNil sets the value for Timestamp to be an explicit nil

### UnsetTimestamp
`func (o *VerificationServiceVerifyVerdict) UnsetTimestamp()`

UnsetTimestamp ensures that no value is present for Timestamp, not even an explicit nil
### GetDocument

`func (o *VerificationServiceVerifyVerdict) GetDocument() DocumentInfo`

GetDocument returns the Document field if non-nil, zero value otherwise.

### GetDocumentOk

`func (o *VerificationServiceVerifyVerdict) GetDocumentOk() (*DocumentInfo, bool)`

GetDocumentOk returns a tuple with the Document field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocument

`func (o *VerificationServiceVerifyVerdict) SetDocument(v DocumentInfo)`

SetDocument sets Document field to given value.

### HasDocument

`func (o *VerificationServiceVerifyVerdict) HasDocument() bool`

HasDocument returns a boolean if a field has been set.

### SetDocumentNil

`func (o *VerificationServiceVerifyVerdict) SetDocumentNil(b bool)`

 SetDocumentNil sets the value for Document to be an explicit nil

### UnsetDocument
`func (o *VerificationServiceVerifyVerdict) UnsetDocument()`

UnsetDocument ensures that no value is present for Document, not even an explicit nil
### GetC2pa

`func (o *VerificationServiceVerifyVerdict) GetC2pa() C2PAInfo`

GetC2pa returns the C2pa field if non-nil, zero value otherwise.

### GetC2paOk

`func (o *VerificationServiceVerifyVerdict) GetC2paOk() (*C2PAInfo, bool)`

GetC2paOk returns a tuple with the C2pa field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetC2pa

`func (o *VerificationServiceVerifyVerdict) SetC2pa(v C2PAInfo)`

SetC2pa sets C2pa field to given value.

### HasC2pa

`func (o *VerificationServiceVerifyVerdict) HasC2pa() bool`

HasC2pa returns a boolean if a field has been set.

### SetC2paNil

`func (o *VerificationServiceVerifyVerdict) SetC2paNil(b bool)`

 SetC2paNil sets the value for C2pa to be an explicit nil

### UnsetC2pa
`func (o *VerificationServiceVerifyVerdict) UnsetC2pa()`

UnsetC2pa ensures that no value is present for C2pa, not even an explicit nil
### GetLicensing

`func (o *VerificationServiceVerifyVerdict) GetLicensing() LicensingInfo`

GetLicensing returns the Licensing field if non-nil, zero value otherwise.

### GetLicensingOk

`func (o *VerificationServiceVerifyVerdict) GetLicensingOk() (*LicensingInfo, bool)`

GetLicensingOk returns a tuple with the Licensing field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetLicensing

`func (o *VerificationServiceVerifyVerdict) SetLicensing(v LicensingInfo)`

SetLicensing sets Licensing field to given value.

### HasLicensing

`func (o *VerificationServiceVerifyVerdict) HasLicensing() bool`

HasLicensing returns a boolean if a field has been set.

### SetLicensingNil

`func (o *VerificationServiceVerifyVerdict) SetLicensingNil(b bool)`

 SetLicensingNil sets the value for Licensing to be an explicit nil

### UnsetLicensing
`func (o *VerificationServiceVerifyVerdict) UnsetLicensing()`

UnsetLicensing ensures that no value is present for Licensing, not even an explicit nil
### GetMerkleProof

`func (o *VerificationServiceVerifyVerdict) GetMerkleProof() MerkleProofInfo`

GetMerkleProof returns the MerkleProof field if non-nil, zero value otherwise.

### GetMerkleProofOk

`func (o *VerificationServiceVerifyVerdict) GetMerkleProofOk() (*MerkleProofInfo, bool)`

GetMerkleProofOk returns a tuple with the MerkleProof field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetMerkleProof

`func (o *VerificationServiceVerifyVerdict) SetMerkleProof(v MerkleProofInfo)`

SetMerkleProof sets MerkleProof field to given value.

### HasMerkleProof

`func (o *VerificationServiceVerifyVerdict) HasMerkleProof() bool`

HasMerkleProof returns a boolean if a field has been set.

### SetMerkleProofNil

`func (o *VerificationServiceVerifyVerdict) SetMerkleProofNil(b bool)`

 SetMerkleProofNil sets the value for MerkleProof to be an explicit nil

### UnsetMerkleProof
`func (o *VerificationServiceVerifyVerdict) UnsetMerkleProof()`

UnsetMerkleProof ensures that no value is present for MerkleProof, not even an explicit nil
### GetDetails

`func (o *VerificationServiceVerifyVerdict) GetDetails() map[string]interface{}`

GetDetails returns the Details field if non-nil, zero value otherwise.

### GetDetailsOk

`func (o *VerificationServiceVerifyVerdict) GetDetailsOk() (*map[string]interface{}, bool)`

GetDetailsOk returns a tuple with the Details field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDetails

`func (o *VerificationServiceVerifyVerdict) SetDetails(v map[string]interface{})`

SetDetails sets Details field to given value.

### HasDetails

`func (o *VerificationServiceVerifyVerdict) HasDetails() bool`

HasDetails returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


