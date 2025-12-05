# AppModelsResponseModelsVerifyVerdict

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

## Example

```python
from encypher.models.app_models_response_models_verify_verdict import AppModelsResponseModelsVerifyVerdict

# TODO update the JSON string below
json = "{}"
# create an instance of AppModelsResponseModelsVerifyVerdict from a JSON string
app_models_response_models_verify_verdict_instance = AppModelsResponseModelsVerifyVerdict.from_json(json)
# print the JSON string representation of the object
print(AppModelsResponseModelsVerifyVerdict.to_json())

# convert the object into a dict
app_models_response_models_verify_verdict_dict = app_models_response_models_verify_verdict_instance.to_dict()
# create an instance of AppModelsResponseModelsVerifyVerdict from a dict
app_models_response_models_verify_verdict_from_dict = AppModelsResponseModelsVerifyVerdict.from_dict(app_models_response_models_verify_verdict_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


