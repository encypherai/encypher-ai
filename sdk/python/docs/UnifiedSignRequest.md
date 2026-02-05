# UnifiedSignRequest

Unified sign request supporting single document or batch.  For single document signing: ```json {     \"text\": \"Content to sign...\",     \"document_title\": \"My Article\",     \"options\": {         \"segmentation_level\": \"sentence\"     } } ```  For batch signing (Professional+): ```json {     \"documents\": [         {\"text\": \"First document...\", \"document_title\": \"Doc 1\"},         {\"text\": \"Second document...\", \"document_title\": \"Doc 2\"}     ],     \"options\": {         \"segmentation_level\": \"sentence\"     } } ```

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **str** |  | [optional] 
**document_id** | **str** |  | [optional] 
**document_title** | **str** |  | [optional] 
**document_url** | **str** |  | [optional] 
**metadata** | **Dict[str, object]** |  | [optional] 
**documents** | [**List[SignDocument]**](SignDocument.md) |  | [optional] 
**options** | [**SignOptions**](SignOptions.md) | Signing options - features gated by tier | [optional] 

## Example

```python
from encypher.models.unified_sign_request import UnifiedSignRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UnifiedSignRequest from a JSON string
unified_sign_request_instance = UnifiedSignRequest.from_json(json)
# print the JSON string representation of the object
print(UnifiedSignRequest.to_json())

# convert the object into a dict
unified_sign_request_dict = unified_sign_request_instance.to_dict()
# create an instance of UnifiedSignRequest from a dict
unified_sign_request_from_dict = UnifiedSignRequest.from_dict(unified_sign_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


