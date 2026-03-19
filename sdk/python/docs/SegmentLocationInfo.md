# SegmentLocationInfo

Location of a segment within the original document.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**paragraph_index** | **int** | 0-indexed paragraph number |
**sentence_in_paragraph** | **int** | 0-indexed sentence within the paragraph |

## Example

```python
from encypher.models.segment_location_info import SegmentLocationInfo

# TODO update the JSON string below
json = "{}"
# create an instance of SegmentLocationInfo from a JSON string
segment_location_info_instance = SegmentLocationInfo.from_json(json)
# print the JSON string representation of the object
print(SegmentLocationInfo.to_json())

# convert the object into a dict
segment_location_info_dict = segment_location_info_instance.to_dict()
# create an instance of SegmentLocationInfo from a dict
segment_location_info_from_dict = SegmentLocationInfo.from_dict(segment_location_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
