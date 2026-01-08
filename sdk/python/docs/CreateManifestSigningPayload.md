# CreateManifestSigningPayload


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**claim_generator** | **str** |  | 
**actions** | **List[Dict[str, object]]** |  | [optional] 

## Example

```python
from encypher.models.create_manifest_signing_payload import CreateManifestSigningPayload

# TODO update the JSON string below
json = "{}"
# create an instance of CreateManifestSigningPayload from a JSON string
create_manifest_signing_payload_instance = CreateManifestSigningPayload.from_json(json)
# print the JSON string representation of the object
print(CreateManifestSigningPayload.to_json())

# convert the object into a dict
create_manifest_signing_payload_dict = create_manifest_signing_payload_instance.to_dict()
# create an instance of CreateManifestSigningPayload from a dict
create_manifest_signing_payload_from_dict = CreateManifestSigningPayload.from_dict(create_manifest_signing_payload_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


