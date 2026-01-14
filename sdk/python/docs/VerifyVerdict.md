# VerifyVerdict

Detailed verification verdict data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**valid** | **bool** | Whether the signature is valid | 
**tampered** | **bool** | Whether the payload was tampered | 
**reason_code** | **str** | Reason code describing the verdict | 
**signer_id** | **str** |  | [optional] 
**signer_name** | **str** |  | [optional] 
**timestamp** | **datetime** |  | [optional] 
**details** | **Dict[str, object]** | Structured details (manifest, benchmarking stats, etc.) | [optional] 
**embeddings_found** | **int** | Number of embeddings found in the text | [optional] [default to 0]
**all_embeddings** | [**List[EmbeddingVerdict]**](EmbeddingVerdict.md) |  | [optional] 

## Example

```python
from encypher.models.verify_verdict import VerifyVerdict

# TODO update the JSON string below
json = "{}"
# create an instance of VerifyVerdict from a JSON string
verify_verdict_instance = VerifyVerdict.from_json(json)
# print the JSON string representation of the object
print(VerifyVerdict.to_json())

# convert the object into a dict
verify_verdict_dict = verify_verdict_instance.to_dict()
# create an instance of VerifyVerdict from a dict
verify_verdict_from_dict = VerifyVerdict.from_dict(verify_verdict_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


