# EvidenceGenerateRequest

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**TargetText** | **string** | Text content to generate evidence for | 
**DocumentId** | Pointer to **NullableString** |  | [optional] 
**IncludeMerkleProof** | Pointer to **bool** | Include Merkle proof in evidence package | [optional] [default to true]
**IncludeSignatureChain** | Pointer to **bool** | Include full signature verification chain | [optional] [default to true]
**IncludeTimestampProof** | Pointer to **bool** | Include timestamp verification | [optional] [default to true]
**ExportFormat** | Pointer to **string** | Export format: json, pdf, or both | [optional] [default to "json"]

## Methods

### NewEvidenceGenerateRequest

`func NewEvidenceGenerateRequest(targetText string, ) *EvidenceGenerateRequest`

NewEvidenceGenerateRequest instantiates a new EvidenceGenerateRequest object
This constructor will assign default values to properties that have it defined,
and makes sure properties required by API are set, but the set of arguments
will change when the set of required properties is changed

### NewEvidenceGenerateRequestWithDefaults

`func NewEvidenceGenerateRequestWithDefaults() *EvidenceGenerateRequest`

NewEvidenceGenerateRequestWithDefaults instantiates a new EvidenceGenerateRequest object
This constructor will only assign default values to properties that have it defined,
but it doesn't guarantee that properties required by API are set

### GetTargetText

`func (o *EvidenceGenerateRequest) GetTargetText() string`

GetTargetText returns the TargetText field if non-nil, zero value otherwise.

### GetTargetTextOk

`func (o *EvidenceGenerateRequest) GetTargetTextOk() (*string, bool)`

GetTargetTextOk returns a tuple with the TargetText field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetTargetText

`func (o *EvidenceGenerateRequest) SetTargetText(v string)`

SetTargetText sets TargetText field to given value.


### GetDocumentId

`func (o *EvidenceGenerateRequest) GetDocumentId() string`

GetDocumentId returns the DocumentId field if non-nil, zero value otherwise.

### GetDocumentIdOk

`func (o *EvidenceGenerateRequest) GetDocumentIdOk() (*string, bool)`

GetDocumentIdOk returns a tuple with the DocumentId field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetDocumentId

`func (o *EvidenceGenerateRequest) SetDocumentId(v string)`

SetDocumentId sets DocumentId field to given value.

### HasDocumentId

`func (o *EvidenceGenerateRequest) HasDocumentId() bool`

HasDocumentId returns a boolean if a field has been set.

### SetDocumentIdNil

`func (o *EvidenceGenerateRequest) SetDocumentIdNil(b bool)`

 SetDocumentIdNil sets the value for DocumentId to be an explicit nil

### UnsetDocumentId
`func (o *EvidenceGenerateRequest) UnsetDocumentId()`

UnsetDocumentId ensures that no value is present for DocumentId, not even an explicit nil
### GetIncludeMerkleProof

`func (o *EvidenceGenerateRequest) GetIncludeMerkleProof() bool`

GetIncludeMerkleProof returns the IncludeMerkleProof field if non-nil, zero value otherwise.

### GetIncludeMerkleProofOk

`func (o *EvidenceGenerateRequest) GetIncludeMerkleProofOk() (*bool, bool)`

GetIncludeMerkleProofOk returns a tuple with the IncludeMerkleProof field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIncludeMerkleProof

`func (o *EvidenceGenerateRequest) SetIncludeMerkleProof(v bool)`

SetIncludeMerkleProof sets IncludeMerkleProof field to given value.

### HasIncludeMerkleProof

`func (o *EvidenceGenerateRequest) HasIncludeMerkleProof() bool`

HasIncludeMerkleProof returns a boolean if a field has been set.

### GetIncludeSignatureChain

`func (o *EvidenceGenerateRequest) GetIncludeSignatureChain() bool`

GetIncludeSignatureChain returns the IncludeSignatureChain field if non-nil, zero value otherwise.

### GetIncludeSignatureChainOk

`func (o *EvidenceGenerateRequest) GetIncludeSignatureChainOk() (*bool, bool)`

GetIncludeSignatureChainOk returns a tuple with the IncludeSignatureChain field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIncludeSignatureChain

`func (o *EvidenceGenerateRequest) SetIncludeSignatureChain(v bool)`

SetIncludeSignatureChain sets IncludeSignatureChain field to given value.

### HasIncludeSignatureChain

`func (o *EvidenceGenerateRequest) HasIncludeSignatureChain() bool`

HasIncludeSignatureChain returns a boolean if a field has been set.

### GetIncludeTimestampProof

`func (o *EvidenceGenerateRequest) GetIncludeTimestampProof() bool`

GetIncludeTimestampProof returns the IncludeTimestampProof field if non-nil, zero value otherwise.

### GetIncludeTimestampProofOk

`func (o *EvidenceGenerateRequest) GetIncludeTimestampProofOk() (*bool, bool)`

GetIncludeTimestampProofOk returns a tuple with the IncludeTimestampProof field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetIncludeTimestampProof

`func (o *EvidenceGenerateRequest) SetIncludeTimestampProof(v bool)`

SetIncludeTimestampProof sets IncludeTimestampProof field to given value.

### HasIncludeTimestampProof

`func (o *EvidenceGenerateRequest) HasIncludeTimestampProof() bool`

HasIncludeTimestampProof returns a boolean if a field has been set.

### GetExportFormat

`func (o *EvidenceGenerateRequest) GetExportFormat() string`

GetExportFormat returns the ExportFormat field if non-nil, zero value otherwise.

### GetExportFormatOk

`func (o *EvidenceGenerateRequest) GetExportFormatOk() (*string, bool)`

GetExportFormatOk returns a tuple with the ExportFormat field if it's non-nil, zero value otherwise
and a boolean to check if the value has been set.

### SetExportFormat

`func (o *EvidenceGenerateRequest) SetExportFormat(v string)`

SetExportFormat sets ExportFormat field to given value.

### HasExportFormat

`func (o *EvidenceGenerateRequest) HasExportFormat() bool`

HasExportFormat returns a boolean if a field has been set.


[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


