# EvidenceGenerateRequest

Request to generate an evidence package for content attribution.  Patent Reference: FIG. 11 - Evidence Generation & Attribution Flow

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**target_text** | **str** | Text content to generate evidence for | 
**document_id** | **str** |  | [optional] 
**include_merkle_proof** | **bool** | Include Merkle proof in evidence package | [optional] [default to True]
**include_signature_chain** | **bool** | Include full signature verification chain | [optional] [default to True]
**include_timestamp_proof** | **bool** | Include timestamp verification | [optional] [default to True]
**export_format** | **str** | Export format: json, pdf, or both | [optional] [default to 'json']

## Example

```python
from encypher.models.evidence_generate_request import EvidenceGenerateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of EvidenceGenerateRequest from a JSON string
evidence_generate_request_instance = EvidenceGenerateRequest.from_json(json)
# print the JSON string representation of the object
print(EvidenceGenerateRequest.to_json())

# convert the object into a dict
evidence_generate_request_dict = evidence_generate_request_instance.to_dict()
# create an instance of EvidenceGenerateRequest from a dict
evidence_generate_request_from_dict = EvidenceGenerateRequest.from_dict(evidence_generate_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


