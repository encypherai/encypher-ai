# ContentInfo

Content information from verification.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**text_preview** | **str** | First 200 characters of content | 
**leaf_hash** | **str** | Cryptographic hash of full content | 
**leaf_index** | **int** | Position in document | 

## Example

```python
from encypher.models.content_info import ContentInfo

# TODO update the JSON string below
json = "{}"
# create an instance of ContentInfo from a JSON string
content_info_instance = ContentInfo.from_json(json)
# print the JSON string representation of the object
print(ContentInfo.to_json())

# convert the object into a dict
content_info_dict = content_info_instance.to_dict()
# create an instance of ContentInfo from a dict
content_info_from_dict = ContentInfo.from_dict(content_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


