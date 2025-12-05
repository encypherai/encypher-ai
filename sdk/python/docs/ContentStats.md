# ContentStats

Content corpus statistics.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**period_start** | **str** |  | 
**period_end** | **str** |  | 
**documents_count** | **int** |  | 
**sentences_count** | **int** |  | 
**total_characters** | **int** |  | 
**unique_content_hash_count** | **int** |  | 
**content_categories** | **Dict[str, object]** |  | [optional] 

## Example

```python
from encypher.models.content_stats import ContentStats

# TODO update the JSON string below
json = "{}"
# create an instance of ContentStats from a JSON string
content_stats_instance = ContentStats.from_json(json)
# print the JSON string representation of the object
print(ContentStats.to_json())

# convert the object into a dict
content_stats_dict = content_stats_instance.to_dict()
# create an instance of ContentStats from a dict
content_stats_from_dict = ContentStats.from_dict(content_stats_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


