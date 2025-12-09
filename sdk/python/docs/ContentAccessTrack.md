# ContentAccessTrack

Schema for tracking content access.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content_id** | **int** |  | 
**access_type** | **str** |  | [optional] 

## Example

```python
from encypher.models.content_access_track import ContentAccessTrack

# TODO update the JSON string below
json = "{}"
# create an instance of ContentAccessTrack from a JSON string
content_access_track_instance = ContentAccessTrack.from_json(json)
# print the JSON string representation of the object
print(ContentAccessTrack.to_json())

# convert the object into a dict
content_access_track_dict = content_access_track_instance.to_dict()
# create an instance of ContentAccessTrack from a dict
content_access_track_from_dict = ContentAccessTrack.from_dict(content_access_track_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


