# ValidateManifestResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**valid** | **bool** |  | 
**errors** | **List[str]** |  | [optional] 
**warnings** | **List[str]** |  | [optional] 
**assertions** | [**List[C2PAAssertionValidationResult]**](C2PAAssertionValidationResult.md) |  | [optional] 

## Example

```python
from encypher.models.validate_manifest_response import ValidateManifestResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ValidateManifestResponse from a JSON string
validate_manifest_response_instance = ValidateManifestResponse.from_json(json)
# print the JSON string representation of the object
print(ValidateManifestResponse.to_json())

# convert the object into a dict
validate_manifest_response_dict = validate_manifest_response_instance.to_dict()
# create an instance of ValidateManifestResponse from a dict
validate_manifest_response_from_dict = ValidateManifestResponse.from_dict(validate_manifest_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


