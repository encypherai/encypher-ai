# GhostManualSignRequest

Request body for manually triggering signing of a Ghost post.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**post_type** | **str** | Type of Ghost resource: &#39;post&#39; or &#39;page&#39; | [optional] [default to 'post']

## Example

```python
from encypher.models.ghost_manual_sign_request import GhostManualSignRequest

# TODO update the JSON string below
json = "{}"
# create an instance of GhostManualSignRequest from a JSON string
ghost_manual_sign_request_instance = GhostManualSignRequest.from_json(json)
# print the JSON string representation of the object
print(GhostManualSignRequest.to_json())

# convert the object into a dict
ghost_manual_sign_request_dict = ghost_manual_sign_request_instance.to_dict()
# create an instance of GhostManualSignRequest from a dict
ghost_manual_sign_request_from_dict = GhostManualSignRequest.from_dict(ghost_manual_sign_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
