# CreateManifestResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**manifest** | **Dict[str, object]** |  | 
**signing** | [**CreateManifestSigningPayload**](CreateManifestSigningPayload.md) |  | 

## Example

```python
from encypher.models.create_manifest_response import CreateManifestResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateManifestResponse from a JSON string
create_manifest_response_instance = CreateManifestResponse.from_json(json)
# print the JSON string representation of the object
print(CreateManifestResponse.to_json())

# convert the object into a dict
create_manifest_response_dict = create_manifest_response_instance.to_dict()
# create an instance of CreateManifestResponse from a dict
create_manifest_response_from_dict = CreateManifestResponse.from_dict(create_manifest_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


