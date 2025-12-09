# ExtractAndVerifyResponse

Response from extracting and verifying invisible embedding.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**valid** | **bool** | Whether embedding is valid | 
**verified_at** | **datetime** |  | [optional] 
**content** | [**ContentInfo**](ContentInfo.md) |  | [optional] 
**document** | [**DocumentInfo**](DocumentInfo.md) |  | [optional] 
**merkle_proof** | [**MerkleProofInfo**](MerkleProofInfo.md) |  | [optional] 
**c2pa** | [**C2PAInfo**](C2PAInfo.md) |  | [optional] 
**licensing** | [**LicensingInfo**](LicensingInfo.md) |  | [optional] 
**metadata** | **Dict[str, object]** |  | [optional] 
**error** | **str** |  | [optional] 

## Example

```python
from encypher.models.extract_and_verify_response import ExtractAndVerifyResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ExtractAndVerifyResponse from a JSON string
extract_and_verify_response_instance = ExtractAndVerifyResponse.from_json(json)
# print the JSON string representation of the object
print(ExtractAndVerifyResponse.to_json())

# convert the object into a dict
extract_and_verify_response_dict = extract_and_verify_response_instance.to_dict()
# create an instance of ExtractAndVerifyResponse from a dict
extract_and_verify_response_from_dict = ExtractAndVerifyResponse.from_dict(extract_and_verify_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


