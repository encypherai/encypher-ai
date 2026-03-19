# SegmentLocationResponse

Location of a segment within the original document.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**paragraph_index** | **int** | 0-indexed paragraph number |
**sentence_in_paragraph** | **int** | 0-indexed sentence within the paragraph |

## Example

```python
from encypher.models.segment_location_response import SegmentLocationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SegmentLocationResponse from a JSON string
segment_location_response_instance = SegmentLocationResponse.from_json(json)
# print the JSON string representation of the object
print(SegmentLocationResponse.to_json())

# convert the object into a dict
segment_location_response_dict = segment_location_response_instance.to_dict()
# create an instance of SegmentLocationResponse from a dict
segment_location_response_from_dict = SegmentLocationResponse.from_dict(segment_location_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
