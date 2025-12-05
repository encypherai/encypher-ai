# SourceAttributionResponse

Response schema for source attribution.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether search was successful | 
**query_hash** | **str** | Hash of the queried text segment | 
**matches_found** | **int** | Number of matching sources found | 
**sources** | [**List[SourceMatch]**](SourceMatch.md) | List of matching sources | 
**processing_time_ms** | **float** | Processing time in milliseconds | 

## Example

```python
from encypher.models.source_attribution_response import SourceAttributionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SourceAttributionResponse from a JSON string
source_attribution_response_instance = SourceAttributionResponse.from_json(json)
# print the JSON string representation of the object
print(SourceAttributionResponse.to_json())

# convert the object into a dict
source_attribution_response_dict = source_attribution_response_instance.to_dict()
# create an instance of SourceAttributionResponse from a dict
source_attribution_response_from_dict = SourceAttributionResponse.from_dict(source_attribution_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


