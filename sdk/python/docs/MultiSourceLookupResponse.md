# MultiSourceLookupResponse

Response containing multi-source lookup results.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether lookup succeeded | 
**query_hash** | **str** | Hash of the queried text | 
**total_sources** | **int** | Total number of matching sources | 
**sources** | [**List[SourceRecord]**](SourceRecord.md) | List of matching sources | [optional] 
**original_source** | [**SourceRecord**](SourceRecord.md) |  | [optional] 
**has_chain** | **bool** | Whether sources form a linked chain | 
**chain_length** | **int** | Length of the source chain | [optional] [default to 0]
**processing_time_ms** | **float** | Processing time in milliseconds | 
**message** | **str** | Status message | 

## Example

```python
from encypher.models.multi_source_lookup_response import MultiSourceLookupResponse

# TODO update the JSON string below
json = "{}"
# create an instance of MultiSourceLookupResponse from a JSON string
multi_source_lookup_response_instance = MultiSourceLookupResponse.from_json(json)
# print the JSON string representation of the object
print(MultiSourceLookupResponse.to_json())

# convert the object into a dict
multi_source_lookup_response_dict = multi_source_lookup_response_instance.to_dict()
# create an instance of MultiSourceLookupResponse from a dict
multi_source_lookup_response_from_dict = MultiSourceLookupResponse.from_dict(multi_source_lookup_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


