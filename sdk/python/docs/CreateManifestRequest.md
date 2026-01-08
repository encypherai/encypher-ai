# CreateManifestRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text** | **str** | Plaintext content to derive a manifest for | 
**filename** | **str** |  | [optional] 
**document_title** | **str** |  | [optional] 
**claim_generator** | **str** |  | [optional] 

## Example

```python
from encypher.models.create_manifest_request import CreateManifestRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateManifestRequest from a JSON string
create_manifest_request_instance = CreateManifestRequest.from_json(json)
# print the JSON string representation of the object
print(CreateManifestRequest.to_json())

# convert the object into a dict
create_manifest_request_dict = create_manifest_request_instance.to_dict()
# create an instance of CreateManifestRequest from a dict
create_manifest_request_from_dict = CreateManifestRequest.from_dict(create_manifest_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


