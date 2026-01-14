# MultiSourceLookupRequest

Request to look up content across multiple sources.  Patent Reference: FIG. 8 - Multi-Source Hash Table Lookup

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text_segment** | **str** | Text segment to search for | 
**include_all_sources** | **bool** | Return all matching sources (not just first) | [optional] [default to True]
**order_by** | **str** | Ordering: chronological (earliest first), authority, or confidence | [optional] [default to 'chronological']
**include_authority_score** | **bool** | Include authority ranking scores (Enterprise feature) | [optional] [default to False]
**max_results** | **int** | Maximum number of sources to return | [optional] [default to 10]

## Example

```python
from encypher.models.multi_source_lookup_request import MultiSourceLookupRequest

# TODO update the JSON string below
json = "{}"
# create an instance of MultiSourceLookupRequest from a JSON string
multi_source_lookup_request_instance = MultiSourceLookupRequest.from_json(json)
# print the JSON string representation of the object
print(MultiSourceLookupRequest.to_json())

# convert the object into a dict
multi_source_lookup_request_dict = multi_source_lookup_request_instance.to_dict()
# create an instance of MultiSourceLookupRequest from a dict
multi_source_lookup_request_from_dict = MultiSourceLookupRequest.from_dict(multi_source_lookup_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


