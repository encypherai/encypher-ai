# EvidenceGenerateResponse

Response containing the generated evidence package.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether evidence generation succeeded | 
**evidence** | [**EvidencePackage**](EvidencePackage.md) |  | [optional] 
**processing_time_ms** | **float** | Processing time in milliseconds | 
**message** | **str** | Status message | 

## Example

```python
from encypher.models.evidence_generate_response import EvidenceGenerateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of EvidenceGenerateResponse from a JSON string
evidence_generate_response_instance = EvidenceGenerateResponse.from_json(json)
# print the JSON string representation of the object
print(EvidenceGenerateResponse.to_json())

# convert the object into a dict
evidence_generate_response_dict = evidence_generate_response_instance.to_dict()
# create an instance of EvidenceGenerateResponse from a dict
evidence_generate_response_from_dict = EvidenceGenerateResponse.from_dict(evidence_generate_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


