# ContentListResponse

Schema for listing available content.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content** | [**List[ContentMetadata]**](ContentMetadata.md) |  | 
**total** | **int** |  | 
**quota_remaining** | **int** |  | [optional] 

## Example

```python
from encypher.models.content_list_response import ContentListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ContentListResponse from a JSON string
content_list_response_instance = ContentListResponse.from_json(json)
# print the JSON string representation of the object
print(ContentListResponse.to_json())

# convert the object into a dict
content_list_response_dict = content_list_response_instance.to_dict()
# create an instance of ContentListResponse from a dict
content_list_response_from_dict = ContentListResponse.from_dict(content_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


