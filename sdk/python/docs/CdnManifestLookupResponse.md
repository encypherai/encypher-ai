# CdnManifestLookupResponse

Response for GET /cdn/manifests/lookup?url=...

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**record_id** | **str** |  |
**manifest_url** | **str** |  |
**original_url** | **str** |  | [optional]

## Example

```python
from encypher.models.cdn_manifest_lookup_response import CdnManifestLookupResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CdnManifestLookupResponse from a JSON string
cdn_manifest_lookup_response_instance = CdnManifestLookupResponse.from_json(json)
# print the JSON string representation of the object
print(CdnManifestLookupResponse.to_json())

# convert the object into a dict
cdn_manifest_lookup_response_dict = cdn_manifest_lookup_response_instance.to_dict()
# create an instance of CdnManifestLookupResponse from a dict
cdn_manifest_lookup_response_from_dict = CdnManifestLookupResponse.from_dict(cdn_manifest_lookup_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
