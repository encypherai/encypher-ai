# ValidateManifestRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**manifest** | **Dict[str, object]** | Manifest JSON object | 
**schemas** | **Dict[str, Dict[str, object]]** |  | [optional] 

## Example

```python
from encypher.models.validate_manifest_request import ValidateManifestRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ValidateManifestRequest from a JSON string
validate_manifest_request_instance = ValidateManifestRequest.from_json(json)
# print the JSON string representation of the object
print(ValidateManifestRequest.to_json())

# convert the object into a dict
validate_manifest_request_dict = validate_manifest_request_instance.to_dict()
# create an instance of ValidateManifestRequest from a dict
validate_manifest_request_from_dict = ValidateManifestRequest.from_dict(validate_manifest_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


